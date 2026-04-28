"""End-to-end integration tests: load settings.ini and run the organizer."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from app.config import load_settings
from app.main import run

DATE_FORMAT = "%Y%m%d"


def _touch_with_mtime(path: Path, year: int, month: int, day: int) -> None:
    path.write_text("x", encoding="utf-8")
    ts = datetime(year, month, day, 12, 0, 0).timestamp()
    os.utime(path, (ts, ts))


def _write_ini(path: Path, mode: str, work_dir: Path) -> None:
    path.write_text(
        f"[Settings]\n"
        f"mode = {mode}\n"
        f"date_format = %%Y%%m%%d\n"
        f"\n"
        f"[Directories]\n"
        f"base_dir1 = {work_dir}\n",
        encoding="utf-8",
    )


def test_end_to_end_by_modified_date(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    _touch_with_mtime(work / "a.txt", 2023, 6, 13)
    _touch_with_mtime(work / "b.txt", 2023, 6, 14)

    ini = tmp_path / "settings.ini"
    _write_ini(ini, "by_modified_date", work)

    run(load_settings(ini))

    assert (work / "20230613" / "a.txt").is_file()
    assert (work / "20230614" / "b.txt").is_file()


def test_end_to_end_today_mode(tmp_path: Path) -> None:
    work = tmp_path / "work"
    work.mkdir()
    _touch_with_mtime(work / "a.txt", 2023, 6, 13)
    _touch_with_mtime(work / "b.txt", 2023, 6, 14)
    legacy = work / "previous_run"
    legacy.mkdir()
    (legacy / "inner.txt").write_text("hi", encoding="utf-8")

    ini = tmp_path / "settings.ini"
    _write_ini(ini, "today", work)

    run(load_settings(ini))

    today = datetime.now().strftime(DATE_FORMAT)
    today_dir = work / today
    assert today_dir.is_dir()
    assert (today_dir / "a.txt").is_file()
    assert (today_dir / "b.txt").is_file()
    assert (today_dir / "previous_run" / "inner.txt").is_file()
    assert [p.name for p in work.iterdir()] == [today]


def test_end_to_end_skips_missing_directory(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"

    ini = tmp_path / "settings.ini"
    _write_ini(ini, "today", missing)

    run(load_settings(ini))
    assert not missing.exists()
