import os
import sys
from pathlib import Path


def get_base_path() -> str:
    """
    Return the base directory for resources.

    When frozen via PyInstaller it uses the executable directory,
    otherwise it points to the project root (parent of the module folder).
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return str(Path(__file__).resolve().parents[1])
