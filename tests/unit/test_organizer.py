"""Unit tests for app.organizer.FileOrganizer."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pytest

from app.config import Mode, Settings
from app.organizer import FileOrganizer

DATE_FORMAT = "%Y%m%d"


def _make_settings(mode: Mode, directory: Path, ignore: list[str] | None = None) -> Settings:
    return Settings(
        mode=mode,
        date_format=DATE_FORMAT,
        directories=[directory],
        ignore=ignore or [],
    )


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


def test_today_mode_deletes_empty_folders_instead_of_moving_them(tmp_path: Path) -> None:
    empty_a = tmp_path / "empty_a"
    empty_b = tmp_path / "empty_b"
    empty_a.mkdir()
    empty_b.mkdir()
    non_empty = tmp_path / "has_content"
    non_empty.mkdir()
    (non_empty / "file.txt").write_text("hi", encoding="utf-8")
    file_a = tmp_path / "a.txt"
    _touch_with_mtime(file_a, 2023, 6, 13)

    FileOrganizer(_make_settings(Mode.TODAY, tmp_path)).organize(tmp_path)

    today = datetime.now().strftime(DATE_FORMAT)
    today_dir = tmp_path / today

    assert not empty_a.exists()
    assert not empty_b.exists()
    assert (today_dir / "has_content" / "file.txt").is_file()
    assert (today_dir / "a.txt").is_file()
    assert not (today_dir / "empty_a").exists()
    assert not (today_dir / "empty_b").exists()


def test_today_mode_deletes_empty_target_folder_when_only_empty_dirs_exist(tmp_path: Path) -> None:
    (tmp_path / "empty_a").mkdir()
    (tmp_path / "empty_b").mkdir()

    FileOrganizer(_make_settings(Mode.TODAY, tmp_path)).organize(tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_today_mode_skips_folders_on_ignore_list(tmp_path: Path) -> None:
    keep = tmp_path / "rechnungen_unbearbeitet"
    keep.mkdir()
    (keep / "invoice.pdf").write_text("x", encoding="utf-8")
    other = tmp_path / "other_folder"
    other.mkdir()
    (other / "doc.txt").write_text("x", encoding="utf-8")
    file_a = tmp_path / "a.txt"
    _touch_with_mtime(file_a, 2023, 6, 13)

    settings = _make_settings(Mode.TODAY, tmp_path, ignore=["rechnungen_unbearbeitet"])
    FileOrganizer(settings).organize(tmp_path)

    today = datetime.now().strftime(DATE_FORMAT)
    today_dir = tmp_path / today
    assert keep.is_dir()
    assert (keep / "invoice.pdf").is_file()
    assert (today_dir / "other_folder" / "doc.txt").is_file()
    assert (today_dir / "a.txt").is_file()


def test_today_mode_does_not_delete_empty_folder_on_ignore_list(tmp_path: Path) -> None:
    ignored = tmp_path / "rechnungen_unbearbeitet"
    ignored.mkdir()

    settings = _make_settings(Mode.TODAY, tmp_path, ignore=["rechnungen_unbearbeitet"])
    FileOrganizer(settings).organize(tmp_path)

    assert ignored.is_dir()


def test_ignore_list_is_case_insensitive(tmp_path: Path) -> None:
    keep = tmp_path / "Rechnungen_Unbearbeitet"
    keep.mkdir()
    (keep / "x.txt").write_text("x", encoding="utf-8")
    file_a = tmp_path / "a.txt"
    _touch_with_mtime(file_a, 2023, 6, 13)

    settings = _make_settings(Mode.TODAY, tmp_path, ignore=["rechnungen_unbearbeitet"])
    FileOrganizer(settings).organize(tmp_path)

    assert keep.is_dir()
    assert (keep / "x.txt").is_file()


def test_by_modified_date_skips_files_on_ignore_list(tmp_path: Path) -> None:
    file_keep = tmp_path / "todo.txt"
    file_move = tmp_path / "report.txt"
    _touch_with_mtime(file_keep, 2023, 6, 13)
    _touch_with_mtime(file_move, 2023, 6, 13)

    settings = _make_settings(Mode.BY_MODIFIED_DATE, tmp_path, ignore=["todo.txt"])
    FileOrganizer(settings).organize(tmp_path)

    assert file_keep.is_file()
    assert (tmp_path / "20230613" / "report.txt").is_file()


def test_today_mode_skips_entry_when_move_raises_shutil_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conflict = tmp_path / "Gajim"
    conflict.mkdir()
    (conflict / "data.txt").write_text("x", encoding="utf-8")

    other = tmp_path / "ok_folder"
    other.mkdir()
    (other / "f.txt").write_text("x", encoding="utf-8")

    import shutil

    real_move = shutil.move

    def selective_move(src: str, dst: str, *args: object, **kwargs: object) -> object:
        if Path(src).name == "Gajim":
            raise shutil.Error(f"Destination path '{dst}' already exists")
        return real_move(src, dst)

    monkeypatch.setattr(shutil, "move", selective_move)

    FileOrganizer(_make_settings(Mode.TODAY, tmp_path)).organize(tmp_path)

    today = datetime.now().strftime(DATE_FORMAT)
    today_dir = tmp_path / today
    assert conflict.is_dir()
    assert (conflict / "data.txt").is_file()
    assert (today_dir / "ok_folder" / "f.txt").is_file()


def test_today_mode_skips_empty_folder_when_rmdir_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    blocked = tmp_path / "blocked_empty"
    blocked.mkdir()
    other_empty = tmp_path / "other_empty"
    other_empty.mkdir()
    file_a = tmp_path / "a.txt"
    _touch_with_mtime(file_a, 2023, 6, 13)

    real_rmdir = Path.rmdir

    def selective_rmdir(self: Path) -> None:
        if self.name == "blocked_empty":
            raise PermissionError(32, "in use")
        real_rmdir(self)

    monkeypatch.setattr(Path, "rmdir", selective_rmdir)

    FileOrganizer(_make_settings(Mode.TODAY, tmp_path)).organize(tmp_path)

    today = datetime.now().strftime(DATE_FORMAT)
    assert blocked.is_dir()
    assert not other_empty.exists()
    assert (tmp_path / today / "a.txt").is_file()


def test_by_modified_date_skips_file_when_move_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    locked = tmp_path / "locked.txt"
    movable = tmp_path / "ok.txt"
    _touch_with_mtime(locked, 2023, 6, 13)
    _touch_with_mtime(movable, 2023, 6, 13)

    import shutil

    real_move = shutil.move

    def selective_move(src: str, dst: str, *args: object, **kwargs: object) -> object:
        if Path(src).name == "locked.txt":
            raise PermissionError(32, "in use")
        return real_move(src, dst)

    monkeypatch.setattr(shutil, "move", selective_move)

    FileOrganizer(_make_settings(Mode.BY_MODIFIED_DATE, tmp_path)).organize(tmp_path)

    assert locked.is_file()
    assert (tmp_path / "20230613" / "ok.txt").is_file()
