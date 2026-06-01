"""Build a standalone Grey Whale Migration app with PyInstaller.

Run this on the operating system you want to target:
- macOS -> builds a .app bundle
- Windows -> builds an .exe
"""

from __future__ import annotations

import os
import sys
import tempfile
import stat
from pathlib import Path

from PyInstaller.__main__ import run as pyinstaller_run
from macholib.MachO import MachO
import PyInstaller.utils.osx as py_osx


PROJECT_ROOT = Path(__file__).resolve().parent
ENTRYPOINT = PROJECT_ROOT / "COLLAB.py"
APP_NAME = "Grey Whale Migration"
PYINSTALLER_CACHE = Path(tempfile.gettempdir()) / "pyinstaller-cache"

os.environ.setdefault("PYINSTALLER_CONFIG_DIR", str(PYINSTALLER_CACHE))


def thin_binary_with_macholib(filename: str, thin_arch: str, output_filename: str | None = None) -> None:
    """Replace lipo with a pure-Python slice extractor for fat Mach-O binaries."""
    output_filename = output_filename or filename
    executable = MachO(filename)
    for header in executable.headers:
        if py_osx._get_arch_string(header.header) == thin_arch:
            with open(filename, "rb") as source:
                source.seek(header.offset)
                payload = source.read(header.size)
            with open(output_filename, "wb") as target:
                target.write(payload)
            os.chmod(output_filename, stat.S_IMODE(os.stat(filename).st_mode))
            return
    raise RuntimeError(f"{filename} does not contain a {thin_arch} slice")


py_osx.convert_binary_to_thin_arch = thin_binary_with_macholib


def build_args() -> list[str]:
    args = [
        "--clean",
        "--noconfirm",
        "--windowed",
        "--name",
        APP_NAME,
        "--distpath",
        str(PROJECT_ROOT / "dist"),
        "--workpath",
        str(PROJECT_ROOT / "build"),
    ]

    if sys.platform == "darwin":
        # macOS .app bundles are delivered as directories, so build an onedir app bundle.
        args.extend(["--onedir", "--target-arch", "arm64"])
    else:
        args.append("--onefile")

    for asset in sorted(PROJECT_ROOT.glob("*.png")):
        args.extend(["--add-data", f"{asset}{os.pathsep}."])

    args.append(str(ENTRYPOINT))
    return args


if __name__ == "__main__":
    pyinstaller_run(build_args())
