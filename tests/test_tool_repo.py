from __future__ import annotations

from unittest.mock import MagicMock, patch

from zeus.system.tool_repo import ensure_tool_repo


def _result(returncode=0, stdout=""):
    return MagicMock(returncode=returncode, stdout=stdout)


def test_git_missing_returns_none_without_trying_anything(tmp_path):
    with patch(
        "zeus.system.tool_repo.command_exists", return_value=False
    ), patch("zeus.system.tool_repo.run_command") as mock_run, patch(
        "zeus.system.tool_repo.confirm"
    ) as mock_confirm:
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tmp_path,
        )

    assert result is None
    mock_run.assert_not_called()
    mock_confirm.assert_not_called()


def test_missing_dir_confirmed_clones_and_returns_entry_path(tmp_path):
    tools_root = tmp_path / "tools"

    def fake_clone(command, **kwargs):
        # Simulate "git clone" by creating the entry script on disk.
        repo_dir = tools_root / "athena"
        repo_dir.mkdir(parents=True)
        (repo_dir / "athena.py").write_text("# entry", encoding="utf-8")
        return _result(returncode=0)

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.confirm", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command", side_effect=fake_clone
    ) as mock_run:
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result == tools_root / "athena" / "athena.py"
    called_args = mock_run.call_args.args[0]
    assert called_args[:2] == ["git", "clone"]


def test_missing_dir_declined_returns_none_without_cloning(tmp_path):
    tools_root = tmp_path / "tools"

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.confirm", return_value=False
    ), patch("zeus.system.tool_repo.run_command") as mock_run:
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result is None
    mock_run.assert_not_called()
    assert not tools_root.exists()


def test_clone_failure_returns_none(tmp_path):
    tools_root = tmp_path / "tools"

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.confirm", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command",
        return_value=_result(returncode=1),
    ):
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result is None


def test_existing_dir_same_hash_does_not_pull(tmp_path):
    tools_root = tmp_path / "tools"
    repo_dir = tools_root / "athena"
    repo_dir.mkdir(parents=True)
    (repo_dir / "athena.py").write_text("# entry", encoding="utf-8")

    def fake_run(command, **kwargs):
        if command[:2] == ["git", "-C"] and "rev-parse" in command:
            return _result(returncode=0, stdout="deadbeef\n")
        if command[:2] == ["git", "ls-remote"]:
            return _result(returncode=0, stdout="deadbeef\tHEAD\n")
        raise AssertionError(f"unexpected command: {command}")

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command", side_effect=fake_run
    ) as mock_run, patch(
        "zeus.system.tool_repo.confirm"
    ) as mock_confirm:
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result == repo_dir / "athena.py"
    mock_confirm.assert_not_called()
    for call in mock_run.call_args_list:
        assert "pull" not in call.args[0]


def test_existing_dir_different_hash_confirmed_pulls(tmp_path):
    tools_root = tmp_path / "tools"
    repo_dir = tools_root / "athena"
    repo_dir.mkdir(parents=True)
    (repo_dir / "athena.py").write_text("# entry", encoding="utf-8")

    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if "rev-parse" in command:
            return _result(returncode=0, stdout="local111\n")
        if command[:2] == ["git", "ls-remote"]:
            return _result(returncode=0, stdout="remote222\tHEAD\n")
        if "pull" in command:
            return _result(returncode=0)
        raise AssertionError(f"unexpected command: {command}")

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command", side_effect=fake_run
    ), patch(
        "zeus.system.tool_repo.confirm", return_value=True
    ):
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result == repo_dir / "athena.py"
    assert any("pull" in call for call in calls)


def test_existing_dir_different_hash_declined_does_not_pull(tmp_path):
    tools_root = tmp_path / "tools"
    repo_dir = tools_root / "athena"
    repo_dir.mkdir(parents=True)
    (repo_dir / "athena.py").write_text("# entry", encoding="utf-8")

    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if "rev-parse" in command:
            return _result(returncode=0, stdout="local111\n")
        if command[:2] == ["git", "ls-remote"]:
            return _result(returncode=0, stdout="remote222\tHEAD\n")
        raise AssertionError(f"unexpected command: {command}")

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command", side_effect=fake_run
    ), patch(
        "zeus.system.tool_repo.confirm", return_value=False
    ):
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    # Entry still returned (existing copy is usable) but no pull happened.
    assert result == repo_dir / "athena.py"
    assert not any("pull" in call for call in calls)


def test_pull_failure_still_returns_existing_entry_path(tmp_path):
    tools_root = tmp_path / "tools"
    repo_dir = tools_root / "athena"
    repo_dir.mkdir(parents=True)
    (repo_dir / "athena.py").write_text("# entry", encoding="utf-8")

    def fake_run(command, **kwargs):
        if "rev-parse" in command:
            return _result(returncode=0, stdout="local111\n")
        if command[:2] == ["git", "ls-remote"]:
            return _result(returncode=0, stdout="remote222\tHEAD\n")
        if "pull" in command:
            return _result(returncode=1)
        raise AssertionError(f"unexpected command: {command}")

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command", side_effect=fake_run
    ), patch(
        "zeus.system.tool_repo.confirm", return_value=True
    ):
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result == repo_dir / "athena.py"


def test_local_head_failure_treated_as_unknown_no_pull_attempted(tmp_path):
    tools_root = tmp_path / "tools"
    repo_dir = tools_root / "athena"
    repo_dir.mkdir(parents=True)
    (repo_dir / "athena.py").write_text("# entry", encoding="utf-8")

    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if "rev-parse" in command:
            return _result(returncode=1)
        if command[:2] == ["git", "ls-remote"]:
            return _result(returncode=0, stdout="remote222\tHEAD\n")
        raise AssertionError(f"unexpected command: {command}")

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command", side_effect=fake_run
    ), patch(
        "zeus.system.tool_repo.confirm"
    ) as mock_confirm:
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result == repo_dir / "athena.py"
    mock_confirm.assert_not_called()
    assert not any("pull" in call for call in calls)


def test_remote_head_failure_treated_as_unknown_no_pull_attempted(tmp_path):
    tools_root = tmp_path / "tools"
    repo_dir = tools_root / "athena"
    repo_dir.mkdir(parents=True)
    (repo_dir / "athena.py").write_text("# entry", encoding="utf-8")

    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if "rev-parse" in command:
            return _result(returncode=0, stdout="local111\n")
        if command[:2] == ["git", "ls-remote"]:
            return _result(returncode=1)
        raise AssertionError(f"unexpected command: {command}")

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command", side_effect=fake_run
    ), patch(
        "zeus.system.tool_repo.confirm"
    ) as mock_confirm:
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result == repo_dir / "athena.py"
    mock_confirm.assert_not_called()
    assert not any("pull" in call for call in calls)


def test_existing_dir_missing_entry_script_returns_none(tmp_path):
    tools_root = tmp_path / "tools"
    repo_dir = tools_root / "athena"
    repo_dir.mkdir(parents=True)
    # No athena.py written -> entry_path.is_file() is False.

    def fake_run(command, **kwargs):
        if "rev-parse" in command:
            return _result(returncode=0, stdout="same\n")
        if command[:2] == ["git", "ls-remote"]:
            return _result(returncode=0, stdout="same\tHEAD\n")
        raise AssertionError(f"unexpected command: {command}")

    with patch(
        "zeus.system.tool_repo.command_exists", return_value=True
    ), patch(
        "zeus.system.tool_repo.run_command", side_effect=fake_run
    ):
        result = ensure_tool_repo(
            "athena", "https://example.com/athena.git", "athena.py",
            tools_root=tools_root,
        )

    assert result is None
