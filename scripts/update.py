#!/usr/bin/env python3
"""Update a copied skill only when it matches a known Git revision. Python 3.9+."""
import argparse
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

NAME = "design-patterns-refactor"
PACKAGE = Path("skills") / NAME
IGNORED = {"target", "__pycache__", ".DS_Store"}
ROOT = Path(__file__).resolve().parents[1]


def pending_path(destination):
    return destination / ("." + NAME + ".update.json")


def exists(path):
    return path.exists() or path.is_symlink()


def backup_parent_for(destination):
    parent = destination.parent / "skill-backups"
    if parent.is_symlink() or parent.resolve().is_relative_to(destination):
        raise ValueError("Backup location must be a real directory outside skill scanning.")
    return parent


@contextmanager
def installation_lock(destination):
    """The OS releases this lock on process exit; never unlink its shared inode."""
    path = destination / ("." + NAME + ".update.lock")
    if path.is_symlink():
        raise ValueError(f"Refusing a symlink lock: {path}")
    fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        if os.name == "nt":
            import msvcrt

            def lock(mode):
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, mode, 1)

            acquire = lambda: lock(msvcrt.LK_NBLCK)
            release = lambda: lock(msvcrt.LK_UNLCK)
        else:
            import fcntl
            acquire = lambda: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            release = lambda: fcntl.flock(fd, fcntl.LOCK_UN)
        try:
            acquire()
        except OSError as error:
            raise FileExistsError(f"Another update or recovery is running: {destination}") from error
        try:
            yield
        finally:
            release()
    finally:
        os.close(fd)


def write_pending(destination, backup_dir, installed, current):
    record = {"version": 1, "destination": str(destination), "backup_dir": backup_dir.name,
              "installed": installed, "current": current}
    fd, temporary = tempfile.mkstemp(prefix="." + NAME + ".journal-", dir=destination)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(record, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, pending_path(destination))
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def recover_pending(destination):
    """Called with the installation lock held. Never replace an existing target."""
    journal = pending_path(destination)
    if not exists(journal):
        print("No interrupted update to recover.")
        return
    if journal.is_symlink():
        raise ValueError(f"Refusing a symlink journal: {journal}")
    record = json.loads(journal.read_text(encoding="utf-8"))
    if (not isinstance(record, dict) or record.get("version") != 1
            or record.get("destination") != str(destination)):
        raise ValueError("Recovery journal does not match this installation.")
    folder = record.get("backup_dir")
    if (not isinstance(folder, str) or not folder.startswith(NAME + "-")
            or "/" in folder or "\\" in folder or folder in {".", ".."}):
        raise ValueError("Invalid recovery backup directory.")
    for field in ("installed", "current"):
        value = record.get(field)
        if (not isinstance(value, dict) or "SKILL.md" not in value
                or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items())):
            raise ValueError("Invalid recovery fingerprints.")
    directory = backup_parent_for(destination) / folder
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError(f"Recovery directory is missing or unsafe: {directory}")
    backup = directory / NAME
    target = destination / NAME
    active = snapshot(target) if exists(target) else None
    saved = snapshot(backup) if exists(backup) else None

    if active == record["installed"] and saved is None:
        print("Original installation is already in place.")
    elif saved == record["installed"] and active is None:
        backup.rename(target)
        print(f"Restored original installation: {target}")
    elif saved == record["installed"] and active == record["current"]:
        print(f"New installation is intact; completed interrupted update. Backup: {backup}")
    else:
        raise ValueError(
            f"Recovery refused: files were modified or are missing. Nothing overwritten. "
            f"Inspect {target} and {directory}."
        )
    journal.unlink()


def recover(destination):
    destination = destination.expanduser().resolve()
    with installation_lock(destination):
        recover_pending(destination)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError(f"Expected a copied directory, not a symlink: {directory}")
    result = {}
    for current, dirs, files in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED)
        for name in dirs + sorted(files):
            if name in IGNORED:
                continue
            path = Path(current) / name
            if path.is_symlink():
                raise ValueError(f"Refusing a symlink inside the skill: {path}")
            if path.is_file():
                result[path.relative_to(directory).as_posix()] = fingerprint(path.read_bytes())
            elif not path.is_dir():
                raise ValueError(f"Unsupported file type: {path}")
    return result


def revision_snapshot(root, revision):
    archive = git(root, "archive", "--format=tar", revision, "--", PACKAGE.as_posix())
    result = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
        for member in tree:
            if Path(member.name) in PACKAGE.parents:
                continue
            relative = Path(member.name).relative_to(PACKAGE)
            if any(part in IGNORED for part in relative.parts):
                continue
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError(f"Unsupported Git entry: {member.name}")
            result[relative.as_posix()] = fingerprint(tree.extractfile(member).read())
    return result


def update(root, destination, check=False, from_ref=None):
    destination = destination.expanduser().resolve()
    if check:
        return update_locked(root, destination, check, from_ref)
    with installation_lock(destination):
        return update_locked(root, destination, check, from_ref)


def update_locked(root, destination, check, from_ref):
    if exists(pending_path(destination)):
        raise ValueError(
            f'Interrupted update detected. Run: python3 scripts/update.py --recover "{destination}"'
        )
    target = destination / NAME
    installed = snapshot(target)
    if "SKILL.md" not in installed:
        raise ValueError(f"Missing SKILL.md in {target}")
    source = root / PACKAGE
    current = snapshot(source)
    revision = git(root, "rev-parse", "HEAD").decode().strip()
    if current != revision_snapshot(root, revision):
        raise ValueError("Skill source differs from HEAD; commit or review local changes before updating.")
    if current == installed:
        print(f"Already up to date: {target} (source {revision[:12]})")
        return None

    if from_ref:
        if from_ref.startswith("-"):
            raise ValueError("Invalid baseline revision")
        candidates = [git(root, "rev-parse", "--verify", from_ref + "^{commit}").decode().strip()]
    else:
        candidates = git(root, "log", "-100", "--format=%H", "HEAD", "--", PACKAGE.as_posix()).decode().splitlines()
    baseline = next((ref for ref in candidates if installed == revision_snapshot(root, ref)), None)
    if baseline is None:
        raise ValueError(
            "Installed files contain local changes or an unknown version; nothing was overwritten. "
            "Compare your files first. For an older known version use --from-ref <commit-or-tag>."
        )
    print(f"Verified installed baseline {baseline[:12]} -> source {revision[:12]}: {target}")
    if check:
        print("Check only; no files changed.")
        return None

    # Stage and verify before recording recovery data or moving the original.
    backup_parent = backup_parent_for(destination)
    backup_parent.mkdir(exist_ok=True)
    backup_dir = Path(tempfile.mkdtemp(prefix=NAME + "-", dir=backup_parent))
    staged = backup_dir / "incoming"
    backup = backup_dir / NAME
    shutil.copytree(source, staged, ignore=shutil.ignore_patterns(*IGNORED))
    if snapshot(staged) != current or snapshot(target) != installed:
        raise ValueError("Files changed during update; original installation left in place.")
    write_pending(destination, backup_dir, installed, current)
    try:
        target.rename(backup)
        print(f"Backup: {backup}")
        staged.rename(target)
        pending_path(destination).unlink()
        print(f"Updated: {target}")
        return backup
    except BaseException:
        # Also restore after Ctrl+C/SystemExit. A hard process kill is handled by --recover.
        try:
            recover_pending(destination)
        except (OSError, ValueError) as recovery_error:
            print(f"Automatic recovery incomplete: {recovery_error}\n"
                  f'Retry: python3 scripts/update.py --recover "{destination}"', file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", type=Path, default=Path.home() / ".agents" / "skills",
                        help="skills parent directory (same argument as install.sh)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="identify versions without writing files")
    mode.add_argument("--recover", action="store_true", help="safely finish or restore an interrupted update")
    parser.add_argument("--from-ref", help="known installed Git commit/tag; files must match exactly")
    args = parser.parse_args()
    try:
        if args.recover:
            if args.from_ref:
                parser.error("--from-ref cannot be combined with --recover")
            recover(args.destination)
        else:
            update(ROOT, args.destination, args.check, args.from_ref)
    except KeyboardInterrupt:
        parser.exit(130, "Update interrupted. Run --check; if recovery is requested, use --recover.\n")
    except (OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as error:
        parser.exit(1, f"Update refused or failed: {error}\n")


if __name__ == "__main__":
    main()
