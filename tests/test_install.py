import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install.sh"


class InstallTest(unittest.TestCase):
    def run_install(self, destination, env=None):
        return subprocess.run(["bash", str(SCRIPT), str(destination)], cwd="/",
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
            target.symlink_to(missing)
            self.assertNotEqual(0, self.run_install(temporary).returncode)
            self.assertTrue(target.is_symlink())
            self.assertFalse(missing.exists())

    def test_default_location_uses_home_agents_skills(self):
        with tempfile.TemporaryDirectory(prefix="refactor-home-") as temporary:
            env = dict(os.environ, HOME=temporary)
            result = subprocess.run(["bash", str(SCRIPT)], env=env, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue((Path(temporary) / ".agents" / "skills" /
                             "design-patterns-refactor" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
