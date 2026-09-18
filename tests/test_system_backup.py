from __future__ import annotations

from zeus.system.backup import backup_file


def test_backup_file_returns_none_when_source_missing(tmp_path):
    assert backup_file(tmp_path / "missing.txt") is None


def test_backup_file_creates_timestamped_copy(tmp_path):
    source = tmp_path / "config.txt"
    source.write_text("hello", encoding="utf-8")

    backup = backup_file(source)

    assert backup is not None
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "hello"
    assert backup.name.startswith("config.backup_")
    assert backup.suffix == ".txt"


def test_backup_file_uses_custom_prefix(tmp_path):
    source = tmp_path / "config.txt"
    source.write_text("data", encoding="utf-8")

    backup = backup_file(source, prefix="custom")

    assert backup.name.startswith("custom.backup_")


def test_backup_file_content_is_byte_identical(tmp_path):
    source = tmp_path / "bin.dat"
    source.write_bytes(b"\x00\x01\xff")

    backup = backup_file(source)

    assert backup.read_bytes() == b"\x00\x01\xff"
