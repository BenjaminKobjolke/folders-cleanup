"""Unit tests for app.organizer.FileOrganizer."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from app.config import Mode, Settings
from app.organizer import FileOrganizer

DATE_FORMAT = "%Y%m%d"


def _make_settings(mode: Mode, directory: Path) -> Settings:
    return Settings(mode=mode, date_format=DATE_FORMAT, directories=[directory])


def _touch_with_mtime(path: Path, year: int, month: int, day: int) -> None:
    path.write_text("x", encoding="utf-8")
    ts = datetime(year, month, day, 12, 0, 0).timestamp()
    os.utime(path, (ts, ts))


def test_by_modified_date_groups_files_into_per_date_subfolders(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    c = tmp_path / "c.txt"
    _touch_with_mtime(a, 2023, 6, 13)
    _touch_with_mtime(b, 2023, 6, 13)
    _touch_with_mtime(c, 2023, 6, 14)

    FileOrganizer(_make_settings(Mode.BY_MODIFIED_DATE, tmp_path)).organize(tmp_path)

    assert (tmp_path / "20230613" / "a.txt").is_file()
    assert (tmp_path / "20230613" / "b.txt").is_file()
    assert (tmp_path / "20230614" / "c.txt").is_file()


def test_by_modified_date_does_not_touch_existing_subfolders(tmp_path: Path) -> None:
    keep_dir = tmp_path / "keep_me"
    keep_dir.mkdir()
    (keep_dir / "inner.txt").write_text("keep", encoding="utf-8")
    file_a = tmp_path / "a.txt"
    _touch_with_mtime(file_a, 2024, 1, 5)

    FileOrganizer(_make_settings(Mode.BY_MODIFIED_DATE, tmp_path)).organize(tmp_path)

    assert keep_dir.is_dir()
    assert (keep_dir / "inner.txt").is_file()
    assert (tmp_path / "20240105" / "a.txt").is_file()


def test_today_mode_bundles_files_and_folders_into_single_today_folder(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    _touch_with_mtime(a, 2023, 6, 13)
    _touch_with_mtime(b, 2023, 6, 14)
    sub = tmp_path / "old_folder"
    sub.mkdir()
    (sub / "inner.txt").write_text("hi", encoding="utf-8")

    FileOrganizer(_make_settings(Mode.TODAY, tmp_path)).organize(tmp_path)

    today = datetime.now().strftime(DATE_FORMAT)
    today_dir = tmp_path / today

    assert today_dir.is_dir()
    assert (today_dir / "a.txt").is_file()
    assert (today_dir / "b.txt").is_file()
    assert (today_dir / "old_folder" / "inner.txt").is_file()
    siblings = [p.name for p in tmp_path.iterdir()]
    assert siblings == [today]


def test_today_mode_is_idempotent(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    _touch_with_mtime(a, 2023, 6, 13)
    organizer = FileOrganizer(_make_settings(Mode.TODAY, tmp_path))

    organizer.organize(tmp_path)
    organizer.organize(tmp_path)

    today = datetime.now().strftime(DATE_FORMAT)
    today_dir = tmp_path / today

    assert today_dir.is_dir()
    assert (today_dir / "a.txt").is_file()
    assert not (today_dir / today).exists()


def test_today_mode_skips_when_directory_is_empty(tmp_path: Path) -> None:
    FileOrganizer(_make_settings(Mode.TODAY, tmp_path)).organize(tmp_path)

    assert list(tmp_path.iterdir()) == []
