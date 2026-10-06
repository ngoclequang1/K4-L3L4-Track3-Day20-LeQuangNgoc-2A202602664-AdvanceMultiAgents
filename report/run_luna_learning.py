"""Supplementary Luna learning experiment; never overwrites frozen results/skills."""
from pathlib import Path
import argparse

from lab.curator import curate_skills, validate_skill
from lab.runner import run_task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills", default="report/generated-skills/luna-auto")
    parser.add_argument("--results", default="results/luna-learning-v4")
    parser.add_argument("--recursion-limit", type=int, default=40)
    args = parser.parse_args()
    skills = Path(args.skills)
    if skills.exists():
        raise SystemExit("Refusing to overwrite existing Luna skills; use a new experiment directory.")
    paths = curate_skills(out_dir=skills)
    if not paths:
        raise SystemExit("Curator produced no valid skills; do not run a skill experiment.")
    for path in paths:
        assert not validate_skill(path.read_text(encoding="utf-8"), path.parent.name)
        print(f"curator: {path}", flush=True)
    for task in ("code-learn", "data-learn", "logs-learn"):
        record = run_task(task, "skills-auto", results_dir=args.results, recursion_limit=args.recursion_limit,
                          skills_source=skills)
        print(f"{task}: {record['passed']}/{record['total']} skills_read={record['skills_read']} "
              f"tokens={record['tokens']['total']} error={record['error']}", flush=True)


if __name__ == "__main__":
    main()
