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
from macholib.mach_o import LC_ID_DYLIB, LC_LOAD_DYLIB, LC_LOAD_UPWARD_DYLIB, LC_LOAD_WEAK_DYLIB, LC_PREBOUND_DYLIB, LC_REEXPORT_DYLIB, LC_RPATH
from macholib.util import flipwritable, in_system_path
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


def rewrite_dylib_paths_with_macholib(filename: str, target_rpath: str) -> None:
    """Rewrite Mach-O load commands in place without calling install_name_tool."""
    relocatable = {
        LC_LOAD_DYLIB,
        LC_LOAD_UPWARD_DYLIB,
        LC_LOAD_WEAK_DYLIB,
        LC_PREBOUND_DYLIB,
        LC_REEXPORT_DYLIB,
    }

    binary = MachO(filename)
    changed = False

    for header in binary.headers:
        linked_libs = set()
        dylib_id = None

        for cmd in header.commands:
            lc_type = cmd[0].cmd
            if lc_type not in relocatable and lc_type not in {LC_RPATH, LC_ID_DYLIB}:
                continue

            path = cmd[2].decode("utf-8").rstrip("\x00")
            if lc_type in relocatable:
                linked_libs.add(path)
            elif lc_type == LC_ID_DYLIB:
                dylib_id = path

        def changefunc(path: str) -> str | None:
            if path.startswith("@loader_path/") or path.startswith("@rpath/"):
                return path

            if in_system_path(path):
                return None

            exemptions = (
                "/Library/Frameworks/Tcl.framework/",
                "/Library/Frameworks/Tk.framework/",
            )
            if any(token in path for token in exemptions):
                return None

            return str(Path("@rpath") / Path(path).name)

        if dylib_id is not None:
            # Force the dylib identifier to a relocatable @rpath form.
            changed |= header.rewriteLoadCommands(lambda current: changefunc(current) if current == dylib_id else changefunc(current))

        changed |= header.rewriteLoadCommands(changefunc)

    if not changed:
        return

    old_mode = flipwritable(filename)
    try:
        with open(filename, "rb+") as fh:
            binary.write(fh)
            fh.flush()
    finally:
        flipwritable(filename, old_mode)


py_osx.convert_binary_to_thin_arch = thin_binary_with_macholib
py_osx.set_dylib_dependency_paths = rewrite_dylib_paths_with_macholib


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
