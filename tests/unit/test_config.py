"""Unit tests for app.config."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config import Mode, Settings, load_settings


def _write_ini(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_load_settings_with_mode_and_date_format(tmp_path: Path) -> None:
    ini = tmp_path / "settings.ini"
    _write_ini(
        ini,
        "[Settings]\n"
        "mode = today\n"
        "date_format = %%Y-%%m-%%d\n"
        "\n"
        "[Directories]\n"
        f"base_dir1 = {tmp_path / 'work'}\n",
    )

    settings = load_settings(ini)

    assert settings.mode is Mode.TODAY
    assert settings.date_format == "%Y-%m-%d"
    assert settings.directories == [tmp_path / "work"]


def test_load_settings_defaults_mode_when_missing(tmp_path: Path) -> None:
    ini = tmp_path / "settings.ini"
    _write_ini(
        ini,
        f"[Settings]\ndate_format = %%Y%%m%%d\n\n[Directories]\nbase_dir1 = {tmp_path / 'work'}\n",
    )

    settings = load_settings(ini)

    assert settings.mode is Mode.BY_MODIFIED_DATE


def test_load_settings_invalid_mode_raises(tmp_path: Path) -> None:
    ini = tmp_path / "settings.ini"
    _write_ini(
        ini,
        f"[Settings]\nmode = nonsense\n\n[Directories]\nbase_dir1 = {tmp_path / 'work'}\n",
    )

    with pytest.raises(ValidationError):
        load_settings(ini)


def test_load_settings_missing_directories_section_raises(tmp_path: Path) -> None:
    ini = tmp_path / "settings.ini"
    _write_ini(ini, "[Settings]\nmode = today\n")

    with pytest.raises(ValueError, match="Directories"):
        load_settings(ini)


def test_load_settings_empty_directories_raises(tmp_path: Path) -> None:
    ini = tmp_path / "settings.ini"
    _write_ini(ini, "[Settings]\nmode = today\n\n[Directories]\n")

    with pytest.raises(ValidationError):
        load_settings(ini)


def test_load_settings_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_settings(tmp_path / "does_not_exist.ini")


def test_settings_model_defaults() -> None:
    settings = Settings(directories=[Path("c:/work")])

    assert settings.mode is Mode.BY_MODIFIED_DATE
    assert settings.date_format == "%Y_%m_%d"
