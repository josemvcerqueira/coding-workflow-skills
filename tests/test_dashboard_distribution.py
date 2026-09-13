"""Distribution-boundary tests for the standalone workflow dashboard."""

import json
import os
import select
import shutil
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "thin-coordinator"
APP = ROOT / "apps" / "workflow-dashboard"
PACKAGE_FILES = {
    "README.md",
    "cli.ts",
    "dashboard.html",
    "dashboard_server.ts",
    "package.json",
    "workflow_dashboard.py",
}


def pack_entry(output):
    manifest = json.loads(output)
    return next(iter(manifest.values())) if isinstance(manifest, dict) else manifest[0]


class DashboardDistributionTests(unittest.TestCase):
    def test_coordinate_skill_package_contains_instructions_only(self):
        with tempfile.TemporaryDirectory(prefix="workflow dashboard ") as temporary:
            installed = Path(temporary) / "thin-coordinator"
            shutil.copytree(SKILL, installed)
            runtime_files = [
                path.relative_to(installed).as_posix()
                for path in installed.rglob("*")
                if path.is_file() and path.suffix in {".html", ".py", ".ts", ".js"}
            ]

        self.assertEqual(runtime_files, [])

    @unittest.skipUnless(shutil.which("npm"), "npm is required to build the dashboard package")
    def test_package_contains_only_runtime_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                ["npm", "pack", "--json", "--pack-destination", temporary, str(APP)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = pack_entry(result.stdout)
            packaged = {item["path"] for item in manifest["files"]}
            self.assertEqual(packaged, PACKAGE_FILES)

    @unittest.skipUnless(shutil.which("bun") and shutil.which("npm"), "Bun and npm are required for the installed dashboard CLI")
    def test_packed_cli_runs_heartbeat_and_server_outside_the_source_tree(self):
        with tempfile.TemporaryDirectory(prefix="workflow dashboard ") as temporary:
            root = Path(temporary)
            pack = subprocess.run(
                ["npm", "pack", "--json", "--pack-destination", str(root), str(APP)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(pack.returncode, 0, pack.stderr)
            tarball = root / pack_entry(pack.stdout)["filename"]
            install_root = root / "bun-install"
            environment = os.environ.copy()
            environment["BUN_INSTALL"] = str(install_root)
            install = subprocess.run(
                ["bun", "install", "--global", str(tarball)],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            executable = install_root / "bin" / "workflow-dashboard"

            help_result = subprocess.run(
                [str(executable), "--help"],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn("heartbeat", help_result.stdout)
            self.assertIn("pulse", help_result.stdout)
            self.assertIn("serve", help_result.stdout)

            serve_help = subprocess.run(
                [str(executable), "serve", "--help"],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
            self.assertEqual(serve_help.returncode, 0, serve_help.stderr)
            self.assertIn("WORKFLOW", serve_help.stdout)

            invalid = subprocess.run(
                [str(executable), "serve", str(root / "invalid-workflow"), "--bogus", "value"],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("unknown option", invalid.stderr.lower())

            workflow = Path(temporary) / "workflow"
            command = [
                str(executable),
                "heartbeat",
                str(workflow),
                "--agent-path",
                "/root/worker",
                "--parent",
                "/root",
                "--role",
                "implementer",
                "--stage",
                "implementation",
                "--state",
                "working",
                "--summary",
                "Implementing the ticket",
                "--next-action",
                "Run focused checks",
            ]
            result = subprocess.run(command, env=environment, capture_output=True, text=True, check=False)

            self.assertEqual(result.returncode, 0, result.stderr)
            record_path = Path(result.stdout.strip())
            self.assertTrue(record_path.is_file())
            record = json.loads(record_path.read_text(encoding="utf-8"))
            self.assertEqual(record["agent_path"], "/root/worker")

            pulse = subprocess.run(
                [str(executable), "pulse", str(workflow), "--agent-path", "/root/worker"],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(pulse.returncode, 0, pulse.stderr)
            pulsed = json.loads(record_path.read_text(encoding="utf-8"))
            self.assertIn("heartbeat_at", pulsed)
            self.assertEqual(pulsed["updated_at"], record["updated_at"])

            sessions = root / "sessions"
            sessions.mkdir()
            server = subprocess.Popen(
                [str(executable), "serve", str(workflow), "--sessions-root", str(sessions)],
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                assert server.stdout is not None
                ready, _, _ = select.select([server.stdout], [], [], 10)
                self.assertTrue(ready, "installed dashboard did not report its URL")
                line = server.stdout.readline()
                self.assertTrue(line, "installed dashboard closed stdout before reporting its URL")
                base_url = json.loads(line)["url"]
                with urllib.request.urlopen(base_url + "/health", timeout=2) as response:
                    self.assertEqual(response.read(), b"ok\n")
                with urllib.request.urlopen(base_url + "/", timeout=2) as response:
                    self.assertIn(b"Workflow status", response.read())
                with urllib.request.urlopen(base_url + "/api/status", timeout=2) as response:
                    self.assertIn("snapshot_sequence", json.load(response))
            finally:
                server.terminate()
                try:
                    server.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=3)
                if server.stdout:
                    server.stdout.close()
                if server.stderr:
                    server.stderr.close()


if __name__ == "__main__":
    unittest.main()
