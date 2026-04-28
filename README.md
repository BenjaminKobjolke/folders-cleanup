
# Folders Cleanup

## Overview
The Folders Cleanup script automatically sorts files in specified directories into subfolders named according to date. It supports two modes:

- **by_modified_date** (default): each file is moved into a subfolder named after its modification date.
- **today**: all top-level files **and folders** are bundled into a single subfolder named with today's date.

## Features
- **Multiple Directories:** Can handle multiple directories listed in `settings.ini`.
- **Custom Date Formats:** Customisable date format used for subfolder names.
- **Two Modes:** Per-file modification-date sorting, or today-bundle sorting.
- **Ignore List:** Skip specific files or folders by name (case-insensitive).
- **Empty Folder Cleanup:** In `today` mode, empty top-level folders are deleted instead of moved.
- **Validated Configuration:** Settings are parsed via Pydantic and report clear errors for invalid values.

## Requirements
- Python 3.11 or 3.12
- [uv](https://docs.astral.sh/uv/) for dependency management

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://your-repository-url.com
   cd folders-cleanup
   ```

2. **Install [uv](https://docs.astral.sh/uv/getting-started/installation/)** if you do not have it.

3. **Set up the project:**
   ```bash
   install.bat
   ```
   This runs `uv sync` to create a managed virtual environment, installs all dependencies, and runs the unit tests.

4. **Create your `settings.ini`:**
   - Copy `settings_example.ini` to `settings.ini`.
   - Edit the directories you want to organize and pick a `mode`.

## Configuration

### settings.ini

```ini
[Settings]
; mode controls how files are sorted into subfolders.
;   by_modified_date - one subfolder per file's modification date (default)
;   today            - all files and folders are bundled into one subfolder
;                      named with today's date
mode = by_modified_date
date_format = %%Y%%m%%d
; ignore is a comma-separated list of file or folder names to skip.
; Matching is case-insensitive. Ignored folders are never moved or deleted
; (even if empty). Leave empty to disable.
ignore = archive, _pinned

[Directories]
base_dir1 = Z:\Resilio Sync\Working
base_dir2 = C:\Another\Path
```

- **mode:** `by_modified_date` or `today`. If omitted, `by_modified_date` is used.
- **date_format:** `strftime`-style format for subfolder names. Each `%` must be escaped as `%%` because `configparser` uses `%` for interpolation.
- **ignore:** comma-separated names of files or folders to skip. Matching is
  case-insensitive. Ignored folders are not moved and not deleted (even when
  empty in `today` mode).
- **Directories:** add as many keys as you need under `[Directories]`. Each key (`base_dir1`, `base_dir2`, …) maps to one absolute path.

## Usage

Start the tool:
```bash
start.bat
```

This runs `uv run python -m app.main`, which reads `settings.ini` from the project root and processes every directory listed in `[Directories]`.

### Other batch files

| Script | Purpose |
| --- | --- |
| `install.bat` | First-time setup. Verifies `uv`, runs `uv sync --all-extras`, runs unit tests. |
| `update.bat` | Upgrade dependencies, then run ruff check, ruff format check, mypy and pytest. |
| `tools/run_tests.bat` | Run unit tests only. |
| `tools/run_integration_tests.bat` | Run integration tests only. |

## Examples

### Mode: `by_modified_date`

Before:
```
Working/
├── report.docx          (modified 2024-04-20)
├── presentation.pptx    (modified 2024-04-21)
└── data.csv             (modified 2024-04-22)
```

After (with `date_format = %%Y-%%m-%%d`):
```
Working/
├── 2024-04-20/
│   └── report.docx
├── 2024-04-21/
│   └── presentation.pptx
└── 2024-04-22/
    └── data.csv
```

Existing subfolders inside `Working/` are not touched in this mode — only loose files are moved.

### Mode: `today`

Before (today is 2026-04-28):
```
Working/
├── report.docx          (modified 2024-04-20)
├── presentation.pptx    (modified 2024-04-21)
└── archive/             (an existing folder)
```

After (with `date_format = %%Y-%%m-%%d`):
```
Working/
└── 2026-04-28/
    ├── report.docx
    ├── presentation.pptx
    └── archive/
```

In `today` mode the date of each file is irrelevant — every top-level file **and folder** is moved into one single subfolder named with today's date.

## Date Format Examples

The `date_format` value uses Python `strftime` codes. Each `%` must be doubled in `settings.ini` because `configparser` reserves `%` for interpolation.

| Display format | settings.ini value | Example |
| --- | --- | --- |
| `YYYY-MM-DD` | `%%Y-%%m-%%d` | `2024-04-20` |
| `YYYYMMDD` | `%%Y%%m%%d` | `20240420` |
| `YYMMDD` | `%%y%%m%%d` | `240420` |
| `MMM DD, YYYY` | `%%b %%d, %%Y` | `Apr 20, 2024` |
| `DD-MM-YY` | `%%d-%%m-%%y` | `20-04-24` |
| `YYYY/MM/DD` | `%%Y/%%m/%%d` | `2024/04/20` |

## Project Layout

```
folders-cleanup/
├── app/
│   ├── config.py            # Pydantic Settings + Mode enum + ini loader
│   ├── constants.py         # ini section/key names, defaults
│   ├── logging_setup.py     # logging configuration
│   ├── organizer.py         # FileOrganizer with two strategies
│   └── main.py              # CLI entrypoint
├── tests/
│   ├── unit/
│   └── integration/
├── tools/
│   ├── run_tests.bat
│   └── run_integration_tests.bat
├── pyproject.toml
├── start.bat
├── install.bat
├── update.bat
└── settings_example.ini
```

## License
MIT License

## Contributing
Contributions are welcome. Please fork the repository and submit a pull request with your changes.
