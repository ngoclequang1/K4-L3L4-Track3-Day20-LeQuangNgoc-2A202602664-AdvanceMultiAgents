"""Extra read-only handoff checks; does not replace the provided tests or freeze verifier."""
import ast
import json
import re
import subprocess
from pathlib import Path

from lab.curator import validate_skill
from lab.tasks import ROOT


def original(relative):
    result = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=ROOT, capture_output=True, text=True, check=True)
    return ast.parse(result.stdout)


def nodes(tree, names):
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            found[node.name] = ast.dump(node, include_attributes=False)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    found[target.id] = ast.dump(node, include_attributes=False)
    return found


def main():
    protected = {
        "src/lab/agent.py": {"PATHS_NOTE", "BASE_PROMPT", "SKILLS_NOTE", "SUBAGENTS_NOTE"},
        "src/lab/runner.py": {"CONDITIONS", "render_trace", "main"},
        "src/lab/curator.py": {"SAFE_NAME", "validate_skill", "parse_skill_blocks"},
    }
    for relative, names in protected.items():
        assert nodes(original(relative), names) == nodes(ast.parse((ROOT / relative).read_text(encoding="utf-8")), names), relative
    result = subprocess.run(
        ["git", "diff", "--exit-code", "HEAD", "--", "tests", "tasks", "scripts", "src/lab/model.py",
         "src/lab/tasks.py", "src/lab/grading.py", "src/lab/testing.py", "src/lab/compare.py"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, "provided files changed"
    skills = list((ROOT / "skills/auto").glob("*/SKILL.md"))
    assert skills, "no generated skill"
    for path in skills:
        assert not validate_skill(path.read_text(encoding="utf-8"), path.parent.name), path
    task_ids = {"code-learn", "data-learn", "logs-learn", "code-eval", "data-eval", "logs-eval"}
    runs = []
    for condition in ("baseline", "subagents", "skills-auto"):
        paths = list((ROOT / "results" / condition).glob("*/run.json"))
        assert {p.parent.name for p in paths} == task_ids, f"incomplete: {condition}"
        for path in paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            assert path.with_name("trace.md").exists(), path
            assert record["total"] > 0 and len(record["checks"]) == record["total"], path
            assert record["passed"] == sum(c["passed"] for c in record["checks"]), path
            assert abs(record["score"] - record["passed"] / record["total"]) < 1e-9, path
            assert not record["skills_modified"], path
            assert record["recursion_limit"] == 40, path
            runs.append(record)
    secret_pattern = re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}")
    for folder in (ROOT / "report", ROOT / "results", ROOT / "skills"):
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json"}:
                assert not secret_pattern.search(path.read_text(encoding="utf-8")), f"possible secret: {path.relative_to(ROOT)}"
    print(f"OK: protected code unchanged, {len(skills)} valid skill(s), {len(runs)} complete official runs, no API key pattern found")


if __name__ == "__main__":
    main()
