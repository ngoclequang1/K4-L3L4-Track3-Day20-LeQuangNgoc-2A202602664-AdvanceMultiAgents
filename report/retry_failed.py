"""Retry only official runs with recorded agent errors, once, preserving every first attempt."""
import json
import shutil

from lab.runner import run_task
from lab.tasks import ROOT


def main():
    failed = []
    for condition in ("baseline", "subagents", "skills-auto"):
        for path in sorted((ROOT / "results" / condition).glob("*/run.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            if record.get("error"):
                failed.append((path, record))
    events = []
    for path, record in failed:
        destination = ROOT / "results" / "official-first-pass" / record["condition"] / record["task"]
        if destination.exists():
            raise RuntimeError(f"Refusing to overwrite archived run: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path.parent), str(destination))
        result = run_task(record["task"], record["condition"], ROOT / "results", recursion_limit=40)
        events.append({
            "condition": record["condition"], "task": record["task"],
            "first_attempt": str(destination.relative_to(ROOT)),
            "first_error": record["error"], "retry_error": result["error"],
            "first_score": record["score"], "retry_score": result["score"],
        })
        (ROOT / "results" / "retry-log.json").write_text(
            json.dumps(events, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
        )
        error = result["error"].splitlines()[0] if result["error"] else "none"
        print(f"retry {record['condition']}/{record['task']}: {result['passed']}/{result['total']} "
              f"tokens={result['tokens']['total']} error={error}", flush=True)


if __name__ == "__main__":
    main()
