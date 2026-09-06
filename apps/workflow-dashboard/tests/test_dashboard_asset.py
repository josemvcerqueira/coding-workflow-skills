import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


ASSET = Path(__file__).resolve().parents[1] / "dashboard.html"


class DashboardAssetTests(unittest.TestCase):
    def test_palette_uses_indigo_without_green_tokens_or_green_hex_values(self):
        html = ASSET.read_text(encoding="utf-8").lower()

        self.assertIn("--accent:", html)
        self.assertIn("--accent-soft:", html)
        self.assertIn("background: var(--accent)", html)
        self.assertNotIn("--green", html)
        for green in ("#167451", "#e7f4ee", "#c9e5d9", "#6ad6ae", "#17372c"):
            self.assertNotIn(green, html)

    def test_dashboard_is_self_contained_and_read_only(self):
        html = ASSET.read_text(encoding="utf-8")

        self.assertNotRegex(html, r'<script[^>]+src=')
        self.assertNotRegex(html, r'<link[^>]+href=["\']https?://')
        self.assertNotRegex(html, r'<form\b')
        self.assertNotRegex(html, r'<button\b')
        self.assertIn('fetch("/api/status"', html)

    def test_status_colors_distinguish_progress_review_and_attention(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not installed")
        script = re.search(r"<script>(.*?)</script>", ASSET.read_text(encoding="utf-8"), re.DOTALL)
        source = script.group(1).replace("    refresh();\n", "")
        expected = {
            "Not started": "tone-neutral", "Replaced": "tone-neutral", "Unknown": "tone-neutral",
            "Connecting": "tone-neutral", "Not reported": "tone-neutral",
            "Running": "tone-info", "Implementation": "tone-info",
            "Review": "tone-review", "Awaiting review": "tone-warning",
            "Rework": "tone-warning", "Paused": "tone-warning", "Overdue": "tone-warning",
            "Complete": "tone-good", "Review complete": "tone-good", "Healthy": "tone-good",
            "Blocked": "tone-critical", "Failed": "tone-critical",
            "Unexpected stop": "tone-critical", "Connection lost": "tone-critical",
        }
        probe = source + "\nconsole.log(JSON.stringify(Object.fromEntries(" + json.dumps(list(expected)) + ".map(label => [label, tone(label)]))));\n"
        result = subprocess.run([node], input=probe, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), expected)

    def test_first_view_exposes_required_status_regions(self):
        html = ASSET.read_text(encoding="utf-8")

        for region_id in (
            "run-summary",
            "alerts",
            "working-now",
            "active-tickets",
            "agent-tree",
        ):
            self.assertRegex(html, rf'id=["\']{re.escape(region_id)}["\']')

        for label in (
            "Workflow status",
            "Tickets",
            "Agents",
            "Progress",
            "Active agents",
            "Attention",
            "Returned",
        ):
            self.assertIn(label, html)

        for jargon in (
            "Reserved runtimes",
            "Cumulative tokens",
            "Cumulative input",
            "Reasoning output",
            "File lease",
            "Reserved resources",
            "Historical agents",
            "Exact telemetry",
        ):
            self.assertNotIn(jargon, html)

    def test_ticket_and_agent_sections_render_compact_human_projections(self):
        html = ASSET.read_text(encoding="utf-8")

        self.assertIn('const tickets = data.tickets || [];', html)
        self.assertIn("for (const ticket of tickets)", html)
        self.assertIn("humanAgentName", html)
        self.assertIn("ticketPhase", html)
        self.assertIn("revision_count", html)
        self.assertIn("ticket.available === true", html)
        self.assertIn("coordinator_agent_path", html)
        self.assertIn("const currentAgents", html)
        self.assertNotIn("agentDepth", html)
        self.assertNotIn("token-breakdown", html)
        self.assertNotIn("contract-grid", html)

    def test_page_normalizes_legacy_snapshots_from_a_running_preinstall_worker(self):
        html = ASSET.read_text(encoding="utf-8")

        self.assertIn("function ticketIntegrated(ticket)", html)
        self.assertIn("function currentAssignment(agent, tickets)", html)
        self.assertIn("currentAssignment(agent, tickets)", html)
        self.assertIn("if (!tickets.length)", html)
        self.assertIn("terminalHistoryStates.has(agent.state)", html)

    def test_dynamic_content_uses_text_nodes(self):
        html = ASSET.read_text(encoding="utf-8")

        self.assertIn("textContent", html)
        self.assertNotIn("innerHTML", html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('agent.role === "coordinator"', html)
        self.assertIn('`${Math.round(context)}%`', html)
        self.assertIn("AbortController", html)
        self.assertIn("refreshInFlight", html)
        self.assertIn("snapshot_sequence", html)
        self.assertIn("sequence > latestSequence", html)
        self.assertIn("generatedAt !== latestGeneratedAt", html)
        self.assertIn("telemetry_refresh_error", html)
        self.assertIn("refreshError !== latestRefreshError", html)
        self.assertIn("The last snapshot is still shown", html)
        self.assertIn("window.setTimeout(refresh", html)
        self.assertNotIn("window.setInterval(refresh", html)
        self.assertIn('notation: "compact"', html)
        self.assertNotIn("last_exact_observation", html)

    def test_working_now_cards_explain_health_timing_model_and_downstream_outcomes(self):
        html = ASSET.read_text(encoding="utf-8")

        for label in (
            "Working now",
            "Health",
            "Elapsed / expected",
            "Ready next",
            "Moves closer",
        ):
            self.assertIn(label, html)

        for field in (
            "health_reason",
            "stage_elapsed_seconds",
            "expected_duration_seconds",
            "schedule_status",
            "observed_provider",
            "observed_model",
            "requested_model",
            "ready_after_completion",
            "still_waiting_after_completion",
        ):
            self.assertIn(field, html)

        self.assertIn("Model not reported by runtime", html)
        self.assertIn("Expected duration not set", html)

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

    def test_claude_usage_without_context_window_stays_visible(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not installed")
        script = re.search(r"<script>(.*?)</script>", ASSET.read_text(encoding="utf-8"), re.DOTALL)
        self.assertIsNotNone(script)
        source = script.group(1).replace("    refresh();\n", "")
        fixture = {
            "telemetry": {
                "latest_input_tokens": 126_296,
                "context_window": None,
                "totals": {"total_tokens": 60_509_136},
            }
        }
        probe = source + "\nconsole.log(JSON.stringify(tokenUsage(" + json.dumps(fixture) + ")));\n"

        result = subprocess.run(
            [node], input=probe, text=True, capture_output=True, check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {"value": "126K latest input", "note": "60.5M session total"},
        )


if __name__ == "__main__":
    unittest.main()
