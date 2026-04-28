"""File-organizing strategies for the folders-cleanup tool."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path

from app.config import Mode, Settings

log = logging.getLogger(__name__)


class FileOrganizer:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def organize(self, directory: Path) -> None:
        if self._settings.mode is Mode.BY_MODIFIED_DATE:
            self._organize_by_modified_date(directory)
        else:
            self._organize_today(directory)

    def _organize_by_modified_date(self, directory: Path) -> None:
        for entry in directory.iterdir():
            if not entry.is_file():
                continue
            target_dir = directory / self._format_mtime(entry)
            self._move_into(entry, target_dir)

    def _organize_today(self, directory: Path) -> None:
        target_name = datetime.now().strftime(self._settings.date_format)
        target_dir = directory / target_name
        for entry in directory.iterdir():
            if entry == target_dir:
                continue
            self._move_into(entry, target_dir)

    def _format_mtime(self, file_path: Path) -> str:
        mod_time = file_path.stat().st_mtime
        return datetime.fromtimestamp(mod_time).strftime(self._settings.date_format)

    @staticmethod
    def _move_into(entry: Path, target_dir: Path) -> None:
        target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / entry.name
        shutil.move(str(entry), str(destination))
        log.debug("Moved %s -> %s", entry, destination)
