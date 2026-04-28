# Project Guidelines for Claude Code

This file mirrors the relevant entries from
`D:\GIT\BenjaminKobjolke\claude-code\coding-rules\COMMON_RULES.md` and
`D:\GIT\BenjaminKobjolke\claude-code\coding-rules\PYTHON_RULES.md`. When those rule files
change, update this file too.

---

## Common Rules

### Use Objects for Related Values
Bundle multiple related values (e.g. settings, DTOs) into a dedicated object instead of
passing many parameters.

### Test-Driven Development for Features and Bug Fixes
1. Write tests first
2. Confirm they fail
3. Implement the change
4. Confirm tests now pass

### Integration Tests
Every project must include integration tests in addition to unit tests.

### Test Runner Scripts
- `tools/run_tests.bat` — runs unit tests
- `tools/run_integration_tests.bat` — runs integration tests

### Prefer Type-Safe Values
Use enums, typed DTOs and explicit types over stringly-typed values.

### String Constants
Centralize string constants (see `app/constants.py`).

### README.md is Mandatory
Every project must have a `README.md` covering description, install, usage, dependencies.

### Don't Repeat Yourself (DRY)
Extract shared logic into helpers, classes or constants.

### Confirm Dependency Versions
Before adding a new package, confirm the version with the user.

### Error Handling & Logging Strategy
Centralized error handling. Use the `logging` module — never `print`.

### Input Validation at Boundaries
Validate ini/file/user input at the boundary (Pydantic in this project).

### Maximum File Length — 300 Lines
Split files when they grow beyond ~300 lines.

### Naming Conventions
- Files: `snake_case`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Security Baseline
- Never commit secrets.
- Validate inputs at boundaries.
- Keep dependencies up to date.

### No God Classes
Keep each class focused on a single responsibility.

### Self-Describing Classes
When behavior depends on which fields a class has, expose them through a contract.

---

## Python Rules

### `pyproject.toml` is the Single Source of Truth
- Python version pinned in `pyproject.toml` (`>=3.11,<3.13`).
- Dependencies managed via `uv add ...`.
- Lockfile committed: `uv.lock`.

### Toolchain
```bash
uv add --dev ruff mypy pytest
```
- Ruff handles lint + formatting.
- MyPy handles type checking (configured strict in `pyproject.toml`).
- CI must run: `ruff check`, `ruff format --check`, `mypy`, `pytest`.

### Type Hints on Public APIs
All public functions/classes/methods must have typed parameters and return types.

### Centralized Configuration
Settings live in `app/config.py` (Pydantic). No `os.getenv()` scattered around the code.

### Tests
- pytest for unit tests
- No network in unit tests
- Use tmp dirs / fixtures
- Run tests on every push

### Use `spec=` with MagicMock
When mocking, always use `MagicMock(spec=RealClass)` to validate against the real interface.

### Required Batch Files
- `start.bat` — runs the application
- `tools/run_tests.bat` — runs the test suite
- `tools/run_integration_tests.bat` — runs integration tests

### Structured Logging
Use the `logging` module via `app/logging_setup.py`. Do not use `print()`.

### Validation
Use Pydantic for data validation at the configuration boundary.

---

## Project-Specific Notes

- The CLI entry point is `python -m app.main` (run via `start.bat`).
- `settings.ini` lives in the project root and is gitignored.
- `settings_example.ini` is the committed template; copy it to `settings.ini`
  and edit before running.
- The two `mode` values are `by_modified_date` (default) and `today`. They are defined as
  the `Mode` enum in `app/config.py` — add new values there, never as raw strings.
