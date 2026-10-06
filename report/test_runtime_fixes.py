"""Additional regression tests; the provided tests/ directory stays unchanged."""
from langchain_core.messages import AIMessage

from lab.agent import build_agent, make_backend
from lab.runner import run_task
from lab.testing import ScriptedChatModel


def call(name, args):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": "1"}])


def test_workspace_package_is_importable(tmp_path):
    package = tmp_path / "workspace" / "example_package"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("VALUE = 42\n")
    result = make_backend(tmp_path).execute("python -c 'import example_package; print(example_package.VALUE)'")
    assert result.exit_code == 0 and "42" in result.output


def test_syntax_error_has_recovery_advice(tmp_path):
    model = ScriptedChatModel(script=[
        call("execute", {"command": "python -c 'x = 1; with open(\"x\") as f: pass'"}),
        AIMessage(content="done"),
    ])
    result = build_agent(tmp_path, model=model).invoke({"messages": [{"role": "user", "content": "test"}]})
    text = str(next(m for m in result["messages"] if m.type == "tool").content)
    assert "SyntaxError" in text and "write_file" in text and "Do not repeat" in text


def test_failed_edit_requests_current_content(tmp_path):
    (tmp_path / "workspace").mkdir()
    (tmp_path / "workspace" / "file.txt").write_text("current\n")
    model = ScriptedChatModel(script=[
        call("edit_file", {"file_path": "workspace/file.txt", "old_string": "stale", "new_string": "new"}),
        AIMessage(content="done"),
    ])
    result = build_agent(tmp_path, model=model).invoke({"messages": [{"role": "user", "content": "test"}]})
    text = str(next(m for m in result["messages"] if m.type == "tool").content)
    assert "String not found" in text and "CURRENT content" in text
    assert (tmp_path / "workspace/file.txt").read_text() == "current\n"


def test_build_failure_still_produces_record(tmp_path, monkeypatch):
    import lab.runner as runner

    def fail(*args, **kwargs):
        raise RuntimeError("build failure")

    monkeypatch.setattr(runner, "build_agent", fail)
    record = run_task("data-learn", "baseline", results_dir=tmp_path, model=ScriptedChatModel(script=[AIMessage(content="done")]))
    assert "build failure" in record["error"]
    assert record["tokens"]["total"] == 0 and record["total"] == 8
    assert (tmp_path / "baseline/data-learn/run.json").exists()
    assert (tmp_path / "baseline/data-learn/trace.md").exists()


def test_luna_uses_compatible_tool_configuration_without_mutation(tmp_path, monkeypatch):
    import lab.agent as agent_module
    from langchain_openai import ChatOpenAI

    original = ChatOpenAI(model="gpt-6-luna", api_key="test-placeholder", reasoning_effort="medium")
    captured = {}

    def capture(**kwargs):
        captured.update(kwargs)
        return "graph"

    monkeypatch.setattr(agent_module, "create_deep_agent", capture)
    assert build_agent(tmp_path, model=original) == "graph"
    assert captured["model"].reasoning_effort == "none"
    assert captured["model"].use_responses_api is False
    assert captured["model"].temperature is None
    assert original.reasoning_effort == "medium"


def test_alternate_skills_cannot_overwrite_official_experiment(tmp_path):
    import pytest

    with pytest.raises(ValueError, match="separate results"):
        run_task("code-learn", "skills-auto", skills_source=tmp_path)
    with pytest.raises(ValueError, match="skills-auto"):
        run_task("code-learn", "baseline", results_dir=tmp_path, skills_source=tmp_path)


def test_linux_sandbox_original_test_hash_without_editing_repo(tmp_path):
    import os
    import pytest
    from lab.tasks import get_task

    if os.name == "nt":
        pytest.skip("Unix checkout normalization is only applied on Unix runners")
    original = get_task("code-learn").dir / "workspace/tests/test_report.py"
    before = original.read_bytes()
    record = run_task("code-learn", "baseline", results_dir=tmp_path,
                      model=ScriptedChatModel(script=[AIMessage(content="done")]))
    check = next(c for c in record["checks"] if c["name"] == "tests_not_modified")
    assert check["passed"] is True
    assert original.read_bytes() == before
