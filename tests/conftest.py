from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_home_and_cwd(tmp_path, monkeypatch):
    """Safety net: no test may touch the real HOME or the real cwd.

    Incident this guards against: a test that forgot to isolate HOME wrote
    into the real ~/.zshrc, and a stray cwd let a script run against the
    real thero repo. Every test gets a throwaway HOME/cwd by default; a
    test may still override HOME/USERPROFILE explicitly if it needs a
    specific value, since monkeypatch calls in the test body run after
    this fixture and simply take precedence.
    """
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    monkeypatch.chdir(tmp_path)
