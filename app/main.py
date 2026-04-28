"""CLI entry point for folders-cleanup."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from app.config import Settings, load_settings
from app.constants import SETTINGS_FILE
from app.logging_setup import configure_logging
from app.organizer import FileOrganizer

log = logging.getLogger(__name__)


def run(settings: Settings) -> None:
    organizer = FileOrganizer(settings)
    for directory in settings.directories:
        if not directory.exists():
            log.warning("Directory does not exist: %s", directory)
            continue
        organizer.organize(directory)
        log.info(
            "Organized %s (mode=%s, date_format=%s)",
            directory,
            settings.mode.value,
            settings.date_format,
        )


def main() -> int:
    configure_logging()
    settings_path = Path(SETTINGS_FILE)
    try:
        settings = load_settings(settings_path)
    except FileNotFoundError as exc:
        log.error("%s", exc)
        return 1
    except ValueError as exc:
        log.error("Invalid configuration: %s", exc)
        return 1
    run(settings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
