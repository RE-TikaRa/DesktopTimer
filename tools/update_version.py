#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
from pathlib import Path
import re
import sys


def _replace(path: Path, pattern: str, repl, count: int = 0, flags: int = 0) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n:
        path.write_text(new_text, encoding="utf-8")
    return n


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: update_version.py <version> [--date YYYY-MM-DD]")
        return 1

    raw_version = sys.argv[1].strip()
    version = raw_version[1:] if raw_version.startswith("v") else raw_version
    if not version:
        print("Error: version is empty.")
        return 1

    release_date = date.today().isoformat()
    if len(sys.argv) >= 4 and sys.argv[2] == "--date":
        release_date = sys.argv[3].strip() or release_date

    root = Path(__file__).resolve().parents[1]

    targets = [
        (root / "module" / "constants.py", r'APP_VERSION\s*=\s*"[^"]+"', f'APP_VERSION = "{version}"'),
        (root / "pyproject.toml", r'(?m)^version\s*=\s*"[^"]+"', f'version = "{version}"'),
        (
            root / "setup" / "setup.iss",
            r'(#define\s+MyAppVersion\s+")([^"]+)(")',
            lambda m: f"{m.group(1)}{version}{m.group(3)}",
        ),
        (
            root / "AGENTS.md",
            r'(\*\*DesktopTimer\s+)[0-9A-Za-z\.\-]+',
            lambda m: f"{m.group(1)}{version}",
        ),
        (
            root / "README.md",
            r'(?m)^### v[^\s]+ \(\d{4}-\d{2}-\d{2}\)',
            f"### v{version} ({release_date})",
        ),
        (
            root / "uv.lock",
            r'(name = "desktoptimer"\s*\nversion = ")[^"]+(")',
            lambda m: f"{m.group(1)}{version}{m.group(2)}",
        ),
    ]

    updated = 0
    for path, pattern, repl in targets:
        if not path.exists():
            print(f"[SKIP] {path} (not found)")
            continue
        n = _replace(path, pattern, repl, count=1 if path.name != "uv.lock" else 0, flags=0)
        if n:
            updated += 1
            print(f"[OK] {path.relative_to(root)}")
        else:
            print(f"[WARN] {path.relative_to(root)} (pattern not found)")

    if updated == 0:
        print("No files updated.")
        return 1

    print(f"Version set to {version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
