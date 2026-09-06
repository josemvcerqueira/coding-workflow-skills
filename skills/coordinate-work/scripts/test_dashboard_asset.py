import re
import shutil
import subprocess
import unittest
from pathlib import Path


ASSET = Path(__file__).resolve().parents[1] / "assets" / "dashboard.html"


class DashboardAssetTests(unittest.TestCase):
    def test_dashboard_is_self_contained_and_read_only(self):
        html = ASSET.read_text(encoding="utf-8")

        self.assertNotRegex(html, r'<script[^>]+src=')
        self.assertNotRegex(html, r'<link[^>]+href=["\']https?://')
        self.assertNotRegex(html, r'<form\b')
        self.assertNotRegex(html, r'<button\b')
        self.assertIn('fetch("/api/status"', html)

    def test_first_view_exposes_required_status_regions(self):
        html = ASSET.read_text(encoding="utf-8")

        for region_id in (
            "run-summary",
            "pipeline-progress",
            "alerts",
            "active-tickets",
            "agent-tree",
        ):
            self.assertRegex(html, rf'id=["\']{re.escape(region_id)}["\']')

        for label in (
            "Workflow status",
            "Pipeline progress",
            "Active tickets",
            "Tickets blocked",
            "Agents and context",
            "Latest context",
            "Cumulative tokens",
            "Cumulative input",
            "Cached input",
            "Output",
            "Reasoning output",
            "File lease",
            "Reserved resources",
        ):
            self.assertIn(label, html)

    def test_dynamic_content_uses_text_nodes(self):
        html = ASSET.read_text(encoding="utf-8")

        self.assertIn("textContent", html)
        self.assertNotIn("innerHTML", html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('Object.prototype.hasOwnProperty.call(summary, "cumulative_tokens")', html)
        self.assertIn('tokens === null ? "unavailable or incomplete"', html)
        self.assertNotIn('notation:', html)
        self.assertIn('parent === currentName', html)

    def test_inline_javascript_has_valid_syntax_when_node_is_available(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not installed")
        script = re.search(r"<script>(.*?)</script>", ASSET.read_text(encoding="utf-8"), re.DOTALL)
        self.assertIsNotNone(script)
        result = subprocess.run(
            [node, "--check"],
            input=script.group(1),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
