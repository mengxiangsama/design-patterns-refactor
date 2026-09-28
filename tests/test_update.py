import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from support import symlink_or_skip

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("skill_update", ROOT / "scripts" / "update.py")
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="refactor-update-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        self.source = self.root / updater.PACKAGE
        self.source.mkdir(parents=True)
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Installer tests")
        self.run_git("config", "user.email", "tests@example.invalid")
        (self.source / "SKILL.md").write_text("old skill", encoding="utf-8")
        (self.source / "obsolete.md").write_text("old reference", encoding="utf-8")
        self.commit()
        self.baseline = self.run_git("rev-parse", "HEAD").strip()
        self.destination = Path(self.temp.name) / "path with spaces" / "skills"
        self.destination.mkdir(parents=True)
        self.target = self.destination / updater.NAME
        shutil.copytree(self.source, self.target)
        (self.source / "SKILL.md").write_text("new skill", encoding="utf-8")
        (self.source / "obsolete.md").unlink()
        (self.source / "new.md").write_text("new reference", encoding="utf-8")
        self.commit()

    def run_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True,
                                       stderr=subprocess.PIPE)

    def commit(self):
        self.run_git("add", ".")
        self.run_git("-c", "commit.gpgsign=false", "commit", "-qm", "test revision")

    def test_update_backs_up_and_replaces_known_version(self):
        backup = updater.update(self.root, self.destination)
        self.assertEqual(updater.snapshot(self.source), updater.snapshot(self.target))
        self.assertEqual("old skill", (backup / "SKILL.md").read_text())
        self.assertTrue((backup / "obsolete.md").exists())
        self.assertFalse((self.target / "obsolete.md").exists())
        self.assertFalse(backup.is_relative_to(self.destination))

    def test_check_is_read_only(self):
        before = updater.snapshot(self.target)
        updater.update(self.root, self.destination, check=True)
        self.assertEqual(before, updater.snapshot(self.target))
        self.assertFalse((self.destination.parent / "skill-backups").exists())

    def test_modified_added_and_missing_files_block_update(self):
        for change in ("modified", "added", "missing"):
            with self.subTest(change=change):
                entry = self.target / "SKILL.md"
                entry.write_text("custom" if change == "modified" else "old skill")
                extra = self.target / "custom.md"
                if change == "added":
                    extra.write_text("mine")
                if change == "missing":
                    extra.unlink()
                    entry.unlink()
                before = updater.snapshot(self.target)
                with self.assertRaises(ValueError):
                    updater.update(self.root, self.destination)
                self.assertEqual(before, updater.snapshot(self.target))

    def test_symlink_install_is_rejected(self):
        moved = self.destination / "actual-copy"
        self.target.rename(moved)
        symlink_or_skip(self, self.target, moved)
        with self.assertRaises(ValueError):
            updater.update(self.root, self.destination)
        self.assertEqual("old skill", (moved / "SKILL.md").read_text())

    def test_nested_symlink_is_rejected(self):
        symlink_or_skip(self, self.target / "outside", self.source)
        with self.assertRaises(ValueError):
            updater.update(self.root, self.destination)

    def test_dirty_source_is_rejected(self):
        (self.source / "SKILL.md").write_text("uncommitted")
        with self.assertRaises(ValueError):
            updater.update(self.root, self.destination)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())

    def test_explicit_baseline_and_noop_update(self):
        updater.update(self.root, self.destination, from_ref=self.baseline)
        self.assertIsNone(updater.update(self.root, self.destination))

    def test_failed_activation_restores_original(self):
        original_rename = Path.rename

        def fail_activation(path, destination):
            if path.name == "incoming":
                raise OSError("simulated activation failure")
            return original_rename(path, destination)

        with patch.object(Path, "rename", fail_activation):
            with self.assertRaises(OSError):
                updater.update(self.root, self.destination)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())
        self.assertFalse(updater.pending_path(self.destination).exists())
        with updater.installation_lock(self.destination):
            pass

    def test_generated_files_are_backed_up_but_not_reinstalled(self):
        generated = self.target / "assets" / "target"
        generated.mkdir(parents=True)
        (generated / "build-output").write_text("generated")
        backup = updater.update(self.root, self.destination)
        self.assertTrue((backup / "assets" / "target" / "build-output").exists())
        self.assertFalse((self.target / "assets" / "target").exists())

    def test_failed_staging_leaves_original(self):
        with patch.object(shutil, "copytree", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                updater.update(self.root, self.destination)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())

    def test_wrong_baseline_cannot_override_customization(self):
        with self.assertRaises(ValueError):
            updater.update(self.root, self.destination, from_ref="HEAD")
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())

    def test_existing_lock_prevents_overlapping_update(self):
        with updater.installation_lock(self.destination):
            with self.assertRaises(FileExistsError):
                updater.update(self.root, self.destination)
            with self.assertRaises(FileExistsError):
                updater.recover(self.destination)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())

    def test_backup_symlink_is_rejected(self):
        backup_parent = self.destination.parent / "skill-backups"
        symlink_or_skip(self, backup_parent, self.destination)
        with self.assertRaises(ValueError):
            updater.update(self.root, self.destination)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())

    def test_ctrl_c_during_activation_restores_original(self):
        original_rename = Path.rename

        def interrupt_activation(path, destination):
            if path.name == "incoming":
                raise KeyboardInterrupt("simulated Ctrl+C")
            return original_rename(path, destination)

        with patch.object(Path, "rename", interrupt_activation):
            with self.assertRaises(KeyboardInterrupt):
                updater.update(self.root, self.destination)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())
        self.assertFalse(updater.pending_path(self.destination).exists())
        updater.update(self.root, self.destination)
        self.assertEqual(updater.snapshot(self.source), updater.snapshot(self.target))

    def hard_exit_at(self, phase):
        code = """
import os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import update
root, destination, phase = Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
original = Path.rename
def abrupt_exit(path, target):
    if phase == 'prepared' and path.name == update.NAME:
        os._exit(71)
    result = original(path, target)
    if phase == 'backed_up' and path.name == update.NAME:
        os._exit(72)
    if phase == 'activated' and path.name == 'incoming':
        os._exit(73)
    return result
Path.rename = abrupt_exit
update.update(root, destination)
"""
        result = subprocess.run([sys.executable, "-B", "-c", code, str(ROOT / "scripts"),
                                 str(self.root), str(self.destination), phase],
                                capture_output=True, text=True)
        self.assertEqual({"prepared": 71, "backed_up": 72, "activated": 73}[phase],
                         result.returncode, result.stderr)
        self.assertTrue(updater.pending_path(self.destination).exists())

    def test_hard_exit_before_move_is_recoverable(self):
        self.hard_exit_at("prepared")
        updater.recover(self.destination)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())
        self.assertFalse(updater.pending_path(self.destination).exists())

    def test_hard_exit_after_backup_is_detected_and_cli_recovers(self):
        self.hard_exit_at("backed_up")
        self.assertFalse(self.target.exists())
        journal = updater.pending_path(self.destination).read_bytes()
        with self.assertRaisesRegex(ValueError, "--recover"):
            updater.update(self.root, self.destination, check=True)
        self.assertEqual(journal, updater.pending_path(self.destination).read_bytes())
        self.assertFalse(self.target.exists())
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "update.py"),
                                 "--recover", str(self.destination)], text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())
        updater.recover(self.destination)  # Repeating recovery is harmless.
        updater.update(self.root, self.destination)
        self.assertEqual(updater.snapshot(self.source), updater.snapshot(self.target))

    def test_hard_exit_after_activation_finishes_without_rollback(self):
        self.hard_exit_at("activated")
        before = updater.snapshot(self.target)
        updater.recover(self.destination)
        self.assertEqual(before, updater.snapshot(self.target))
        self.assertEqual(updater.snapshot(self.source), before)
        self.assertFalse(updater.pending_path(self.destination).exists())

    def test_recovery_does_not_overwrite_recreated_target(self):
        self.hard_exit_at("backed_up")
        self.target.mkdir()
        (self.target / "SKILL.md").write_text("my replacement")
        with self.assertRaisesRegex(ValueError, "Nothing overwritten"):
            updater.recover(self.destination)
        self.assertEqual("my replacement", (self.target / "SKILL.md").read_text())
        self.assertTrue(updater.pending_path(self.destination).exists())

    def test_recovery_refuses_modified_backup(self):
        self.hard_exit_at("backed_up")
        record = json.loads(updater.pending_path(self.destination).read_text())
        backup = self.destination.parent / "skill-backups" / record["backup_dir"] / updater.NAME
        (backup / "SKILL.md").write_text("custom backup")
        with self.assertRaisesRegex(ValueError, "Nothing overwritten"):
            updater.recover(self.destination)
        self.assertFalse(self.target.exists())
        self.assertEqual("custom backup", (backup / "SKILL.md").read_text())

    def test_recovery_refuses_path_traversal_in_journal(self):
        self.hard_exit_at("backed_up")
        journal = updater.pending_path(self.destination)
        record = json.loads(journal.read_text())
        record["backup_dir"] = updater.NAME + "-x/../../outside"
        journal.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "Invalid recovery backup"):
            updater.recover(self.destination)
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
