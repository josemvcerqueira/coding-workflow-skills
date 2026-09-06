"""Verify the repository test runner works when executed directly."""

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestSuiteEntrypointTests(unittest.TestCase):
    def test_direct_invocation_runs_the_discovered_suite(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "skills/test_all.py"),
                "-k",
                "test_coordinate_skill_package_contains_instructions_only",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("Ran 1 test", output)
        self.assertIn("OK", output)

    def test_root_discovery_runs_the_shared_suite(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                ".",
                "-p",
                "test_*.py",
                "-k",
                "test_coordinate_skill_package_contains_instructions_only",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("Ran 1 test", output)


if __name__ == "__main__":
    unittest.main()
