from __future__ import annotations

from zeus.prompts import PLAN_PROMPT


def test_plan_prompt_formats_without_keyerror():
    result = PLAN_PROMPT.format(task="do the thing", summaries="some summary text")

    assert "do the thing" in result
    assert "some summary text" in result
