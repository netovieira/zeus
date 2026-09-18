from __future__ import annotations

from unittest.mock import patch

import pytest

from zeus.cli import main, parse_args


def test_parse_args_plan_with_default_path(monkeypatch):
    monkeypatch.setattr("sys.argv", ["zeus.py", "plan", "do the thing"])

    args = parse_args()

    assert args.command == "plan"
    assert args.task == "do the thing"
    assert args.path == "."


def test_parse_args_plan_with_explicit_path(monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["zeus.py", "plan", "do the thing", "/some/project"]
    )

    args = parse_args()

    assert args.path == "/some/project"


def test_main_exits_when_project_dir_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["zeus.py", "plan", "task", str(tmp_path / "nope")]
    )

    with patch("zeus.cli.run_plan") as mock_run_plan:
        with pytest.raises(SystemExit) as exc_info:
            main(tmp_path / "zeus.py")

    assert exc_info.value.code == 1
    mock_run_plan.assert_not_called()


def test_main_exits_when_run_plan_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["zeus.py", "plan", "task", str(tmp_path)])

    with patch("zeus.cli.run_plan", return_value=False):
        with pytest.raises(SystemExit) as exc_info:
            main(tmp_path / "zeus.py")

    assert exc_info.value.code == 1


def test_main_does_not_exit_when_run_plan_succeeds(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["zeus.py", "plan", "task", str(tmp_path)])

    with patch("zeus.cli.run_plan", return_value=True) as mock_run_plan:
        main(tmp_path / "zeus.py")

    mock_run_plan.assert_called_once()


def test_main_exits_when_no_command_given(monkeypatch):
    monkeypatch.setattr("sys.argv", ["zeus.py"])

    with pytest.raises(SystemExit) as exc_info:
        main("zeus.py")

    assert exc_info.value.code == 1
