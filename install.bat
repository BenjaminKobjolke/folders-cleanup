@echo off
where uv >nul 2>nul
if errorlevel 1 (
    echo uv is not installed or not on PATH.
    echo Install it from https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)

uv sync --all-extras
if errorlevel 1 exit /b 1

uv run pytest tests/unit -v
