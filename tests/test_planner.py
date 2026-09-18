from __future__ import annotations

from unittest.mock import patch

import pytest

from zeus.planner import run_plan, validate_plan
from zeus.settings import ZEUS_PLAN_DIRNAME, ZEUS_PLAN_FILENAME


def test_validate_plan_rejects_too_short():
    assert validate_plan("short") is False


def test_validate_plan_rejects_markdown_fence():
    assert validate_plan("```\n" + "x" * 300) is False


def test_validate_plan_accepts_normal_content():
    assert validate_plan("# Plan\n\n" + "x" * 300) is True


def test_run_plan_aborts_when_athena_index_fails(tmp_path):
    with patch(
        "zeus.planner.run_athena_index", return_value=False
    ), patch("zeus.planner.call_claude") as mock_claude:
        result = run_plan("task", tmp_path, tmp_path / "zeus.py")

    assert result is False
    mock_claude.assert_not_called()


def test_run_plan_errors_when_no_summaries_found(tmp_path):
    with patch(
        "zeus.planner.run_athena_index", return_value=True
    ), patch(
        "zeus.planner.collect_summaries", return_value=None
    ), patch("zeus.planner.call_claude") as mock_claude:
        result = run_plan("task", tmp_path, tmp_path / "zeus.py")

    assert result is False
    mock_claude.assert_not_called()


def test_run_plan_claude_failure_writes_nothing(tmp_path):
    with patch(
        "zeus.planner.run_athena_index", return_value=True
    ), patch(
        "zeus.planner.collect_summaries", return_value="some summaries"
    ), patch("zeus.planner.call_claude", return_value=None):
        result = run_plan("task", tmp_path, tmp_path / "zeus.py")

    assert result is False
    assert not (tmp_path / ZEUS_PLAN_DIRNAME).exists()


def test_run_plan_validation_failure_writes_nothing(tmp_path):
    with patch(
        "zeus.planner.run_athena_index", return_value=True
    ), patch(
        "zeus.planner.collect_summaries", return_value="some summaries"
    ), patch("zeus.planner.call_claude", return_value="too short"):
        result = run_plan("task", tmp_path, tmp_path / "zeus.py")

    assert result is False
    assert not (tmp_path / ZEUS_PLAN_DIRNAME).exists()


def test_run_plan_success_writes_plan_file(tmp_path):
    plan_content = "# Plan\n\n" + "x" * 300

    with patch(
        "zeus.planner.run_athena_index", return_value=True
    ), patch(
        "zeus.planner.collect_summaries", return_value="some summaries"
    ), patch("zeus.planner.call_claude", return_value=plan_content):
        result = run_plan("task", tmp_path, tmp_path / "zeus.py")

    assert result is True
    plan_path = tmp_path / ZEUS_PLAN_DIRNAME / ZEUS_PLAN_FILENAME
    assert plan_path.exists()
    assert plan_path.read_text(encoding="utf-8") == plan_content.strip() + "\n"


def test_run_plan_write_failure_cleans_up_temp_file_and_returns_false(tmp_path):
    plan_content = "# Plan\n\n" + "x" * 300

    with patch(
        "zeus.planner.run_athena_index", return_value=True
    ), patch(
        "zeus.planner.collect_summaries", return_value="some summaries"
    ), patch(
        "zeus.planner.call_claude", return_value=plan_content
    ), patch(
        "zeus.planner.os.replace", side_effect=OSError("disk full")
    ):
        result = run_plan("task", tmp_path, tmp_path / "zeus.py")

    assert result is False
    plan_dir = tmp_path / ZEUS_PLAN_DIRNAME
    leftover_temp_files = list(plan_dir.glob(".zeus-plan.md.tmp_*"))
    assert leftover_temp_files == []


def test_run_plan_backs_up_existing_plan(tmp_path):
    plan_dir = tmp_path / ZEUS_PLAN_DIRNAME
    plan_dir.mkdir(parents=True)
    plan_path = plan_dir / ZEUS_PLAN_FILENAME
    plan_path.write_text("old plan", encoding="utf-8")

    plan_content = "# Plan\n\n" + "x" * 300

    with patch(
        "zeus.planner.run_athena_index", return_value=True
    ), patch(
        "zeus.planner.collect_summaries", return_value="some summaries"
    ), patch("zeus.planner.call_claude", return_value=plan_content):
        result = run_plan("task", tmp_path, tmp_path / "zeus.py")

    assert result is True
    backups = list(plan_dir.glob("zeus-plan.backup_*.md"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "old plan"
