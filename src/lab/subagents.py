"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when the task requires inspecting specifications, README files, docstrings, tests, "
                "or input data before any implementation; return verified findings and do not edit files."
            ),
            "system_prompt": (
                "You are a read-only investigator. Read every relevant specification, docstring, test, and sample "
                "before drawing conclusions. Do not modify files. Report concrete findings, edge cases, applicable "
                "rules, and the exact paths you inspected. Clearly distinguish evidence from assumptions. "
                "Perform the assigned work yourself; do not delegate to another agent. Return one final report."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when a non-trivial code, data, or output-file change must be implemented and verified "
                "against the complete task specification."
            ),
            "system_prompt": (
                "You are an implementation specialist. Read the supplied task rules and relevant workspace files, "
                "make only the requested changes, and run the appropriate tests or validation scripts. Fix root "
                "causes rather than symptoms. Report files actually changed and the exact verification results. "
                "Perform the assigned work yourself; do not delegate to another agent. Return one final report."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use after work has been completed when an independent review of requirements, edge cases, "
                "output formats, and test evidence is needed; do not edit files."
            ),
            "system_prompt": (
                "You are an independent read-only reviewer. Compare the current workspace with every supplied "
                "requirement, inspect likely hidden edge cases, and run non-destructive checks where useful. Do not "
                "modify files. Report failures, missing evidence, and a concise pass/fail conclusion. "
                "Perform the assigned work yourself; do not delegate to another agent. Return one final report."
            ),
        },
    ]
