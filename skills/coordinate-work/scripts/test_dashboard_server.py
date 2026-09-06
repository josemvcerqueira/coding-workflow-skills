import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))
import workflow_dashboard as dashboard


class DashboardServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workflow = Path(self.temp.name) / "workflow"
        (self.workflow / "tickets").mkdir(parents=True)
        self.server = dashboard.make_server(
            self.workflow,
            session_roots=[],
            capacity=4,
            host="127.0.0.1",
            port=0,
            stale_after=600,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"

    def tearDown(self):
        if hasattr(self, "server"):
            self.server.shutdown()
            self.server.server_close()
        if hasattr(self, "thread"):
            self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, path, method="GET"):
        return urllib.request.urlopen(
            urllib.request.Request(self.base_url + path, method=method),
            timeout=2,
        )

    def test_serves_health_page_and_live_snapshot(self):
        with self.request("/health") as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read(), b"ok\n")

        with self.request("/") as response:
            html = response.read().decode("utf-8")
            self.assertEqual(response.headers.get_content_type(), "text/html")
            self.assertIn("Workflow status", html)

        with self.request("/api/status") as response:
            payload = json.load(response)
            self.assertEqual(response.headers.get_content_type(), "application/json")
            self.assertEqual(payload["summary"]["capacity"], 4)
            self.assertIn("generated_at", payload)

    def test_rejects_unknown_paths_and_mutation_methods(self):
        with self.assertRaises(urllib.error.HTTPError) as missing:
            self.request("/missing")
        self.assertEqual(missing.exception.code, 404)

        with self.assertRaises(urllib.error.HTTPError) as mutation:
            self.request("/api/status", method="POST")
        self.assertEqual(mutation.exception.code, 405)

    def test_server_rejects_non_loopback_bind_by_default_policy(self):
        with self.assertRaises(ValueError):
            dashboard.make_server(
                self.workflow,
                session_roots=[],
                capacity=None,
                host="0.0.0.0",
                port=0,
                stale_after=600,
            )


if __name__ == "__main__":
    unittest.main()
