#!/usr/bin/env python3
"""Update a copied skill only when it matches a known Git revision. Python 3.9+."""
import argparse
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

NAME = "design-patterns-refactor"
PACKAGE = Path("skills") / NAME
IGNORED = {"target", "__pycache__", ".DS_Store"}
ROOT = Path(__file__).resolve().parents[1]


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
    destination = destination.expanduser().absolute()
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

    # Prevent overlapping runs of this updater. A stale lock requires manual inspection.
    lock = destination / ("." + NAME + ".update.lock")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        # Keep backups and staging outside the scanned skills directory.
        backup_parent = destination.parent / "skill-backups"
        if backup_parent.is_symlink() or backup_parent.resolve().is_relative_to(destination.resolve()):
            raise ValueError("Backup location must be a real directory outside skill scanning.")
        backup_parent.mkdir(exist_ok=True)
        backup_dir = Path(tempfile.mkdtemp(prefix=NAME + "-", dir=backup_parent))
        staged = backup_dir / "incoming"
        backup = backup_dir / NAME
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns(*IGNORED))
        if snapshot(staged) != current or snapshot(target) != installed:
            raise ValueError("Files changed during update; original installation left in place.")
        target.rename(backup)
        print(f"Backup: {backup}")
        try:
            staged.rename(target)
        except OSError as activation_error:
            try:
                backup.rename(target)
            except OSError as restore_error:
                raise OSError(f"Activation and restoration failed; original files remain at {backup}") from restore_error
            print("Activation failed; original installation restored.")
            raise activation_error
        print(f"Updated: {target}")
        return backup
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", type=Path, default=Path.home() / ".agents" / "skills",
                        help="skills parent directory (same argument as install.sh)")
    parser.add_argument("--check", action="store_true", help="identify versions without writing files")
    parser.add_argument("--from-ref", help="known installed Git commit/tag; files must match exactly")
    args = parser.parse_args()
    try:
        update(ROOT, args.destination, args.check, args.from_ref)
    except (OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as error:
        parser.exit(1, f"Update refused or failed: {error}\n")


if __name__ == "__main__":
    main()
