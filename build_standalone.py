"""Build a standalone Grey Whale Migration app with PyInstaller.

Run this on the operating system you want to target:
- macOS -> builds a .app bundle
- Windows -> builds an .exe
"""

from __future__ import annotations

import os
from pathlib import Path

from PyInstaller.__main__ import run as pyinstaller_run


PROJECT_ROOT = Path(__file__).resolve().parent
ENTRYPOINT = PROJECT_ROOT / "COLLAB.py"
APP_NAME = "Grey Whale Migration"


def build_args() -> list[str]:
    args = [
        "--clean",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "--distpath",
        str(PROJECT_ROOT / "dist"),
        "--workpath",
        str(PROJECT_ROOT / "build"),
    ]

    for asset in sorted(PROJECT_ROOT.glob("*.png")):
        args.extend(["--add-data", f"{asset}{os.pathsep}."])

    args.append(str(ENTRYPOINT))
    return args


if __name__ == "__main__":
    pyinstaller_run(build_args())
