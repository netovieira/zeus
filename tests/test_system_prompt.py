from __future__ import annotations

from unittest.mock import patch

import pytest

from zeus.system.prompt import confirm


def test_confirm_returns_default_when_not_a_tty():
    with patch("zeus.system.prompt.sys.stdin.isatty", return_value=False):
        assert confirm("Proceed?", default=True) is True
        assert confirm("Proceed?", default=False) is False


@pytest.mark.parametrize("answer", ["y", "yes", "s", "sim", "Y", "SIM"])
def test_confirm_accepts_affirmative_answers(answer):
    with patch("zeus.system.prompt.sys.stdin.isatty", return_value=True), patch(
        "builtins.input", return_value=answer
    ):
        assert confirm("Proceed?", default=False) is True


@pytest.mark.parametrize("answer", ["n", "no", "nao", "whatever"])
def test_confirm_rejects_other_answers(answer):
    with patch("zeus.system.prompt.sys.stdin.isatty", return_value=True), patch(
        "builtins.input", return_value=answer
    ):
        assert confirm("Proceed?", default=True) is False


def test_confirm_empty_answer_returns_default():
    with patch("zeus.system.prompt.sys.stdin.isatty", return_value=True), patch(
        "builtins.input", return_value=""
    ):
        assert confirm("Proceed?", default=True) is True
        assert confirm("Proceed?", default=False) is False


def test_confirm_eof_error_returns_default():
    with patch("zeus.system.prompt.sys.stdin.isatty", return_value=True), patch(
        "builtins.input", side_effect=EOFError
    ):
        assert confirm("Proceed?", default=True) is True


def test_confirm_keyboard_interrupt_returns_default():
    with patch("zeus.system.prompt.sys.stdin.isatty", return_value=True), patch(
        "builtins.input", side_effect=KeyboardInterrupt
    ):
        assert confirm("Proceed?", default=False) is False
