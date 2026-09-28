import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

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
        self.target.symlink_to(moved, target_is_directory=True)
        with self.assertRaises(ValueError):
            updater.update(self.root, self.destination)
        self.assertEqual("old skill", (moved / "SKILL.md").read_text())

    def test_nested_symlink_is_rejected(self):
        (self.target / "outside").symlink_to(self.source, target_is_directory=True)
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
        self.assertFalse((self.destination / ("." + updater.NAME + ".update.lock")).exists())

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
        lock = self.destination / ("." + updater.NAME + ".update.lock")
        lock.write_text("another updater")
        with self.assertRaises(FileExistsError):
            updater.update(self.root, self.destination)
        self.assertEqual("another updater", lock.read_text())
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())

    def test_backup_symlink_is_rejected(self):
        backup_parent = self.destination.parent / "skill-backups"
        backup_parent.symlink_to(self.destination, target_is_directory=True)
        with self.assertRaises(ValueError):
            updater.update(self.root, self.destination)
        self.assertEqual("old skill", (self.target / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
