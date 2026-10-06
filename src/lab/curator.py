"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    results_root = Path(results_dir) / source_condition
    destination = Path(out_dir) if out_dir is not None else ROOT / "skills" / "auto"
    runs = []

    if results_root.exists():
        for run_path in sorted(results_root.glob("*/run.json")):
            try:
                run = json.loads(run_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if run.get("role") != "learn":
                continue
            failed = [
                (str(check.get("name", "")), str(check.get("detail", "")))
                for check in run.get("checks", [])
                if not check.get("passed", False)
            ]
            trace_path = run_path.with_name("trace.md")
            trace = trace_path.read_text(encoding="utf-8")[-6000:] if trace_path.exists() else ""
            runs.append({"task": run.get("task", run_path.parent.name), "failed": failed, "trace": trace})

    if not any(run["failed"] for run in runs):
        print("warning: no failed checks in learning tasks")
        return []

    sections = []
    for run in runs:
        if not run["failed"]:
            continue
        failures = "\n".join(f"- {name}: {detail}" for name, detail in run["failed"])
        sections.append(f"TASK: {run['task']}\nFAILED CHECKS:\n{failures}\nTRACE (tail):\n{run['trace']}")
    prompt = f"""You write SKILL files for an engineering and data-analysis agent.
Below are failed checks (including evaluator feedback) and execution traces from learning tasks.
Find general PROCESS failures rather than task-specific answers, and write at most {max_skills} concise skills
that help on NEW tasks of the same kind.

Rules:
- Generalize: do not mention task ids, task-specific input filenames, functions, columns, answers, or numbers.
- Preserve reusable organizational conventions stated in RULE feedback, including required output filenames,
  JSON keys, headers, money units, and test locations. These are conventions, not task-specific input details.
- Keep each convention scoped to its task type. Do not invent broader replacements or requirements.
- Read each new task's specification for accepted error levels, missing-value sentinels, identifier fields,
  categorical spelling, and input format. Never hard-code these input details from the learning examples.
- Preserve exact organizational schema values, ordering rules, metadata fields, and changelog format from
  the RULE feedback, rather than merely saying to follow a schema. Do not lose the stated convention.
- Converting timestamps requires timezone-aware conversion to UTC before formatting, not merely relabeling with Z.
- Prefer three focused skills for code repair, tabular analysis, and log triage, covering both process checks
  and the observed organizational feedback. A skill must not assume extra libraries are installed.
- Each skill must have YAML frontmatter with `name` (lowercase words separated by hyphens) and a one-sentence
  `description` explaining WHEN TO USE IT, followed by at most 40 lines of imperative instructions.
- Prefer a short, verifiable checklist. Do not include evaluation-task material.
- Output exactly this format for each skill:
=== SKILL: <name> ===
---
name: <name>
description: <when to use it>
---
<instructions>
=== END ===

{chr(10).join(sections)}
"""
    response = (model or make_model()).invoke(prompt)
    written = []
    for name, text in parse_skill_blocks(response.content):
        if len(written) >= max_skills:
            break
        if validate_skill(text, expected_name=name):
            continue
        path = destination / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written.append(path)
    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
