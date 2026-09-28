import os
from pathlib import Path
import shutil


def bash_executable():
    if os.name == "nt":
        # Avoid selecting the unrelated WSL bash launcher from System32.
        git = shutil.which("git")
        if git:
            bundled = Path(git).parent.parent / "bin" / "bash.exe"
            if bundled.is_file():
                return str(bundled)
    return shutil.which("bash") or "bash"


def symlink_or_skip(test, link, target):
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as error:
        if os.name == "nt" and getattr(error, "winerror", None) == 1314:
            test.skipTest("Windows account cannot create symlinks")
        raise
