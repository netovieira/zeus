from __future__ import annotations

from zeus.collector import collect_summaries
from zeus.settings import MAX_CONTEXT_CHARS


def make_athena_output(project_root, root_summary="# Root\n\nHello."):
    output_dir = project_root / ".athena"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.md").write_text(root_summary, encoding="utf-8")
    return output_dir


def test_returns_none_without_root_summary(tmp_path):
    assert collect_summaries(tmp_path) is None


def test_returns_root_summary_only_when_no_tree_dir(tmp_path):
    make_athena_output(tmp_path)

    result = collect_summaries(tmp_path)

    assert result is not None
    assert "## Resumo raiz do projeto" in result
    assert "Hello." in result


def test_includes_file_summary_with_relative_path_as_heading(tmp_path):
    output_dir = make_athena_output(tmp_path)
    tree_dir = output_dir / "tree"
    tree_dir.mkdir()
    (tree_dir / "foo.py.md").write_text("Foo summary.", encoding="utf-8")

    result = collect_summaries(tmp_path)

    assert "## foo.py" in result
    assert "Foo summary." in result


def test_dir_summary_maps_to_parent_folder_name(tmp_path):
    output_dir = make_athena_output(tmp_path)
    tree_dir = output_dir / "tree"
    sub_dir = tree_dir / "sub"
    sub_dir.mkdir(parents=True)
    (sub_dir / "_dir_summary.md").write_text("Sub dir summary.", encoding="utf-8")

    result = collect_summaries(tmp_path)

    assert "## sub" in result
    assert "Sub dir summary." in result


def test_root_dir_summary_maps_to_dot(tmp_path):
    output_dir = make_athena_output(tmp_path)
    tree_dir = output_dir / "tree"
    tree_dir.mkdir()
    (tree_dir / "_dir_summary.md").write_text("Root dir summary.", encoding="utf-8")

    result = collect_summaries(tmp_path)

    assert "## ." in result


def test_nested_file_summary_uses_forward_slash_path(tmp_path):
    output_dir = make_athena_output(tmp_path)
    tree_dir = output_dir / "tree" / "sub" / "deeper"
    tree_dir.mkdir(parents=True)
    (tree_dir / "bar.py.md").write_text("Bar summary.", encoding="utf-8")

    result = collect_summaries(tmp_path)

    assert "## sub/deeper/bar.py" in result


def test_truncates_when_over_max_context_chars(tmp_path):
    huge_summary = "x" * (MAX_CONTEXT_CHARS + 1000)
    make_athena_output(tmp_path, root_summary=huge_summary)

    result = collect_summaries(tmp_path)

    assert result is not None
    assert len(result) <= MAX_CONTEXT_CHARS + len(
        "\n\n[TRUNCADO: resumos excederam o limite de contexto]"
    )
    assert result.endswith("[TRUNCADO: resumos excederam o limite de contexto]")


def test_does_not_truncate_when_under_limit(tmp_path):
    make_athena_output(tmp_path, root_summary="short")

    result = collect_summaries(tmp_path)

    assert "TRUNCADO" not in result
