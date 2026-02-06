# Repository Guidelines

## Project Structure & Module Organization
- `main.py` is the app entry point.
- `module/` holds core logic and UI (e.g., `app.py`, `timer_window.py`, `settings_dialog.py`).
- `img/`, `lang/`, `sounds/` store assets copied to `dist/` for packaged builds.
- `settings/` contains default user config (`settings/timer_settings.json`).
- `tools/` has build helpers; `build/` and `dist/` are generated outputs.

## Build, Test, and Development Commands
- Install deps: `uv sync`
- Run locally: `uv run python main.py` (or `Run.bat` on Windows)
- Build exe: `uv sync --dev` then `uv run python -m PyInstaller DesktopTimer.spec --noconfirm`
- Full build script (clean + copy assets + zip): `tools\\pyinstaller.bat`

## Coding Style & Naming Conventions
- Python 3.13; keep modules in `module/` and use `snake_case` filenames.
- Follow existing naming like `settings_dialog.py` and `timer_window.py`.
- Lint/format: Ruff is in dev deps; run `uv run ruff check .` and `uv run ruff format .`.
## Testing Guidelines
- No automated test suite is present. Do a manual smoke run with `uv run python main.py`.
- If you add tests, place them under `tests/` and document how to run them in this file.

## Commit & Pull Request Guidelines
- Commit messages in history use a conventional prefix such as `fix:` or `feat:` with a short summary.
- Example: `feat: add preset search to settings`
- PRs should include a concise description, verification steps, and screenshots for UI changes.
- Link related issues and mention any packaging changes (e.g., asset copy steps).

## Configuration & Packaging Notes
- Runtime settings persist in `settings/timer_settings.json`.
- When packaging, ensure `img/`, `lang/`, and `sounds/` are present next to `dist/DesktopTimer.exe`.
