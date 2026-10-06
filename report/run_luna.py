"""Run supplementary Luna tasks with an existing, unmodified generated skill set."""
import argparse
from pathlib import Path

from lab.model import make_model
from lab.runner import run_task
from lab.tasks import list_tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", nargs="+", default=["learn"])
    parser.add_argument("--results", default="results/luna-followup")
    parser.add_argument("--skills", default="report/generated-skills/luna-auto-v2")
    parser.add_argument("--recursion-limit", type=int, default=60)
    args = parser.parse_args()
    model = make_model()
    if getattr(model, "model_name", None) != "gpt-6-luna":
        raise SystemExit("Set LAB_MODEL=openai:gpt-6-luna before running this experiment.")
    skills = Path(args.skills)
    if not list(skills.glob("*/SKILL.md")):
        raise SystemExit("No generated skills found in the selected directory.")
    tasks = [t.id for t in list_tasks(args.tasks[0])] if args.tasks in (["learn"], ["eval"]) else args.tasks
    if args.tasks == ["all"]:
        tasks = [t.id for t in list_tasks()]
    for task in tasks:
        if (Path(args.results) / "skills-auto" / task / "run.json").exists():
            raise SystemExit("Refusing to overwrite a completed run; select a new --results directory.")
    for task in tasks:
        record = run_task(task, "skills-auto", results_dir=args.results, model=model,
                          recursion_limit=args.recursion_limit, skills_source=skills)
        print(f"{task}: {record['passed']}/{record['total']} skills_read={record['skills_read']} "
              f"tokens={record['tokens']['total']} error={record['error']}", flush=True)


if __name__ == "__main__":
    main()
