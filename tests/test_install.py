import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from support import bash_executable, symlink_or_skip

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install.sh"


class InstallTest(unittest.TestCase):
    def run_install(self, destination, env=None):
        return subprocess.run([bash_executable(), SCRIPT.as_posix(), Path(destination).as_posix()],
                              cwd=tempfile.gettempdir(),
                              env=env, text=True, capture_output=True)

    def test_install_is_portable_and_excludes_build_outputs(self):
        with tempfile.TemporaryDirectory(prefix="refactor-install-") as temporary:
            target = Path(temporary) / "path with spaces"
            result = self.run_install(target)
            self.assertEqual(0, result.returncode, result.stderr)
            skill = target / "design-patterns-refactor"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertTrue((skill / "references" / "pattern-selection.md").is_file())
            self.assertTrue((skill / "assets" / "java-examples" / "pom.xml").is_file())
            self.assertTrue((skill / "LICENSE").is_file())
            self.assertEqual([], list(skill.rglob("target")))

    def test_existing_install_is_not_overwritten(self):
        with tempfile.TemporaryDirectory(prefix="refactor-install-") as temporary:
            self.assertEqual(0, self.run_install(temporary).returncode)
            entry = Path(temporary) / "design-patterns-refactor" / "SKILL.md"
            entry.write_text("local customization", encoding="utf-8")
            result = self.run_install(temporary)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("local customization", entry.read_text(encoding="utf-8"))

    def test_dangling_target_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory(prefix="refactor-install-") as temporary:
            target = Path(temporary) / "design-patterns-refactor"
            missing = Path(temporary) / "elsewhere"
            symlink_or_skip(self, target, missing)
            self.assertNotEqual(0, self.run_install(temporary).returncode)
            self.assertTrue(target.is_symlink())
            self.assertFalse(missing.exists())

    def test_pending_update_blocks_reinstall_into_missing_target(self):
        with tempfile.TemporaryDirectory(prefix="refactor-install-") as temporary:
            journal = Path(temporary) / ".design-patterns-refactor.update.json"
            journal.write_text("unfinished update", encoding="utf-8")
            result = self.run_install(temporary)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("--recover", result.stderr)
            self.assertFalse((Path(temporary) / "design-patterns-refactor").exists())
            self.assertEqual("unfinished update", journal.read_text(encoding="utf-8"))

    def test_default_location_uses_home_agents_skills(self):
        with tempfile.TemporaryDirectory(prefix="refactor-home-") as temporary:
            env = dict(os.environ, HOME=Path(temporary).as_posix())
            result = subprocess.run([bash_executable(), SCRIPT.as_posix()], env=env,
                                    text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((Path(temporary) / ".agents" / "skills" /
                             "design-patterns-refactor" / "SKILL.md").is_file())

    def test_crlf_checkout_keeps_shell_lf_and_installs(self):
        # Commit a small fixture using the REAL current scripts and attributes,
        # then test a fresh checkout with Windows-style Git conversion enabled.
        with tempfile.TemporaryDirectory(prefix="refactor-crlf-") as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            for relative in (".gitattributes", "scripts/install.sh"):
                target = source / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            entry = source / "skills" / "design-patterns-refactor" / "SKILL.md"
            entry.parent.mkdir(parents=True)
            entry.write_bytes(b"---\nname: design-patterns-refactor\ndescription: test\n---\n")
            for args in (("init", "-q"), ("config", "user.name", "Installer test"),
                         ("config", "user.email", "test@example.invalid"), ("add", "."),
                         ("-c", "commit.gpgsign=false", "commit", "-qm", "fixture")):
                subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)
            checkout = root / "checkout"
            subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", "--config",
                            "core.autocrlf=true", str(source), str(checkout)],
                           check=True, capture_output=True)
            script = checkout / "scripts" / "install.sh"
            self.assertNotIn(b"\r\n", script.read_bytes())
            installed = root / "installed with spaces"
            result = subprocess.run([bash_executable(), script.as_posix(), installed.as_posix()],
                                    text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual((checkout / "skills" / "design-patterns-refactor" / "SKILL.md").read_bytes(),
                             (installed / "design-patterns-refactor" / "SKILL.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
