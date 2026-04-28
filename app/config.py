"""Settings model and loader for the folders-cleanup tool."""

from __future__ import annotations

import configparser
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.constants import (
    DATE_FORMAT_KEY,
    DEFAULT_DATE_FORMAT,
    DIRECTORIES_SECTION,
    MODE_KEY,
    SETTINGS_SECTION,
)


class Mode(StrEnum):
    BY_MODIFIED_DATE = "by_modified_date"
    TODAY = "today"


class Settings(BaseModel):
    mode: Mode = Mode.BY_MODIFIED_DATE
    date_format: str = DEFAULT_DATE_FORMAT
    directories: list[Path] = Field(min_length=1)

    @field_validator("directories", mode="before")
    @classmethod
    def _strip_whitespace(cls, value: object) -> object:
        if isinstance(value, list):
            return [v.strip() if isinstance(v, str) else v for v in value]
        return value


def load_settings(path: Path) -> Settings:
    """Read settings.ini at ``path`` and return a validated :class:`Settings`.

    Raises FileNotFoundError if the file is missing, ValueError if required
    sections are absent, and pydantic ValidationError for invalid values.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Settings file not found: {path}")

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")

    if not parser.has_section(DIRECTORIES_SECTION):
        raise ValueError(f"Missing [{DIRECTORIES_SECTION}] section in {path}")

    raw: dict[str, Any] = {}
    if parser.has_section(SETTINGS_SECTION):
        section = parser[SETTINGS_SECTION]
        if MODE_KEY in section:
            raw[MODE_KEY] = section[MODE_KEY].strip()
        if DATE_FORMAT_KEY in section:
            raw[DATE_FORMAT_KEY] = section[DATE_FORMAT_KEY]

    raw["directories"] = [parser[DIRECTORIES_SECTION][key] for key in parser[DIRECTORIES_SECTION]]

    return Settings(**raw)
