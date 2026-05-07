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
        self._ignored_names: frozenset[str] = frozenset(name.casefold() for name in settings.ignore)

    def organize(self, directory: Path) -> None:
        if self._settings.mode is Mode.BY_MODIFIED_DATE:
            self._organize_by_modified_date(directory)
        else:
            self._organize_today(directory)

    def _organize_by_modified_date(self, directory: Path) -> None:
        for entry in directory.iterdir():
            if self._is_ignored(entry):
                log.debug("Ignoring %s", entry)
                continue
            if not entry.is_file():
                continue
            target_dir = directory / self._format_mtime(entry)
            try:
                self._move_into(entry, target_dir)
            except OSError as exc:
                log.warning("Could not move %s: %s", entry, exc)

    def _organize_today(self, directory: Path) -> None:
        target_name = datetime.now().strftime(self._settings.date_format)
        target_dir = directory / target_name
        for entry in directory.iterdir():
            if entry == target_dir:
                continue
            if self._is_ignored(entry):
                log.debug("Ignoring %s", entry)
                continue
            if self._is_date_folder(entry):
                log.debug("Skipping existing date folder %s", entry)
                continue
            if self._is_empty_dir(entry):
                try:
                    entry.rmdir()
                    log.debug("Removed empty folder %s", entry)
                except OSError as exc:
                    log.warning("Could not remove empty folder %s: %s", entry, exc)
                continue
            try:
                self._move_into(entry, target_dir)
            except OSError as exc:
                log.warning("Could not move %s: %s", entry, exc)

    def _is_ignored(self, entry: Path) -> bool:
        return entry.name.casefold() in self._ignored_names

    def _is_date_folder(self, entry: Path) -> bool:
        if not entry.is_dir():
            return False
        try:
            datetime.strptime(entry.name, self._settings.date_format)
        except ValueError:
            return False
        return True

    @staticmethod
    def _is_empty_dir(entry: Path) -> bool:
        return entry.is_dir() and not any(entry.iterdir())

    def _format_mtime(self, file_path: Path) -> str:
        mod_time = file_path.stat().st_mtime
        return datetime.fromtimestamp(mod_time).strftime(self._settings.date_format)

    @staticmethod
    def _move_into(entry: Path, target_dir: Path) -> None:
        target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / entry.name
        shutil.move(str(entry), str(destination))
        log.debug("Moved %s -> %s", entry, destination)
