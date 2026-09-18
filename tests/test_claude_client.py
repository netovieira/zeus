from __future__ import annotations

from unittest.mock import patch, MagicMock

from zeus.claude_client import call_claude


def test_call_claude_returns_none_when_claude_missing():
    with patch(
        "zeus.claude_client.command_exists", return_value=False
    ), patch("zeus.claude_client.run_command") as mock_run:
        result = call_claude("prompt")

    assert result is None
    mock_run.assert_not_called()


def test_call_claude_returns_none_on_nonzero_returncode():
    fake_result = MagicMock(returncode=1, stdout="", stderr="boom")
    with patch(
        "zeus.claude_client.command_exists", return_value=True
    ), patch("zeus.claude_client.run_command", return_value=fake_result):
        result = call_claude("prompt")

    assert result is None


def test_call_claude_returns_none_on_empty_stdout():
    fake_result = MagicMock(returncode=0, stdout="   ", stderr="")
    with patch(
        "zeus.claude_client.command_exists", return_value=True
    ), patch("zeus.claude_client.run_command", return_value=fake_result):
        result = call_claude("prompt")

    assert result is None


def test_call_claude_returns_stripped_stdout_on_success():
    fake_result = MagicMock(returncode=0, stdout="  hello world  \n", stderr="")
    with patch(
        "zeus.claude_client.command_exists", return_value=True
    ), patch(
        "zeus.claude_client.run_command", return_value=fake_result
    ) as mock_run:
        result = call_claude("my prompt", cwd="/proj")

    assert result == "hello world"
    mock_run.assert_called_once_with(
        ["claude", "-p"], capture=True, cwd="/proj", input_text="my prompt"
    )
