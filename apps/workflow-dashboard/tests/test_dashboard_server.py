"""Behavior tests for the Bun dashboard server."""

import json
import shutil
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path


APP = Path(__file__).resolve().parents[1]
SCRIPT = APP / "dashboard_server.ts"
HTML = APP / "dashboard.html"


@unittest.skipUnless(shutil.which("bun"), "Bun is required for the dashboard server")
class DashboardServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workflow = self.root / "workflow"
        (self.workflow / "tickets").mkdir(parents=True)
        self.sessions = self.root / "sessions"
        self.sessions.mkdir()
        self.asset = self.root / "dashboard.html"
        shutil.copyfile(HTML, self.asset)
        self.processes = []
        self.process, self.base_url = self.start_server()

    def tearDown(self):
        for process in self.processes:
            process.terminate()
        for process in self.processes:
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
        self.temp.cleanup()

    def start_server(self, *extra):
        command = [
            "bun", str(SCRIPT), "--workflow", str(self.workflow),
            "--host", "127.0.0.1", "--port", "0", "--capacity", "4",
            "--asset", str(self.asset), "--sessions-root", str(self.sessions), *extra,
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.processes.append(process)
        line = process.stdout.readline()
        if not line:
            self.fail(process.stderr.read())
        return process, json.loads(line)["url"]

    def request(self, path, method="GET", base_url=None):
        return urllib.request.urlopen(
            urllib.request.Request((base_url or self.base_url) + path, method=method),
            timeout=2,
        )

    def test_serves_health_fresh_html_and_nonblocking_snapshot(self):
        with self.request("/health") as response:
            self.assertEqual(response.read(), b"ok\n")
        with self.request("/") as response:
            self.assertIn(b"Workflow status", response.read())

        started = time.monotonic()
        with self.request("/api/status") as response:
            first = json.load(response)
        self.assertLess(time.monotonic() - started, 0.5)
        self.assertEqual(first["summary"]["capacity"], 4)
        self.assertIn("snapshot_sequence", first)

        self.asset.write_text("updated asset", encoding="utf-8")
        with self.request("/") as response:
            self.assertEqual(response.read(), b"updated asset")

    def test_slow_refreshes_do_not_overlap_or_delay_http(self):
        calls = self.root / "calls.log"
        fake = self.root / "fake_worker.py"
        fake.write_text(
            "import json, sys, time\n"
            f"calls = {str(calls)!r}\n"
            "for line in sys.stdin:\n"
            "    request = json.loads(line)\n"
            "    with open(calls, 'a', encoding='utf-8') as stream: stream.write('call\\n')\n"
            "    print(json.dumps({'kind': 'response', 'id': request['id'], 'ok': True, 'refreshing': True, 'snapshot': {'generated_at': 'now', 'run': {'mode': 'active'}, 'summary': {'capacity': 4}, 'tickets': [], 'agents': [], 'alerts': []}}), flush=True)\n"
            "    time.sleep(.25)\n"
            "    print(json.dumps({'kind': 'update', 'ok': True, 'refreshing': False, 'snapshot': {'generated_at': 'now', 'run': {'mode': 'active'}, 'summary': {'capacity': 4}, 'tickets': [], 'agents': [], 'alerts': []}}), flush=True)\n",
            encoding="utf-8",
        )
        _process, base_url = self.start_server("--worker-script", str(fake), "--refresh-ms", "10")
        deadline = time.monotonic() + 1
        while (not calls.exists() or not calls.read_text(encoding="utf-8")) and time.monotonic() < deadline:
            time.sleep(.01)
        time.sleep(.1)
        self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["call"])

        started = time.monotonic()
        with self.request("/api/status", base_url=base_url) as response:
            payload = json.load(response)
        self.assertLess(time.monotonic() - started, 0.5)
        self.assertTrue(payload["telemetry_refreshing"])
        with self.request("/api/status", base_url=base_url) as response:
            unchanged = json.load(response)
        self.assertEqual(unchanged["snapshot_sequence"], payload["snapshot_sequence"])

    def test_first_snapshot_includes_integration_pending(self):
        reviews = self.workflow / "reviews"
        reviews.mkdir()
        (reviews / "T-007.md").write_text("review passed", encoding="utf-8")
        ticket = {
            "id": "T-007", "title": "Reviewed change", "status": "ready",
            "spec": "spec.md", "spec_refs": ["Dashboard"], "blocked_by": [],
            "exclusive_resources": [], "external_blockers": [], "available": False,
            "superseded_by": [], "implementation_ref": "records/T-007.md",
            "review_ref": "../reviews/T-007.md",
        }
        body = "\n".join(f"{key}: {json.dumps(value)}" for key, value in ticket.items())
        (self.workflow / "tickets" / "T-007.md").write_text(f"---\n{body}\n---\n", encoding="utf-8")
        sessions = self.root / "empty-sessions"
        sessions.mkdir()

        _process, base_url = self.start_server("--sessions-root", str(sessions))
        with self.request("/api/status", base_url=base_url) as response:
            payload = json.load(response)

        projected = next(item for item in payload["tickets"] if item["id"] == "T-007")
        self.assertEqual(projected["health"], "integration_pending")
        self.assertFalse(projected["available"])

    def test_forwards_claude_session_roots_to_snapshot_worker(self):
        arguments = self.root / "worker-arguments.json"
        fake = self.root / "argument_worker.py"
        fake.write_text(
            "import json, sys\n"
            f"path = {str(arguments)!r}\n"
            "with open(path, 'w', encoding='utf-8') as stream: json.dump(sys.argv[1:], stream)\n"
            "for line in sys.stdin:\n"
            "    request = json.loads(line)\n"
            "    snapshot = {'generated_at': 'now', 'run': {'mode': 'active'}, 'summary': {'capacity': 4}, 'tickets': [], 'agents': [], 'alerts': []}\n"
            "    print(json.dumps({'kind': 'response', 'id': request['id'], 'ok': True, 'refreshing': False, 'snapshot': snapshot}), flush=True)\n",
            encoding="utf-8",
        )
        claude_root = self.root / "claude-projects"
        claude_root.mkdir()

        self.start_server(
            "--worker-script", str(fake),
            "--claude-sessions-root", str(claude_root),
        )

        deadline = time.monotonic() + 2
        while not arguments.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        forwarded = json.loads(arguments.read_text(encoding="utf-8"))
        index = forwarded.index("--claude-sessions-root")
        self.assertEqual(forwarded[index + 1], str(claude_root))

    def test_rejects_unknown_paths_mutations_and_non_loopback_bind(self):
        with self.assertRaises(urllib.error.HTTPError) as missing:
            self.request("/missing")
        self.assertEqual(missing.exception.code, 404)
        with self.assertRaises(urllib.error.HTTPError) as mutation:
            self.request("/api/status", method="POST")
        self.assertEqual(mutation.exception.code, 405)

        result = subprocess.run(
            ["bun", str(SCRIPT), "--workflow", str(self.workflow), "--host", "0.0.0.0"],
            capture_output=True, text=True, timeout=3,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("127.0.0.1", result.stderr)


if __name__ == "__main__":
    unittest.main()
