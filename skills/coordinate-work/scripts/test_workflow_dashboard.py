"""Behavior tests for the workflow dashboard data layer."""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
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


def write_jsonl(root, filename, entries, trailing_newline=True):
    root.mkdir(parents=True, exist_ok=True)
    path = root / filename
    path.write_text("\n".join(json.dumps(entry) for entry in entries) + ("\n" if trailing_newline else ""), encoding="utf-8")
    return path


def progress(agent_path="/root/owner", **changes):
    record = {"agent_path": agent_path, "parent_agent_path": "/root", "role": "implementer", "stage": "coding", "state": "active", "summary": "working", "next_action": "test"}
    record.update(changes)
    return record


class WorkflowDashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workflow = Path(self.temp.name) / "workflow"
        self.workflow.mkdir()

    def tearDown(self):
        self.temp.cleanup()

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

    def test_heartbeat_cli_records_repeatable_reserved_test_resources(self):
        arguments = ["heartbeat", str(self.workflow), "--agent-path", "/root/cli", "--role", "implementer", "--stage", "coding", "--state", "active", "--summary", "working", "--next-action", "test", "--reserved-test-resource", "db-1", "--reserved-test-resource", "port-2"]
        self.assertEqual(dashboard.main(arguments), 0)
        self.assertEqual(dashboard._read_progress(self.workflow)[0]["reserved_test_resources"], ["db-1", "port-2"])

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
        self.assertFalse(any(forbidden in str(value) for value in decoded))
        self.assertNotIn(forbidden, json.dumps(result))

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
        self.assertEqual(telemetry["unavailable_reason"], "session_id_not_reported")

    def test_snapshot_includes_ticket_dependencies_and_external_blockers_in_health_and_readiness(self):
        write_ticket(self.workflow, ticket("T-001", status="pending", external_blockers=["vendor approval"]))
        write_ticket(self.workflow, ticket("T-002", status="pending", blocked_by=["T-001"]))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        self.assertEqual(snapshot["summary"]["ready"], 0)
        self.assertEqual(snapshot["summary"]["tickets_blocked"], 2)
        self.assertEqual(snapshot["tickets"][0]["health"], "blocked")
        self.assertIn("vendor approval", snapshot["tickets"][0]["blockers"])
        self.assertIn("T-001", snapshot["tickets"][1]["blockers"])
        alert = next(alert for alert in snapshot["alerts"] if alert.get("ticket_id") == "T-001")
        self.assertIn("vendor approval", alert["message"])

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

    def test_snapshot_telemetry_cache_reuses_unchanged_files_and_refreshes_changed_files(self):
        root = self.workflow / "sessions"
        path = write_jsonl(root, UUID + ".jsonl", session_lines(UUID, events=[event("token_count", {"info": token(3)})]))
        cache = dashboard.TelemetryCache()
        with patch.object(dashboard, "read_token_telemetry", wraps=dashboard.read_token_telemetry) as reader:
            dashboard._discover_telemetry([root], cache)
            dashboard._discover_telemetry([root], cache)
            self.assertEqual(reader.call_count, 1)
            path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            dashboard._discover_telemetry([root], cache)
            self.assertEqual(reader.call_count, 2)

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

    def test_terminal_agents_never_become_stale_but_active_agents_do(self):
        old = (NOW - timedelta(seconds=601)).isoformat()
        dashboard.write_progress(self.workflow, progress("/root/completed", state="complete", updated_at=old))
        dashboard.write_progress(self.workflow, progress("/root/active", state="active", updated_at=old))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, None)
        completed = next(agent for agent in snapshot["agents"] if agent["agent_path"] == "/root/completed")
        active = next(agent for agent in snapshot["agents"] if agent["agent_path"] == "/root/active")
        self.assertEqual(completed["health"], "complete")
        self.assertEqual(active["health"], "stale")
        self.assertEqual(snapshot["summary"]["attention"], 1)
        self.assertNotIn("complete", [alert["kind"] for alert in snapshot["alerts"]])

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
        self.assertEqual(dashboard.build_snapshot(self.workflow, [], NOW, 600, None)["run"]["mode"], "completed")
        dashboard.write_progress(self.workflow, progress("/root/tied", role="coordinator", state="complete", updated_at=latest))
        self.assertEqual(dashboard.build_snapshot(self.workflow, [], NOW, 600, None)["run"]["mode"], "unknown")

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
                changes["review_ref"] = "reviews/T-005.md"
            if status == "superseded": changes["superseded_by"] = ["T-005"]
            write_ticket(self.workflow, ticket(tid, status=status, **changes))
        dashboard.write_progress(self.workflow, progress("/root/idle", updated_at=(NOW - timedelta(seconds=601)).isoformat()))
        snapshot = dashboard.build_snapshot(self.workflow, [], NOW, 600, 2)
        self.assertEqual(snapshot["summary"]["pipeline_progress"], 50)
        self.assertEqual(snapshot["summary"]["ready"], 1)
        self.assertEqual(snapshot["alerts"][0]["kind"], "stale")


if __name__ == "__main__": unittest.main()
