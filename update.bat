@echo off
uv lock --upgrade
if errorlevel 1 exit /b 1

uv sync
if errorlevel 1 exit /b 1

uv run ruff check .
if errorlevel 1 exit /b 1

uv run ruff format --check .
if errorlevel 1 exit /b 1

uv run mypy app
if errorlevel 1 exit /b 1

uv run pytest
