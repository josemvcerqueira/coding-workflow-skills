"""Behavior tests for the workflow dashboard data layer."""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import workflow_dashboard as dashboard

NOW = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
UUID = "11111111-1111-1111-1111-111111111111"


def ticket(tid, status="in_progress", **changes):
    data = {"id": tid, "title": "Dashboard work", "status": status, "spec": "spec.md", "spec_refs": ["Dashboard"], "blocked_by": [], "exclusive_resources": [], "external_blockers": [], "available": False, "superseded_by": [], "assignee": "owner" if status == "in_progress" else None, "implementation_ref": "records/T-001.md" if status in {"implemented", "in_review", "revision_required", "ready"} else None}
    data.update(changes)
    return data


def write_ticket(workflow, data, nested=True):
    directory = workflow / "tickets" if nested else workflow
    directory.mkdir(parents=True, exist_ok=True)
    (workflow / "spec.md").write_text("# Dashboard\n", encoding="utf-8")
    body = "\n".join(f"{key}: {json.dumps(value)}" for key, value in data.items())
    (directory / f"{data['id']}.md").write_text(f"---\n{body}\n---\n", encoding="utf-8")


def event(kind, payload, timestamp="2026-09-05T11:00:00+00:00"):
    return {"type": "event_msg", "timestamp": timestamp, "payload": {"type": kind, "payload": payload}}


def token(last, total=100, context=250000):
    return {"last_token_usage": {"input_tokens": last}, "total_token_usage": {"input_tokens": total, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0, "total_tokens": total}, "model_context_window": context}


def session_lines(session_id, *, agent_path="/root/owner", parent=None, events=(), model="gpt-test"):
    meta = {"id": session_id, "session_id": session_id, "agent_path": agent_path}
    if parent:
        meta["parent_thread_id"] = parent
    return [{"type": "session_meta", "payload": meta}, {"type": "turn_context", "timestamp": "2026-09-05T10:00:00+00:00", "payload": {"model": model}}, *events]


def claude_assistant(session_id, request_id, usage, *, timestamp, model="claude-opus-5", content=None):
    message = {"model": model, "usage": usage}
    if content is not None:
        message["content"] = content
    return {
        "type": "assistant",
        "sessionId": session_id,
        "requestId": request_id,
        "uuid": f"event-{request_id}-{timestamp}",
        "timestamp": timestamp,
        "message": message,
    }


def write_jsonl(root, filename, entries, trailing_newline=True):
    root.mkdir(parents=True, exist_ok=True)
    path = root / filename
    path.write_text("\n".join(json.dumps(entry) for entry in entries) + ("\n" if trailing_newline else ""), encoding="utf-8")
    return path


def progress(agent_path="/root/owner", **changes):
    record = {"agent_path": agent_path, "parent_agent_path": "/root", "role": "implementer", "stage": "coding", "state": "active", "summary": "working", "next_action": "test"}
    record.update(changes)
    return record


def telemetry_observation(session_id, *, observed_at, context_status="normal"):
    totals = {
        "input_tokens": 100,
        "cached_input_tokens": 0,
        "output_tokens": 20,
        "reasoning_output_tokens": 0,
        "total_tokens": 120,
    }
    return {
        "session_id": session_id,
        "root_session_id": session_id,
        "agent_path": None,
        "parent_session_id": None,
        "provider": "codex",
        "model": "gpt-test",
        "model_observation": "observed",
        "observed_at": observed_at,
        "latest_input_tokens": 95 if context_status == "critical" else 10,
        "context_window": 100,
        "model_context_window": 100,
        "context_occupancy": 0.95 if context_status == "critical" else 0.1,
        "context_status": context_status,
        "totals": totals,
        "total_tokens": 120,
        "cumulative_tokens": 120,
    }


def handoff_manifest(workflow, ticket_id, stage="integration", outcome="integrated"):
    evidence = workflow / "evidence" / f"{ticket_id}-{stage}.txt"
    report = workflow / "evidence" / f"{ticket_id}-{stage}.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("check passed\n", encoding="utf-8")
    report.write_text("# Evidence\nPass.\n", encoding="utf-8")
    return {
        "schema_version": 1,
        "assignment_id": f"run:{ticket_id}:{stage}",
        "ticket_id": ticket_id,
        "stage": stage,
        "outcome": outcome,
        "source_identity": {
            "repository": str(workflow.resolve()),
            "checkout": str(workflow.resolve()),
            "base_revision": "a" * 40,
            "target_revision": "b" * 40,
            "dirty_content_manifest": None,
        },
        "report_paths": [str(report.resolve())],
        "checks": [{
            "command": "verify exact target",
            "result": "pass",
            "evidence_path": str(evidence.resolve()),
            "explicit_skips": [],
        }],
        "cleanup": {"processes": "stopped", "resources": "released", "details": []},
    }


class WorkflowDashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workflow = Path(self.temp.name) / "workflow"
        self.workflow.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_context_status_scales_with_reported_runtime_window(self):
        self.assertEqual(dashboard._context_status(200_000, 300_000), "normal")
        self.assertEqual(dashboard._context_status(240_000, 300_000), "warning")
        self.assertEqual(dashboard._context_status(285_000, 300_000), "critical")
        self.assertEqual(dashboard._context_status(None, 300_000), "unavailable")
        self.assertEqual(dashboard._context_status(200_000, None), "unavailable")

    def test_paused_runtime_is_historical_and_releases_capacity(self):
        dashboard.write_progress(
            self.workflow,
            progress("/root", role="coordinator", state="paused", summary="checkpoint saved"),
        )

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 2)

        self.assertEqual(snapshot["summary"]["reserved_agents"], 0)
        self.assertFalse(snapshot["agents"][0]["current_assignment"])

    def test_terminal_coordinator_makes_leftover_running_records_historical(self):
        """A clean run stop governs older worker heartbeats that were never closed."""
        dashboard.write_progress(
            self.workflow,
            progress(
                "/root/coordinator",
                role="coordinator",
                state="stopped",
                updated_at=NOW.isoformat(),
            ),
        )
        dashboard.write_progress(
            self.workflow,
            progress(
                "/root/old-reviewer",
                role="reviewer",
                state="running",
                updated_at=(NOW - timedelta(hours=2)).isoformat(),
            ),
        )

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 4)

        old_reviewer = next(agent for agent in snapshot["agents"] if agent["role"] == "reviewer")
        self.assertEqual(snapshot["run"]["mode"], "stopped")
        self.assertFalse(old_reviewer["current_assignment"])
        self.assertEqual(snapshot["summary"]["active_agents"], 0)
        self.assertFalse(any(alert.get("agent_path") == "/root/old-reviewer" for alert in snapshot["alerts"]))

    def test_ticket_projection_counts_only_review_rounds_returned_for_revision(self):
        review_dir = self.workflow / "reviews" / "T-001"
        review_dir.mkdir(parents=True)
        (review_dir / "R-001.md").write_text("# T-001 R-001 — revision required\n", encoding="utf-8")
        (review_dir / "R-002.md").write_text("# T-001 R-002 — ready\n", encoding="utf-8")
        (review_dir / "R-003.md").write_text("# T-001 R-003 — review blocked\n", encoding="utf-8")
        write_ticket(self.workflow, ticket("T-001"))

        view = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)["tickets"][0]

        self.assertEqual(view["revision_count"], 1)

    def test_dependency_projection_distinguishes_direct_from_ready_next(self):
        write_ticket(self.workflow, ticket("T-002", title="Stable catalog pages"))
        write_ticket(
            self.workflow,
            ticket("T-003", status="pending", title="Catalog detail", blocked_by=["T-002", "T-004"]),
        )
        write_ticket(
            self.workflow,
            ticket("T-004", status="pending", title="Catalog navigation", blocked_by=["T-002"]),
        )
        write_ticket(
            self.workflow,
            ticket("T-008", status="pending", title="Search catalog", blocked_by=["T-002"]),
        )

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        projected = next(item for item in snapshot["tickets"] if item["id"] == "T-002")

        self.assertEqual(projected["direct_unblocks"], ["T-003", "T-004", "T-008"])
        self.assertEqual(projected["ready_after_completion"], ["T-004", "T-008"])
        self.assertEqual(
            projected["still_waiting_after_completion"],
            [{"ticket_id": "T-003", "waiting_on": ["T-004"]}],
        )

    def test_liveness_uses_freshest_progress_or_telemetry(self):
        cases = [
            ("healthy", "active", NOW - timedelta(minutes=1), None, None, "healthy"),
            ("quiet", "active", NOW - timedelta(minutes=20), NOW - timedelta(minutes=1), None, "quiet"),
            ("stale", "active", NOW - timedelta(minutes=20), None, None, "stale"),
            ("blocked", "active", NOW - timedelta(minutes=1), None, "Waiting for schema", "blocked"),
            ("unexpected", "stopped", NOW - timedelta(minutes=1), None, None, "stopped_unexpectedly"),
        ]
        telemetry = []
        for index, (name, state, updated, observed, blocker, _expected) in enumerate(cases, start=1):
            ticket_id = f"T-{index:03d}"
            session_id = f"{index:08d}-1111-1111-1111-111111111111"
            write_ticket(self.workflow, ticket(ticket_id))
            dashboard.write_progress(
                self.workflow,
                progress(
                    f"/root/{name}", ticket_id=ticket_id, session_id=session_id,
                    state=state, blocker=blocker, updated_at=updated.isoformat(),
                ),
            )
            if observed is not None:
                telemetry.append(telemetry_observation(session_id, observed_at=observed.isoformat()))
        dashboard.write_progress(
            self.workflow,
            progress(
                "/root/historical", role="verifier", state="stopped",
                updated_at=(NOW - timedelta(minutes=1)).isoformat(),
            ),
        )

        snapshot = dashboard.build_snapshot(
            self.workflow, [], NOW, 600, None, telemetry_override=telemetry
        )
        agents = {agent["agent_path"]: agent for agent in snapshot["agents"]}

        for name, _state, updated, observed, _blocker, expected in cases:
            with self.subTest(name=name):
                agent = agents[f"/root/{name}"]
                self.assertEqual(agent["health"], expected)
                self.assertEqual(agent["last_progress_at"], updated.isoformat())
                expected_activity = observed.isoformat() if observed else updated.isoformat()
                self.assertEqual(agent["last_activity_at"], expected_activity)
                self.assertTrue(agent["health_reason"])
        self.assertEqual(agents["/root/historical"]["health"], "stopped")

    def test_completed_implementation_handoff_is_expected_during_review(self):
        write_ticket(
            self.workflow,
            ticket("T-001", status="in_review", assignee="run:T-001:implementation"),
        )
        dashboard.write_progress(
            self.workflow,
            progress(
                "/root/implementer",
                ticket_id="T-001",
                role="implement",
                stage="implementation",
                state="stopped",
                summary="Implementation handed off for review",
                updated_at=(NOW - timedelta(minutes=1)).isoformat(),
            ),
        )

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        implementer = snapshot["agents"][0]

        self.assertEqual(implementer["health"], "stopped")
        self.assertFalse(
            any(alert["kind"] == "stopped_unexpectedly" for alert in snapshot["alerts"])
        )
        ticket_view = snapshot["tickets"][0]
        self.assertIsNone(ticket_view["owner"])
        self.assertEqual(ticket_view["stage"], "in_review")
        self.assertEqual(ticket_view["health"], "not_reported")
        self.assertIn("No active worker", ticket_view["health_reason"])

    def test_pulse_preserves_progress_milestone_and_reports_recent_activity(self):
        milestone = NOW - timedelta(minutes=20)
        pulse_time = NOW - timedelta(minutes=1)
        original = progress(
            "/root/coordinator",
            role="coordinator",
            summary="Waiting for T-002",
            next_action="Reconcile the worker result",
            updated_at=milestone.isoformat(),
        )
        dashboard.write_progress(self.workflow, original)

        with patch.object(dashboard, "_now_iso", return_value=pulse_time.isoformat()):
            path = dashboard.pulse_progress(self.workflow, "/root/coordinator")

        saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["updated_at"], milestone.isoformat())
        self.assertEqual(saved["heartbeat_at"], pulse_time.isoformat())
        self.assertEqual(saved["summary"], "Waiting for T-002")
        self.assertEqual(saved["next_action"], "Reconcile the worker result")

        snapshot = dashboard.build_snapshot(
            self.workflow, [], NOW, 600, None, telemetry_override=[]
        )
        coordinator = snapshot["agents"][0]
        self.assertEqual(coordinator["health"], "quiet")
        self.assertEqual(coordinator["last_progress_at"], milestone.isoformat())
        self.assertEqual(coordinator["last_activity_at"], pulse_time.isoformat())

    def test_schedule_is_independent_from_liveness_and_context(self):
        session_id = "99999999-1111-1111-1111-111111111111"
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(
            self.workflow,
            progress(
                ticket_id="T-001",
                session_id=session_id,
                updated_at=(NOW - timedelta(minutes=1)).isoformat(),
                stage_started_at=(NOW - timedelta(minutes=40)).isoformat(),
                expected_duration_seconds=1800,
            ),
        )
        snapshot = dashboard.build_snapshot(
            self.workflow,
            [],
            NOW,
            600,
            None,
            telemetry_override=[
                telemetry_observation(
                    session_id,
                    observed_at=(NOW - timedelta(minutes=1)).isoformat(),
                    context_status="critical",
                )
            ],
        )

        agent = snapshot["agents"][0]
        self.assertEqual(agent["health"], "healthy")
        self.assertEqual(agent["telemetry"]["context_status"], "critical")
        self.assertEqual(agent["stage_elapsed_seconds"], 2400)
        self.assertEqual(agent["expected_duration_seconds"], 1800)
        self.assertEqual(agent["schedule_status"], "overdue")
        self.assertEqual(agent["overdue_seconds"], 600)
        self.assertIn("overdue", [alert["kind"] for alert in snapshot["alerts"]])

        dashboard.write_progress(
            self.workflow,
            progress(
                "/root/unestimated", role="verifier",
                updated_at=(NOW - timedelta(minutes=1)).isoformat(),
            ),
        )
        without_estimate = dashboard.build_snapshot(
            self.workflow, [], NOW, 600, None, telemetry_override=[]
        )
        unestimated = next(
            item for item in without_estimate["agents"]
            if item["agent_path"] == "/root/unestimated"
        )
        self.assertEqual(unestimated["schedule_status"], "not_estimated")
        self.assertIsNone(unestimated["overdue_seconds"])

    def test_reads_authoritative_nested_tickets_and_rejects_invalid_lifecycle_metadata(self):
        write_ticket(self.workflow, ticket("T-001"))
        self.assertEqual(dashboard.read_tickets(self.workflow)["T-001"]["title"], "Dashboard work")
        write_ticket(self.workflow, ticket("T-002", status="ready", available=True, implementation_ref=None))
        with self.assertRaises(ValueError): dashboard.read_tickets(self.workflow)

    def test_progress_writes_digest_disambiguated_schema_only_records_atomically(self):
        left = dashboard.write_progress(self.workflow, progress("/root/a/b", ticket_id="T-001", ignored="secret"))
        right = dashboard.write_progress(self.workflow, progress("/root/a_b", ticket_id="T-002"))
        self.assertNotEqual(left.name, right.name)
        self.assertRegex(left.name, r"root_a_b-[0-9a-f]{12}\.json")
        saved = json.loads(left.read_text())
        self.assertNotIn("ignored", saved)
        self.assertEqual(saved["schema_version"], 1)
        self.assertFalse(list((self.workflow / "progress").glob("*.tmp")))

    def test_heartbeat_cli_uses_the_documented_parent_option(self):
        arguments = ["heartbeat", str(self.workflow), "--agent-path", "/root/cli", "--role", "implementer", "--stage", "coding", "--state", "active", "--summary", "working", "--next-action", "test", "--parent", "/root"]
        self.assertEqual(dashboard.main(arguments), 0)
        self.assertEqual(len(dashboard._read_progress(self.workflow)), 1)

    def test_pulse_cli_refreshes_existing_agent_activity(self):
        milestone = (NOW - timedelta(minutes=20)).isoformat()
        pulse_time = (NOW - timedelta(minutes=1)).isoformat()
        dashboard.write_progress(
            self.workflow,
            progress("/root/cli", role="coordinator", updated_at=milestone),
        )

        with patch.object(dashboard, "_now_iso", return_value=pulse_time):
            result = dashboard.main([
                "pulse", str(self.workflow), "--agent-path", "/root/cli",
            ])

        self.assertEqual(result, 0)
        record = dashboard._read_progress(self.workflow)[0]
        self.assertEqual(record["updated_at"], milestone)
        self.assertEqual(record["heartbeat_at"], pulse_time)

    def test_heartbeat_cli_records_repeatable_reserved_test_resources(self):
        arguments = ["heartbeat", str(self.workflow), "--agent-path", "/root/cli", "--role", "implementer", "--stage", "coding", "--state", "active", "--summary", "working", "--next-action", "test", "--handoff-path", "/tmp/handoff.json", "--reserved-test-resource", "db-1", "--reserved-test-resource", "port-2"]
        self.assertEqual(dashboard.main(arguments), 0)
        record = dashboard._read_progress(self.workflow)[0]
        self.assertEqual(record["reserved_test_resources"], ["db-1", "port-2"])
        self.assertEqual(record["handoff_path"], "/tmp/handoff.json")

    def test_progress_records_stage_estimate_and_runtime_intent(self):
        stage_started = (NOW - timedelta(minutes=8)).isoformat()
        estimate_set = (NOW - timedelta(minutes=10)).isoformat()

        path = dashboard.write_progress(
            self.workflow,
            progress(
                stage_started_at=stage_started,
                expected_duration_seconds=1800,
                estimate_set_at=estimate_set,
                estimate_note="Bounded catalog read-path change",
                runtime_provider="anthropic",
                requested_model="claude-opus-5",
            ),
        )

        saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["stage_started_at"], stage_started)
        self.assertEqual(saved["expected_duration_seconds"], 1800)
        self.assertEqual(saved["estimate_set_at"], estimate_set)
        self.assertEqual(saved["estimate_note"], "Bounded catalog read-path change")
        self.assertEqual(saved["runtime_provider"], "anthropic")
        self.assertEqual(saved["requested_model"], "claude-opus-5")

    def test_progress_rejects_invalid_stage_estimate(self):
        invalid_records = (
            progress(expected_duration_seconds=0),
            progress(expected_duration_seconds=True),
            progress(stage_started_at="2026-09-05T10:00:00"),
            progress(estimate_set_at="not-a-time"),
            progress(estimate_note=""),
            progress(runtime_provider=" "),
            progress(requested_model=""),
        )

        for record in invalid_records:
            with self.subTest(record=record):
                with self.assertRaisesRegex(ValueError, "invalid progress record"):
                    dashboard.write_progress(self.workflow, record)

    def test_heartbeat_cli_records_stage_estimate_and_runtime_intent(self):
        arguments = [
            "heartbeat", str(self.workflow), "--agent-path", "/root/cli",
            "--role", "implementer", "--stage", "coding", "--state", "active",
            "--summary", "working", "--next-action", "test",
            "--stage-started-at", "2026-09-05T11:52:00+00:00",
            "--expected-duration-seconds", "1800",
            "--estimate-set-at", "2026-09-05T11:50:00+00:00",
            "--estimate-note", "Bounded catalog change",
            "--runtime-provider", "anthropic", "--requested-model", "claude-opus-5",
        ]

        self.assertEqual(dashboard.main(arguments), 0)
        record = dashboard._read_progress(self.workflow)[0]
        self.assertEqual(record["expected_duration_seconds"], 1800)
        self.assertEqual(record["runtime_provider"], "anthropic")
        self.assertEqual(record["requested_model"], "claude-opus-5")

    def test_serve_cli_replaces_itself_with_the_bun_dashboard_service(self):
        with patch.object(dashboard.os, "execvp", side_effect=OSError("captured")) as execute:
            with self.assertRaisesRegex(OSError, "captured"):
                dashboard.main([
                    "serve", str(self.workflow),
                    "--sessions-root", str(self.workflow / "sessions"),
                    "--claude-sessions-root", str(self.workflow / "claude"),
                    "--capacity", "4",
                ])

        executable, command = execute.call_args.args
        self.assertEqual(executable, "bun")
        self.assertEqual(command[0], "bun")
        self.assertTrue(command[1].endswith("dashboard_server.ts"))
        self.assertIn("--sessions-root", command)
        self.assertIn("--claude-sessions-root", command)

    def test_progress_replace_failure_cleans_temporary_file_and_read_rejects_invalid_identity(self):
        with patch.object(dashboard.os, "replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError): dashboard.write_progress(self.workflow, progress())
        self.assertFalse(list((self.workflow / "progress").glob("*.tmp")))
        path = dashboard.write_progress(self.workflow, progress())
        saved = json.loads(path.read_text()); saved["agent_path"] = "/root/other"
        path.write_text(json.dumps(saved), encoding="utf-8")
        self.assertEqual(dashboard._read_progress(self.workflow), [])

    def test_progress_dump_failure_and_invalid_utf8_degrade_without_temporary_or_snapshot_failure(self):
        with patch.object(dashboard.json, "dump", side_effect=TypeError("cannot serialize")):
            with self.assertRaises(TypeError): dashboard.write_progress(self.workflow, progress())
        self.assertFalse(list((self.workflow / "progress").glob("*.tmp")))
        directory = self.workflow / "progress"; directory.mkdir(exist_ok=True)
        (directory / "bad.json").write_bytes(b"\xff")
        self.assertEqual(dashboard._read_progress(self.workflow), [])

    def test_progress_read_degrades_malformed_schema_paths_timestamps_and_optional_types(self):
        directory = self.workflow / "progress"; directory.mkdir()
        invalid = progress(); invalid.update({"schema_version": 999, "started_at": "not-a-time", "updated_at": "also-not-a-time", "blocker": 4})
        (directory / "root_owner-deadbeefcafe.json").write_text(json.dumps(invalid), encoding="utf-8")
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        self.assertEqual(snapshot["agents"], [])
        self.assertEqual(snapshot["telemetry_available"], False)

    def test_parser_does_not_decode_or_expose_canary_in_ignored_records(self):
        root = self.workflow / "sessions"; forbidden = "PROMPT-CANARY-DO-NOT-DECODE"
        entries = [{"type": "message", "payload": {"content": forbidden, "tool": {"auth": forbidden}}}] + session_lines(UUID, events=[event("token_count", {"info": token(1)})])
        path = write_jsonl(root, UUID + ".jsonl", entries)
        original, decoded = dashboard.json.loads, []
        def track(value, *args, **kwargs):
            decoded.append(value); return original(value, *args, **kwargs)
        with patch.object(dashboard.json, "loads", side_effect=track): result = dashboard.read_token_telemetry(path)
        self.assertEqual(result["latest_input_tokens"], 1)
        self.assertEqual(result["provider"], "codex")
        self.assertEqual(result["model_observation"], "observed")
        self.assertFalse(any(forbidden in str(value) for value in decoded))
        self.assertNotIn(forbidden, json.dumps(result))

    def test_claude_parser_is_private_and_deduplicates_streaming_usage(self):
        forbidden = "CLAUDE-PROMPT-CANARY-DO-NOT-DECODE"
        root = self.workflow / "claude"
        entries = [
            claude_assistant(
                UUID,
                "request-a",
                {
                    "input_tokens": 100,
                    "cache_creation_input_tokens": 20,
                    "cache_read_input_tokens": 30,
                    "output_tokens": 5,
                    "thinking_tokens": 2,
                },
                timestamp="2026-09-05T11:40:00+00:00",
                content=[{"type": "text", "text": forbidden}],
            ),
            claude_assistant(
                UUID,
                "request-a",
                {
                    "input_tokens": 100,
                    "cache_creation_input_tokens": 20,
                    "cache_read_input_tokens": 30,
                    "output_tokens": 8,
                    "thinking_tokens": 3,
                },
                timestamp="2026-09-05T11:41:00+00:00",
            ),
            claude_assistant(
                UUID,
                "request-b",
                {
                    "input_tokens": 10,
                    "cache_creation_input_tokens": 1,
                    "cache_read_input_tokens": 2,
                    "output_tokens": 3,
                    "thinking_tokens": 1,
                },
                timestamp="2026-09-05T11:42:00+00:00",
            ),
        ]
        path = write_jsonl(root, UUID + ".jsonl", entries)
        original, decoded = dashboard.json.loads, []

        def track(value, *args, **kwargs):
            decoded.append(value)
            return original(value, *args, **kwargs)

        with patch.object(dashboard.json, "loads", side_effect=track):
            result = dashboard.read_claude_telemetry(path)

        self.assertEqual(result["provider"], "claude")
        self.assertEqual(result["model"], "claude-opus-5")
        self.assertEqual(result["model_observation"], "observed")
        self.assertEqual(result["latest_input_tokens"], 13)
        self.assertEqual(
            result["totals"],
            {
                "input_tokens": 110,
                "cached_input_tokens": 53,
                "output_tokens": 11,
                "reasoning_output_tokens": 4,
                "total_tokens": 178,
            },
        )
        self.assertEqual(result["context_status"], "unavailable")
        self.assertEqual(result["unavailable_reason"], "context_window_not_reported")
        self.assertFalse(any(forbidden in str(value) for value in decoded))
        self.assertNotIn(forbidden, json.dumps(result))

    def test_snapshot_discovers_explicit_claude_session(self):
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(
            self.workflow,
            progress(
                ticket_id="T-001",
                session_id=UUID,
                runtime_provider="anthropic",
                requested_model="claude-opus-5",
            ),
        )
        root = self.workflow / "claude-projects" / "project-a"
        write_jsonl(
            root,
            UUID + ".jsonl",
            [
                claude_assistant(
                    UUID,
                    "request-a",
                    {
                        "input_tokens": 80,
                        "cache_creation_input_tokens": 10,
                        "cache_read_input_tokens": 10,
                        "output_tokens": 5,
                    },
                    timestamp="2026-09-05T11:59:00+00:00",
                )
            ],
        )

        snapshot = dashboard.build_snapshot(
            self.workflow,
            [],
            NOW,
            600,
            None,
            claude_session_roots=[self.workflow / "claude-projects"],
        )

        observation = snapshot["agents"][0]["telemetry"]
        self.assertEqual(observation["provider"], "claude")
        self.assertEqual(observation["model"], "claude-opus-5")
        self.assertEqual(observation["latest_input_tokens"], 100)

    def test_parser_accepts_timestamp_first_jsonl_and_skips_canaries_in_accepted_records(self):
        root = self.workflow / "sessions"; forbidden = "ACCEPTED-RECORD-CANARY"
        entries = [
            {"timestamp": "2026-09-05T10:00:00+00:00", "type": "session_meta", "payload": {"id": UUID, "session_id": UUID, "agent_path": "/root/owner", "instructions": forbidden}},
            {"timestamp": "2026-09-05T10:01:00+00:00", "type": "turn_context", "payload": {"model": "gpt-test", "cwd": forbidden, "git": forbidden}},
            {"timestamp": "2026-09-05T10:02:00+00:00", "type": "event_msg", "payload": {"type": "token_count", "payload": {"info": token(9), "messages": forbidden, "tool_arguments": forbidden, "auth": forbidden}}},
        ]
        path = write_jsonl(root, UUID + ".jsonl", entries)
        original, decoded = dashboard.json.loads, []
        def track(value, *args, **kwargs):
            decoded.append(value); return original(value, *args, **kwargs)
        with patch.object(dashboard.json, "loads", side_effect=track): result = dashboard.read_token_telemetry(path)
        self.assertEqual(result["latest_input_tokens"], 9)
        self.assertFalse(any(forbidden in str(value) for value in decoded))
        self.assertNotIn(forbidden, json.dumps(result))

    def test_parser_rejects_malformed_primary_stream_and_incomplete_counters(self):
        root = self.workflow / "sessions"
        path = write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_usage_record", {"info": token(3)}), event("token_count", {"info": {"not": "tokens"}})]))
        self.assertIsNone(dashboard.read_token_telemetry(path))
        incomplete = token(4); del incomplete["total_token_usage"]["cached_input_tokens"]
        path = write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": incomplete})]))
        self.assertIsNone(dashboard.read_token_telemetry(path))

    def test_parser_rejects_counter_decreases_and_ignores_unterminated_final_line(self):
        first, second = token(100, 105), token(160000, 87)
        first["total_token_usage"]["output_tokens"] = 5; first["total_token_usage"]["total_tokens"] = 110
        second["total_token_usage"]["output_tokens"] = 4; second["total_token_usage"]["total_tokens"] = 91
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": first}), event("token_count", {"info": second})]))
        path.write_text(path.read_text(encoding="utf-8") + '{"type":"message","payload":{"content":"ignored"', encoding="utf-8")
        self.assertIsNone(dashboard.read_token_telemetry(path))

    def test_parser_accepts_task_boundary_counter_reset_and_preserves_cumulative_total(self):
        entries = session_lines(UUID, events=[
            event("token_count", {"info": token(7, 1_000)}),
            event("task_started", {"model_context_window": 300_000}),
            event("token_count", {"info": token(8, 120, 300_000)}),
        ])

        telemetry = dashboard.read_token_telemetry(
            write_jsonl(self.workflow / "sessions", UUID + ".jsonl", entries)
        )

        self.assertEqual(telemetry["latest_input_tokens"], 8)
        self.assertEqual(telemetry["context_window"], 300_000)
        self.assertEqual(telemetry["total_tokens"], 1_120)

    def test_parser_rejects_mixed_cumulative_counter_decreases(self):
        first, mixed = token(1, 100), token(2, 110)
        mixed["total_token_usage"]["cached_input_tokens"] = 0
        first["total_token_usage"]["cached_input_tokens"] = 3
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": first}), event("token_count", {"info": mixed})]))
        self.assertIsNone(dashboard.read_token_telemetry(path))

    def test_parser_rejects_impossible_cumulative_counter_relationships(self):
        cases = []
        cached = token(1, 10); cached["total_token_usage"]["cached_input_tokens"] = 11; cases.append(cached)
        reasoning = token(1, 10); reasoning["total_token_usage"]["output_tokens"] = 4; reasoning["total_token_usage"]["reasoning_output_tokens"] = 5; reasoning["total_token_usage"]["total_tokens"] = 14; cases.append(reasoning)
        total = token(1, 10); total["total_token_usage"]["output_tokens"] = 2; total["total_token_usage"]["total_tokens"] = 11; cases.append(total)
        for invalid in cases:
            path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": invalid})]))
            self.assertIsNone(dashboard.read_token_telemetry(path))

    def test_parser_supports_rollout_uuid_suffix_and_tracks_the_token_turn_model(self):
        root = self.workflow / "sessions"
        entries = session_lines(UUID, events=[event("task_started", {"model_context_window": 300000}, "2026-09-05T10:01:00+00:00"), event("token_count", {"info": {**token(2, 4), "model_context_window": 0}}, "2026-09-05T10:02:00+00:00"), {"type": "turn_context", "timestamp": "2026-09-05T10:03:00+00:00", "payload": {"model": "later-model"}}])
        parsed = dashboard.read_token_telemetry(write_jsonl(root, f"rollout-2026-{UUID}.jsonl", entries))
        self.assertEqual(parsed["session_id"], UUID)
        self.assertEqual(parsed["model"], "gpt-test")
        self.assertEqual(parsed["context_window"], 300000)

    def test_snapshot_prefers_explicit_session_id_and_requires_unique_agent_path_fallback(self):
        write_ticket(self.workflow, ticket("T-001")); dashboard.write_progress(self.workflow, progress(ticket_id="T-001", session_id="22222222-2222-2222-2222-222222222222"))
        root = self.workflow / "sessions"
        for identifier, amount in (("22222222-2222-2222-2222-222222222222", 2), ("33333333-3333-3333-3333-333333333333", 9)):
            write_jsonl(root, identifier + ".jsonl", session_lines(identifier, events=[event("token_count", {"info": token(amount)})]))
        self.assertEqual(dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)["agents"][0]["telemetry"]["latest_input_tokens"], 2)
        dashboard.write_progress(self.workflow, progress("/root/no-session", ticket_id="T-001"))
        for identifier, amount in (("44444444-4444-4444-4444-444444444444", 4), ("55555555-5555-5555-5555-555555555555", 5)):
            write_jsonl(root, identifier + ".jsonl", session_lines(identifier, agent_path="/root/no-session", events=[event("token_count", {"info": token(amount)})]))
        agents = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)["agents"]
        unavailable = next(agent for agent in agents if agent["agent_path"] == "/root/no-session")["telemetry"]
        self.assertIsNone(unavailable["latest_input_tokens"])
        self.assertEqual(unavailable["unavailable_reason"], "ambiguous_agent_path")

    def test_snapshot_does_not_fallback_when_explicit_session_id_is_missing(self):
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(self.workflow, progress(ticket_id="T-001", session_id="missing-session"))
        root = self.workflow / "sessions"
        write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": token(7)})]))
        telemetry = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)["agents"][0]["telemetry"]
        self.assertIsNone(telemetry["latest_input_tokens"])
        self.assertEqual(telemetry["session_id"], "missing-session")
        self.assertEqual(telemetry["unavailable_reason"], "session_file_missing")

    def test_snapshot_reports_malformed_explicit_session_without_losing_its_id(self):
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(self.workflow, progress(ticket_id="T-001", session_id=UUID))
        root = self.workflow / "sessions"
        write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": {"invalid": True}})]))

        telemetry = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)["agents"][0]["telemetry"]

        self.assertEqual(telemetry["session_id"], UUID)
        self.assertEqual(telemetry["unavailable_reason"], "malformed_telemetry")
        self.assertIsNone(telemetry["last_exact_observation"])

    def test_snapshot_keeps_failed_refresh_last_exact_only_as_stale_history(self):
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(self.workflow, progress(ticket_id="T-001", session_id=UUID))
        root = self.workflow / "sessions"
        path = write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": token(7)})]))
        cache = dashboard.TelemetryCache()
        first = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None, cache)["agents"][0]["telemetry"]
        self.assertEqual(first["latest_input_tokens"], 7)
        oversized = event("token_count", {"info": token(8, 110), "ignored": "x" * (dashboard.MAX_SAFE_RECORD_BYTES + 10)})
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(oversized) + "\n")

        failed = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None, cache)["agents"][0]["telemetry"]

        self.assertEqual(failed["session_id"], UUID)
        self.assertEqual(failed["unavailable_reason"], "oversized_record")
        self.assertIsNone(failed["latest_input_tokens"])
        self.assertEqual(failed["last_exact_observation"]["latest_input_tokens"], 7)
        self.assertTrue(failed["last_exact_observation"]["stale"])

    def test_snapshot_includes_ticket_dependencies_and_external_blockers_in_health_and_readiness(self):
        write_ticket(self.workflow, ticket("T-001", status="pending", external_blockers=["vendor approval"]))
        write_ticket(self.workflow, ticket("T-002", status="pending", blocked_by=["T-001"]))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        self.assertEqual(snapshot["summary"]["ready"], 0)
        self.assertEqual(snapshot["summary"]["tickets_blocked"], 1)
        self.assertEqual(snapshot["tickets"][0]["health"], "blocked")
        self.assertIn("vendor approval", snapshot["tickets"][0]["blockers"])
        self.assertEqual(snapshot["tickets"][1]["health"], "waiting")
        self.assertIn("T-001", snapshot["tickets"][1]["waiting_on"])
        alert = next(alert for alert in snapshot["alerts"] if alert.get("ticket_id") == "T-001")
        self.assertIn("vendor approval", alert["message"])
        self.assertFalse(any(alert.get("ticket_id") == "T-002" for alert in snapshot["alerts"]))

    def test_ready_unavailable_ticket_remains_visible_as_integration_pending(self):
        review = self.workflow / "reviews" / "T-001.md"
        review.parent.mkdir(parents=True)
        review.write_text("review passed", encoding="utf-8")
        write_ticket(self.workflow, ticket("T-001", status="ready", available=False, review_ref="../reviews/T-001.md"))
        write_ticket(self.workflow, ticket("T-002", status="pending", blocked_by=["T-001"]))

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        ready = next(item for item in snapshot["tickets"] if item["id"] == "T-001")
        consumer = next(item for item in snapshot["tickets"] if item["id"] == "T-002")

        self.assertFalse(ready["available"])
        self.assertEqual(ready["health"], "integration_pending")
        self.assertEqual(ready["stage"], "integration_pending")
        self.assertIn("Integrate", ready["next_action"])
        self.assertIn("T-001", consumer["waiting_on"])

    def test_ready_ticket_treats_lingering_review_records_as_history(self):
        review = self.workflow / "reviews" / "T-001.md"
        review.parent.mkdir(parents=True)
        review.write_text("review passed", encoding="utf-8")
        write_ticket(self.workflow, ticket("T-001", status="ready", available=False, review_ref="../reviews/T-001.md"))
        dashboard.write_progress(
            self.workflow,
            progress(
                "/root",
                role="coordinator",
                state="running",
                started_at=(NOW - timedelta(hours=3)).isoformat(),
                updated_at=(NOW - timedelta(seconds=30)).isoformat(),
            ),
        )
        for index, stage in enumerate(("quality", "behavior")):
            dashboard.write_progress(
                self.workflow,
                progress(
                    f"/root/{stage}-obsolete",
                    ticket_id="T-001",
                    role="reviewer",
                    stage=stage,
                    state="running",
                    blocker=f"{stage} obsolete blocker",
                    started_at=(NOW - timedelta(hours=2)).isoformat(),
                    updated_at=(NOW - timedelta(minutes=4 + index)).isoformat(),
                ),
            )
            dashboard.write_progress(
                self.workflow,
                progress(
                    f"/root/{stage}-replacement",
                    ticket_id="T-001",
                    role="reviewer",
                    stage=stage,
                    state="stopped",
                    started_at=(NOW - timedelta(minutes=30)).isoformat(),
                    updated_at=(NOW - timedelta(minutes=10)).isoformat(),
                ),
            )

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 4)
        ticket_view = snapshot["tickets"][0]
        obsolete = [agent for agent in snapshot["agents"] if agent["agent_path"].endswith("-obsolete")]

        self.assertEqual(ticket_view["owner"], "/root")
        self.assertEqual(ticket_view["stage"], "integration_pending")
        self.assertEqual(ticket_view["blockers"], [])
        self.assertEqual(snapshot["summary"]["reserved_agents"], 1)
        self.assertTrue(all(agent["current_assignment"] is False for agent in obsolete))
        self.assertFalse(any("obsolete blocker" in alert["message"] for alert in snapshot["alerts"]))

    def test_ready_available_ticket_needs_exact_integration_evidence_before_integrated(self):
        reports = self.workflow / "reports"
        reports.mkdir()
        (reports / "review.md").write_text("review passed", encoding="utf-8")
        (reports / "integration.json").write_text(json.dumps(handoff_manifest(self.workflow, "T-002")) + "\n", encoding="utf-8")
        write_ticket(self.workflow, ticket("T-001", status="ready", available=True, review_ref="../reports/review.md"))
        write_ticket(
            self.workflow,
            ticket(
                "T-002",
                status="ready",
                available=True,
                review_ref="../reports/review.md",
                integration_ref="../reports/integration.json",
                assignee="run:T-002:implementation",
            ),
        )

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        missing = next(item for item in snapshot["tickets"] if item["id"] == "T-001")
        integrated = next(item for item in snapshot["tickets"] if item["id"] == "T-002")

        self.assertEqual(missing["stage"], "integration_unreported")
        self.assertEqual(missing["health"], "integration_unreported")
        self.assertIn("integration handoff", missing["next_action"])
        self.assertEqual(integrated["stage"], "integrated")
        self.assertEqual(integrated["health"], "complete")
        self.assertIsNone(integrated["owner"])
        self.assertEqual(integrated["integration_ref"], "../reports/integration.json")
        self.assertEqual(snapshot["summary"]["tickets_integrated"], 1)
        self.assertEqual(snapshot["summary"]["tickets_available"], 2)
        self.assertEqual(snapshot["summary"]["pipeline_progress"], 88)
        self.assertIn("integration_unreported", [alert["kind"] for alert in snapshot["alerts"]])

    def test_ticket_rejects_invalid_or_mismatched_integration_manifest(self):
        reports = self.workflow / "reports"
        reports.mkdir()
        (reports / "review.md").write_text("review passed", encoding="utf-8")
        integration = reports / "integration.json"
        integration.write_text("{}\n", encoding="utf-8")
        write_ticket(self.workflow, ticket("T-001", status="ready", available=True, review_ref="../reports/review.md", integration_ref="../reports/integration.json"))
        with self.assertRaisesRegex(ValueError, "invalid integration evidence"):
            dashboard.read_tickets(self.workflow)

        empty_evidence = handoff_manifest(self.workflow, "T-001")
        empty_evidence.update(source_identity={}, report_paths=[], checks=[], cleanup={})
        integration.write_text(json.dumps(empty_evidence), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid integration evidence"):
            dashboard.read_tickets(self.workflow)

        integration.write_text(json.dumps(handoff_manifest(self.workflow, "T-001")), encoding="utf-8")
        write_ticket(self.workflow, ticket("T-001", status="in_review", available=True, integration_ref="../reports/integration.json"))
        with self.assertRaisesRegex(ValueError, "invalid integration lifecycle"):
            dashboard.read_tickets(self.workflow)

        integration.write_text(json.dumps(handoff_manifest(self.workflow, "T-999")), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid integration evidence"):
            dashboard.read_tickets(self.workflow)

    def test_snapshot_never_reports_partial_telemetry_as_an_exact_total(self):
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(self.workflow, progress(ticket_id="T-001"))
        dashboard.write_progress(self.workflow, progress("/root/unreported", ticket_id="T-001"))
        root = self.workflow / "sessions"
        write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": token(3, 9)})]))
        snapshot = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)
        self.assertFalse(snapshot["summary"]["telemetry_complete"])
        self.assertIsNone(snapshot["summary"]["cumulative_tokens"])
        self.assertFalse(snapshot["tickets"][0]["telemetry_complete"])
        self.assertIsNone(snapshot["tickets"][0]["total_tokens"])

    def test_ticket_lifecycle_matches_authoritative_validator(self):
        write_ticket(self.workflow, ticket("T-001", status="ready", available=True, review_ref=None))
        with self.assertRaises(ValueError): dashboard.read_tickets(self.workflow)
        (self.workflow / "tickets" / "T-001.md").unlink()
        write_ticket(self.workflow, ticket("T-001", status="superseded", superseded_by=[]))
        with self.assertRaises(ValueError): dashboard.read_tickets(self.workflow)
        (self.workflow / "tickets" / "T-001.md").unlink()
        write_ticket(self.workflow, ticket("T-001", status="ready", available=True, review_ref="reviews/T-001.md", external_blockers=["open"]))
        with self.assertRaises(ValueError): dashboard.read_tickets(self.workflow)

    def test_parser_accepts_direct_event_info_payload(self):
        entries = [
            {"timestamp": "2026-09-05T10:00:00+00:00", "type": "session_meta", "payload": {"id": UUID, "session_id": UUID, "agent_path": "/root/owner"}},
            {"timestamp": "2026-09-05T10:01:00+00:00", "type": "turn_context", "payload": {"model": "gpt-test"}},
            {"timestamp": "2026-09-05T10:02:00+00:00", "type": "event_msg", "payload": {"type": "token_count", "info": token(12, 12)}},
        ]
        parsed = dashboard.read_token_telemetry(write_jsonl(self.workflow / "sessions", UUID + ".jsonl", entries))
        self.assertEqual(parsed["latest_input_tokens"], 12)

    def test_parser_skips_ignored_fractional_and_exponent_numbers_without_decoding_them(self):
        canary = "NUMBER-CANARY"
        entries = session_lines(UUID, events=[event("token_count", {"info": token(6), "ignored_fraction": 0.5, "ignored_exponent": 1e6, "message": canary})])
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", entries)
        original, decoded = dashboard.json.loads, []
        def track(value, *args, **kwargs):
            decoded.append(value); return original(value, *args, **kwargs)
        with patch.object(dashboard.json, "loads", side_effect=track): parsed = dashboard.read_token_telemetry(path)
        self.assertEqual(parsed["latest_input_tokens"], 6)
        self.assertFalse(any(canary in str(value) for value in decoded))

    def test_parser_fast_skips_large_ignored_records_without_selective_parsing(self):
        large = "LARGE-IGNORED-CANARY" * 50_000
        entries = [{"timestamp": "2026-09-05T09:00:00+00:00", "type": "message", "payload": {"content": large}}]
        entries += session_lines(UUID, events=[event("token_count", {"info": token(4)})])
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", entries)
        original, parsed_sizes = dashboard._SelectiveJson.parse, []
        def track(instance):
            parsed_sizes.append(len(instance.raw)); return original(instance)
        with patch.object(dashboard._SelectiveJson, "parse", side_effect=track, autospec=True):
            result = dashboard.read_token_telemetry(path)
        self.assertEqual(result["latest_input_tokens"], 4)
        self.assertFalse(any(size > 100_000 for size in parsed_sizes))

    def test_snapshot_telemetry_cache_reads_appended_records_incrementally(self):
        root = self.workflow / "sessions"
        path = write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": token(3)})]))
        cache = dashboard.TelemetryCache()
        with patch.object(dashboard, "read_token_telemetry", wraps=dashboard.read_token_telemetry) as reader:
            dashboard._discover_telemetry([root], cache)
            dashboard._discover_telemetry([root], cache)
            self.assertEqual(reader.call_count, 1)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event("token_count", {"info": token(4, 110)})) + "\n")
            refreshed = dashboard._discover_telemetry([root], cache)
            self.assertEqual(reader.call_count, 1)
            self.assertEqual(refreshed[0]["latest_input_tokens"], 4)
            self.assertEqual(refreshed[0]["total_tokens"], 110)

    def test_telemetry_cache_accepts_a_stable_prefix_when_session_appends_during_read(self):
        root = self.workflow / "sessions"
        path = write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": token(3)})]))
        cache = dashboard.TelemetryCache()
        original = dashboard._read_token_telemetry_state

        def append_after_read(*args, **kwargs):
            result = original(*args, **kwargs)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event("token_count", {"info": token(4, 110)})) + "\n")
            return result

        with patch.object(dashboard, "_read_token_telemetry_state", side_effect=append_after_read):
            first = cache.read(path)

        self.assertEqual(first["latest_input_tokens"], 3)
        refreshed = cache.read(path)
        self.assertEqual(refreshed["latest_input_tokens"], 4)
        self.assertEqual(refreshed["total_tokens"], 110)

    def test_snapshot_parses_only_explicitly_selected_rollouts_not_unrelated_large_rollouts(self):
        target = "22222222-2222-2222-2222-222222222222"
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(self.workflow, progress(ticket_id="T-001", session_id=target))
        root = self.workflow / "sessions"
        write_jsonl(root, target + ".jsonl", session_lines(target, events=[event("token_count", {"info": token(7)})]))
        for suffix in ("33333333-3333-3333-3333-333333333333", "44444444-4444-4444-4444-444444444444"):
            write_jsonl(root, suffix + ".jsonl", session_lines(suffix, events=[event("token_count", {"info": token(2)})]) + [{"type": "message", "payload": {"content": "x" * 500_000}}])
        with patch.object(dashboard, "read_token_telemetry", wraps=dashboard.read_token_telemetry) as reader:
            snapshot = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)
        self.assertEqual(reader.call_count, 1)
        self.assertEqual(snapshot["agents"][0]["telemetry"]["session_id"], target)

    def test_parser_falls_back_for_payload_before_type_and_fails_closed_for_info_before_event_type(self):
        valid = [
            {"payload": {"id": UUID, "session_id": UUID, "agent_path": "/root/owner"}, "type": "session_meta"},
            {"payload": {"model": "gpt-test"}, "type": "turn_context"},
            {"timestamp": "2026-09-05T10:00:00+00:00", "payload": {"payload": {"info": token(3)}, "type": "token_count"}, "type": "event_msg"},
        ]
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", valid)
        self.assertEqual(dashboard.read_token_telemetry(path)["latest_input_tokens"], 3)
        malformed = [*valid[:-1], {"payload": {"payload": {"info": {"bad": True}}, "type": "token_count"}, "type": "event_msg"}, event("token_usage_record", {"info": token(4)})]
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", malformed)
        self.assertIsNone(dashboard.read_token_telemetry(path))

    def test_fast_classifier_does_not_confuse_nested_type_with_top_level_type(self):
        outer_message = {"payload": {"type": "session_meta", "id": UUID}, "type": "message"}
        raw = (json.dumps(outer_message) + "\n").encode("utf-8")
        self.assertEqual(dashboard._fast_top_level_type(raw), "message")

    def test_snapshot_joins_explicit_rollout_ids_without_ambiguating_shared_root_ancestry(self):
        identifiers = [
            ("11111111-1111-1111-1111-111111111111", 100000),
            ("22222222-2222-2222-2222-222222222222", 200000),
            ("33333333-3333-3333-3333-333333333333", 300000),
            ("44444444-4444-4444-4444-444444444444", 530000),
        ]
        root = self.workflow / "sessions"
        for number, (identifier, total) in enumerate(identifiers):
            agent_path = "/root" if number == 0 else f"/root/child-{number}"
            dashboard.write_progress(self.workflow, progress(agent_path, session_id=identifier))
            lines = session_lines(identifier, agent_path=agent_path, events=[event("token_count", {"info": token(1, total)})])
            if number:
                lines[0]["payload"]["session_id"] = identifiers[0][0]
            write_jsonl(root, identifier + ".jsonl", lines)
        snapshot = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)
        self.assertTrue(all(agent["telemetry"]["total_tokens"] is not None for agent in snapshot["agents"]))
        self.assertEqual(snapshot["summary"]["cumulative_tokens"], 1_130_000)

    def test_terminal_agents_report_stopped_while_active_agents_can_be_stale(self):
        old = (NOW - timedelta(seconds=601)).isoformat()
        dashboard.write_progress(self.workflow, progress("/root/completed", state="complete", updated_at=old))
        dashboard.write_progress(self.workflow, progress("/root/active", state="active", updated_at=old))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        completed = next(agent for agent in snapshot["agents"] if agent["agent_path"] == "/root/completed")
        active = next(agent for agent in snapshot["agents"] if agent["agent_path"] == "/root/active")
        self.assertEqual(completed["health"], "stopped")
        self.assertEqual(active["health"], "stale")
        self.assertEqual(snapshot["summary"]["attention"], 1)
        self.assertNotIn("stopped", [alert["kind"] for alert in snapshot["alerts"]])

    def test_terminal_agent_with_unresolved_blocker_keeps_blocked_health_and_precise_alert(self):
        dashboard.write_progress(
            self.workflow,
            progress(
                "/root/coordinator",
                role="coordinator",
                state="stopped",
                blocker="Missing reviewer handoff R-003",
            ),
        )

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)

        self.assertEqual(snapshot["agents"][0]["health"], "blocked")
        self.assertEqual(snapshot["summary"]["reserved_agents"], 0)
        self.assertEqual(snapshot["alerts"][0]["kind"], "blocked")
        self.assertIn("Missing reviewer handoff R-003", snapshot["alerts"][0]["message"])

    def test_oversized_primary_token_record_fails_closed_instead_of_falling_back(self):
        oversized = event("token_count", {"info": token(2), "ignored": "x" * (dashboard.MAX_SAFE_RECORD_BYTES + 10)})
        entries = session_lines(UUID, events=[oversized, event("token_usage_record", {"info": token(3)})])
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", entries)
        self.assertIsNone(dashboard.read_token_telemetry(path))

    def test_oversized_inconclusive_layout_fails_closed_instead_of_falling_back(self):
        oversized = {"payload": {"payload": {"info": token(2), "ignored": "x" * (dashboard.MAX_SAFE_RECORD_BYTES + 10)}, "type": "token_count"}, "type": "event_msg"}
        entries = session_lines(UUID, events=[oversized, event("token_usage_record", {"info": token(3)})])
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", entries)
        self.assertIsNone(dashboard.read_token_telemetry(path))

    def test_fallback_ambiguity_overrides_telemetry_selected_for_another_explicit_agent(self):
        explicit_id = "22222222-2222-2222-2222-222222222222"
        dashboard.write_progress(self.workflow, progress("/root/explicit", session_id=explicit_id))
        dashboard.write_progress(self.workflow, progress("/root/shared"))
        root = self.workflow / "sessions"
        write_jsonl(root, explicit_id + ".jsonl", session_lines(explicit_id, agent_path="/root/shared", events=[event("token_count", {"info": token(1)})]))
        other = "33333333-3333-3333-3333-333333333333"
        write_jsonl(root, other + ".jsonl", session_lines(other, agent_path="/root/shared", events=[event("token_count", {"info": token(2)})]))
        agents = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)["agents"]
        shared = next(agent for agent in agents if agent["agent_path"] == "/root/shared")
        self.assertEqual(shared["telemetry"]["unavailable_reason"], "ambiguous_agent_path")

    def test_snapshot_uses_unique_coordinator_state_as_run_mode(self):
        dashboard.write_progress(self.workflow, progress("/root", role="coordinator", state="active"))
        self.assertEqual(dashboard.build_snapshot(self.workflow, [], NOW, 600, None)["run"]["mode"], "active")

    def test_snapshot_prefers_unique_live_ticket_owner_and_surfaces_live_owner_conflicts(self):
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(self.workflow, progress("/root/old", ticket_id="T-001", state="stopped"))
        dashboard.write_progress(self.workflow, progress("/root/live", ticket_id="T-001", state="running"))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        self.assertEqual(snapshot["tickets"][0]["owner"], "/root/live")
        dashboard.write_progress(self.workflow, progress("/root/second-live", ticket_id="T-001", state="checkpointed"))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        self.assertIsNone(snapshot["tickets"][0]["owner"])
        self.assertTrue(snapshot["tickets"][0]["owner_conflict"])
        self.assertIn("owner_conflict", [alert["kind"] for alert in snapshot["alerts"]])

    def test_snapshot_uses_unique_live_coordinator_and_counts_all_nonterminal_reservations(self):
        dashboard.write_progress(self.workflow, progress("/root/old-coordinator", role="coordinator", state="completed"))
        dashboard.write_progress(self.workflow, progress("/root/coordinator", role="coordinator", state="checkpointed"))
        for index, state in enumerate(("running", "blocked", "unknown")):
            dashboard.write_progress(self.workflow, progress(f"/root/worker-{index}", state=state))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 6)
        self.assertEqual(snapshot["run"]["mode"], "checkpointed")
        self.assertEqual(snapshot["summary"]["active_agents"], 4)
        self.assertEqual(snapshot["summary"]["reserved_agents"], 4)
        dashboard.write_progress(self.workflow, progress("/root/second-coordinator", role="coordinator", state="running"))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 6)
        self.assertEqual(snapshot["run"]["mode"], "unknown")
        self.assertIn("coordinator_conflict", [alert["kind"] for alert in snapshot["alerts"]])

    def test_snapshot_uses_uniquely_latest_terminal_coordinator_when_none_are_live(self):
        old = (NOW - timedelta(seconds=200)).isoformat()
        latest = (NOW - timedelta(seconds=100)).isoformat()
        dashboard.write_progress(self.workflow, progress("/root/old", role="coordinator", state="stopped", updated_at=old))
        dashboard.write_progress(self.workflow, progress("/root/new", role="coordinator", state="completed", updated_at=latest))
        run = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)["run"]
        self.assertEqual(run["mode"], "completed")
        self.assertEqual(run["coordinator_agent_path"], "/root/new")
        dashboard.write_progress(self.workflow, progress("/root/tied", role="coordinator", state="complete", updated_at=latest))
        run = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)["run"]
        self.assertEqual(run["mode"], "unknown")
        self.assertIsNone(run["coordinator_agent_path"])

    def test_ticket_projection_uses_active_reviewer_and_excludes_obsolete_implementer_blockers(self):
        write_ticket(self.workflow, ticket("T-001", status="in_review"))
        dashboard.write_progress(self.workflow, progress("/root/old", ticket_id="T-001", state="stopped", blocker="obsolete blocker", updated_at=(NOW - timedelta(seconds=300)).isoformat()))
        dashboard.write_progress(self.workflow, progress("/root/replacement", ticket_id="T-001", state="completed", summary="replacement complete", updated_at=(NOW - timedelta(seconds=200)).isoformat()))
        dashboard.write_progress(self.workflow, progress("/root/reviewer", ticket_id="T-001", role="reviewer", stage="review", state="active", summary="reviewing replacement", updated_at=(NOW - timedelta(seconds=100)).isoformat()))
        ticket_view = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)["tickets"][0]
        self.assertEqual(ticket_view["owner"], "/root/reviewer")
        self.assertEqual(ticket_view["stage"], "review")
        self.assertEqual(ticket_view["summary"], "reviewing replacement")
        self.assertEqual(ticket_view["blockers"], [])

    def test_ticket_projection_aggregates_multiple_active_reviewers_without_owner_conflict(self):
        write_ticket(self.workflow, ticket("T-001", status="in_review"))
        dashboard.write_progress(self.workflow, progress("/root/old", ticket_id="T-001", state="stopped", blocker="obsolete blocker", updated_at=(NOW - timedelta(seconds=300)).isoformat()))
        dashboard.write_progress(self.workflow, progress("/root/replacement", ticket_id="T-001", state="completed", summary="replacement complete", updated_at=(NOW - timedelta(seconds=200)).isoformat()))
        dashboard.write_progress(self.workflow, progress("/root/reviewer-one", ticket_id="T-001", role="reviewer", stage="review", state="active", summary="first review", next_action="wait", updated_at=(NOW - timedelta(seconds=100)).isoformat()))
        dashboard.write_progress(self.workflow, progress("/root/reviewer-two", ticket_id="T-001", role="reviewer", stage="review", state="active", summary="latest review", next_action="approve", updated_at=(NOW - timedelta(seconds=50)).isoformat()))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        ticket_view = snapshot["tickets"][0]
        self.assertEqual(ticket_view["owner"], "2 reviewers")
        self.assertFalse(ticket_view["owner_conflict"])
        self.assertEqual(ticket_view["stage"], "review")
        self.assertEqual(ticket_view["summary"], "latest review")
        self.assertEqual(ticket_view["next_action"], "approve")
        self.assertEqual(ticket_view["blockers"], [])
        self.assertNotIn("owner_conflict", [alert["kind"] for alert in snapshot["alerts"]])

    def test_ticket_projection_recognizes_documented_reviewer_role_variants(self):
        write_ticket(self.workflow, ticket("T-001", status="in_review"))
        dashboard.write_progress(self.workflow, progress("/root/replacement", ticket_id="T-001", state="completed", updated_at=(NOW - timedelta(seconds=200)).isoformat()))
        dashboard.write_progress(self.workflow, progress("/root/quality", ticket_id="T-001", role="quality-reviewer", stage="review", state="active", summary="quality findings", next_action="record", updated_at=(NOW - timedelta(seconds=100)).isoformat()))
        dashboard.write_progress(self.workflow, progress("/root/behavior", ticket_id="T-001", role="behavior-reviewer", stage="review", state="active", summary="behavior findings", next_action="test", updated_at=(NOW - timedelta(seconds=50)).isoformat()))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        ticket_view = snapshot["tickets"][0]
        self.assertEqual(ticket_view["owner"], "2 reviewers")
        self.assertFalse(ticket_view["owner_conflict"])
        self.assertEqual(ticket_view["summary"], "behavior findings")
        self.assertNotIn("owner_conflict", [alert["kind"] for alert in snapshot["alerts"]])

    def test_ticket_projection_recognizes_existing_underscore_reviewer_roles(self):
        write_ticket(self.workflow, ticket("T-001", status="in_review"))
        dashboard.write_progress(self.workflow, progress("/root/old", ticket_id="T-001", state="completed"))
        dashboard.write_progress(self.workflow, progress("/root/quality", ticket_id="T-001", role="quality_reviewer", stage="quality", state="active"))
        dashboard.write_progress(self.workflow, progress("/root/behavior", ticket_id="T-001", role="behavior_reviewer", stage="behavior", state="active"))

        ticket_view = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)["tickets"][0]

        self.assertEqual(ticket_view["owner"], "2 reviewers")
        self.assertFalse(ticket_view["owner_conflict"])

    def test_deeply_nested_rollout_degrades_without_crashing_snapshot(self):
        deep = []
        for _ in range(80): deep = [deep]
        entries = session_lines(UUID, events=[event("token_count", {"info": token(1), "untrusted": deep})])
        path = write_jsonl(self.workflow / "sessions", UUID + ".jsonl", entries)
        self.assertIsNone(dashboard.read_token_telemetry(path))

    def test_snapshot_exposes_token_breakdown_and_resource_fields_with_stable_schema(self):
        write_ticket(self.workflow, ticket("T-001"))
        dashboard.write_progress(self.workflow, progress(ticket_id="T-001", session_id=UUID, file_lease="src/file.py", reserved_test_resources=["db-1"]))
        root = self.workflow / "sessions"
        write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": token(3, 9)})]))
        snapshot = dashboard.build_snapshot(self.workflow, [root], NOW, 600, None)
        agent = snapshot["agents"][0]
        self.assertEqual(agent["file_lease"], "src/file.py")
        self.assertEqual(agent["reserved_test_resources"], ["db-1"])
        self.assertEqual(set(agent["telemetry"]["totals"]), set(dashboard.TOKEN_FIELDS))
        self.assertEqual(snapshot["summary"]["cumulative_token_totals"]["total_tokens"], 9)

    def test_snapshot_rolls_up_multiple_agents_and_matches_browser_schema(self):
        write_ticket(self.workflow, ticket("T-001")); dashboard.write_progress(self.workflow, progress(ticket_id="T-001")); dashboard.write_progress(self.workflow, progress("/root/child", parent_agent_path="/root/owner", role="child", ticket_id="T-001"))
        root = self.workflow / "sessions"
        write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": token(160000, 7)})]))
        write_jsonl(root, "66666666-6666-6666-6666-666666666666.jsonl", session_lines("66666666-6666-6666-6666-666666666666", agent_path="/root/child", parent="root-session", events=[event("token_count", {"info": token(8, 11)})]))
        snapshot = dashboard.build_snapshot(self.workflow, [root], NOW, 600, 4); view = snapshot["tickets"][0]
        self.assertEqual(view["token_totals"]["total_tokens"], 18)
        self.assertEqual(snapshot["summary"]["cumulative_tokens"], 18)
        child = next(agent for agent in snapshot["agents"] if agent["agent_path"] == "/root/child")
        self.assertEqual(child["telemetry"]["total_tokens"], 11)
        self.assertIn("elapsed_seconds", view)
        self.assertIsInstance(snapshot["summary"]["pipeline_progress"], int)

    def test_snapshot_uses_weighted_lifecycle_gates_excludes_superseded_and_handles_stale(self):
        for tid, status in (("T-001", "pending"), ("T-002", "in_progress"), ("T-003", "implemented"), ("T-004", "in_review"), ("T-005", "ready"), ("T-006", "superseded")):
            changes = {"available": status == "ready", "assignee": "owner" if status == "in_progress" else None}
            if status == "ready":
                (self.workflow / "tickets" / "reviews").mkdir(parents=True, exist_ok=True)
                (self.workflow / "tickets" / "reviews" / "T-005.md").write_text("review", encoding="utf-8")
                (self.workflow / "tickets" / "reviews" / "T-005-integration.json").write_text(
                    json.dumps(handoff_manifest(self.workflow, "T-005")), encoding="utf-8"
                )
                changes["review_ref"] = "reviews/T-005.md"
                changes["integration_ref"] = "reviews/T-005-integration.json"
            if status == "superseded": changes["superseded_by"] = ["T-005"]
            write_ticket(self.workflow, ticket(tid, status=status, **changes))
        dashboard.write_progress(self.workflow, progress("/root/idle", updated_at=(NOW - timedelta(seconds=601)).isoformat()))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 2)
        self.assertEqual(snapshot["summary"]["pipeline_progress"], 50)
        self.assertEqual(snapshot["summary"]["ready"], 1)
        self.assertEqual(snapshot["summary"]["tickets_implemented"], 3)
        self.assertEqual(snapshot["summary"]["tickets_reviewed"], 1)
        self.assertEqual(snapshot["summary"]["tickets_integrated"], 1)
        self.assertFalse(snapshot["summary"]["whole_feature_verified"])
        self.assertEqual(snapshot["alerts"][0]["kind"], "stale")

    def test_whole_feature_verification_requires_an_explicit_verifier_outcome(self):
        reports = self.workflow / "reports"
        reports.mkdir()
        (reports / "review.md").write_text("review passed", encoding="utf-8")
        (reports / "integration.json").write_text(
            json.dumps(handoff_manifest(self.workflow, "T-001")), encoding="utf-8"
        )
        write_ticket(
            self.workflow,
            ticket(
                "T-001",
                status="ready",
                available=True,
                review_ref="../reports/review.md",
                integration_ref="../reports/integration.json",
            ),
        )
        dashboard.write_progress(
            self.workflow,
            progress(
                "/root/verifier",
                role="verifier",
                stage="whole_feature_verification",
                state="whole_feature_verified",
                summary="combined target passed",
                next_action="clean up",
            ),
        )

        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 2)

        self.assertFalse(snapshot["summary"]["whole_feature_verified"])

        handoff = self.workflow / "evidence" / "whole-feature-handoff.json"
        handoff.write_text(
            json.dumps(handoff_manifest(
                self.workflow,
                "feature",
                stage="whole_feature_verification",
                outcome="whole_feature_verified",
            )),
            encoding="utf-8",
        )
        dashboard.write_progress(
            self.workflow,
            progress(
                "/root/verifier",
                role="verifier",
                stage="whole_feature_verification",
                state="whole_feature_verified",
                summary="combined target passed",
                next_action="clean up",
                handoff_path=str(handoff.resolve()),
            ),
        )
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 2)

        self.assertTrue(snapshot["summary"]["whole_feature_verified"])


if __name__ == "__main__": unittest.main()
