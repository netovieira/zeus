from __future__ import annotations

from unittest.mock import MagicMock, patch

from zeus.athena_bridge import find_athena_script, run_athena_index
from zeus.settings import ATHENA_PATH_ENV_VAR


def test_env_var_takes_priority_when_file_exists(tmp_path, monkeypatch):
    athena_script = tmp_path / "custom" / "athena.py"
    athena_script.parent.mkdir(parents=True)
    athena_script.write_text("# entry", encoding="utf-8")
    monkeypatch.setenv(ATHENA_PATH_ENV_VAR, str(athena_script))

    result = find_athena_script(tmp_path / "zeus" / "zeus.py")

    assert result == athena_script


def test_env_var_pointing_to_missing_file_returns_none(tmp_path, monkeypatch):
    monkeypatch.setenv(ATHENA_PATH_ENV_VAR, str(tmp_path / "nope.py"))

    result = find_athena_script(tmp_path / "zeus" / "zeus.py")

    assert result is None


def test_falls_back_to_sibling_folder(tmp_path, monkeypatch):
    monkeypatch.delenv(ATHENA_PATH_ENV_VAR, raising=False)
    root = tmp_path / "myscripts"
    (root / "athena").mkdir(parents=True)
    athena_script = root / "athena" / "athena.py"
    athena_script.write_text("# entry", encoding="utf-8")
    entry_path = root / "zeus" / "zeus.py"
    entry_path.parent.mkdir(parents=True)

    result = find_athena_script(entry_path)

    assert result == athena_script


def test_falls_back_to_ensure_tool_repo_when_no_sibling(tmp_path, monkeypatch):
    monkeypatch.delenv(ATHENA_PATH_ENV_VAR, raising=False)
    entry_path = tmp_path / "zeus" / "zeus.py"
    entry_path.parent.mkdir(parents=True)

    with patch(
        "zeus.athena_bridge.ensure_tool_repo",
        return_value=tmp_path / "managed" / "athena.py",
    ) as mock_ensure:
        result = find_athena_script(entry_path)

    assert result == tmp_path / "managed" / "athena.py"
    mock_ensure.assert_called_once()


def test_run_athena_index_returns_false_when_script_not_found(tmp_path):
    with patch(
        "zeus.athena_bridge.find_athena_script", return_value=None
    ), patch("zeus.athena_bridge.run_command") as mock_run:
        result = run_athena_index(tmp_path / "zeus.py", tmp_path / "project")

    assert result is False
    mock_run.assert_not_called()


def test_run_athena_index_builds_correct_command(tmp_path):
    athena_script = tmp_path / "athena.py"
    project_root = tmp_path / "project"

    with patch(
        "zeus.athena_bridge.find_athena_script", return_value=athena_script
    ), patch(
        "zeus.athena_bridge.run_command",
        return_value=MagicMock(returncode=0),
    ) as mock_run:
        result = run_athena_index(tmp_path / "zeus.py", project_root)

    assert result is True
    called_command = mock_run.call_args.args[0]
    assert called_command == [
        "python", str(athena_script), "index", str(project_root),
    ]


def test_run_athena_index_propagates_failure_returncode(tmp_path):
    with patch(
        "zeus.athena_bridge.find_athena_script",
        return_value=tmp_path / "athena.py",
    ), patch(
        "zeus.athena_bridge.run_command",
        return_value=MagicMock(returncode=1),
    ):
        result = run_athena_index(tmp_path / "zeus.py", tmp_path / "project")

    assert result is False
