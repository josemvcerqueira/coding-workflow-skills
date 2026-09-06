# Workflow Dashboard Outcomes and Health Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the local workflow dashboard explain whether active work is healthy and on schedule, identify the actual runtime model, and show which tickets become startable when the current ticket finishes.

**Architecture:** Extend the existing schema-limited progress heartbeat with coordinator-owned stage estimates and runtime intent. Normalize Codex and Claude session transcripts into one telemetry shape, then derive liveness, schedule, and dependency projections in the Python snapshot layer so the HTML remains a read-only renderer. Preserve compatibility with old progress records and keep liveness independent from schedule and context pressure.

**Tech Stack:** Python 3 standard library, Bun/TypeScript HTTP wrapper, self-contained HTML/CSS/JavaScript, `unittest`, agent-browser.

---

### Task 1: Capture coordinator-owned stage estimates and runtime intent

**Files:**
- Modify: `apps/workflow-dashboard/tests/test_workflow_dashboard.py`
- Modify: `apps/workflow-dashboard/workflow_dashboard.py`
- Modify: `apps/workflow-dashboard/cli.ts`
- Modify: `apps/workflow-dashboard/README.md`
- Modify: `skills/coordinate-work/references/dashboard.md`

**Step 1: Write the failing progress-contract tests**

Add tests proving that a heartbeat accepts and persists only these new optional fields: `stage_started_at`, `expected_duration_seconds`, `estimate_set_at`, `estimate_note`, `runtime_provider`, and `requested_model`. Test that non-positive durations, naive timestamps, empty provider/model strings, and unknown fields are rejected. Add a CLI test that exercises the matching flags.

**Step 2: Run the focused tests and verify they fail**

Run: `python3 -m unittest apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_progress_records_stage_estimate_and_runtime_intent apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_progress_rejects_invalid_stage_estimate`

Expected: FAIL because the new progress keys and heartbeat options are not implemented.

**Step 3: Implement the schema and heartbeat flags**

Extend `OPTIONAL_PROGRESS` and `_valid_progress` without changing the required legacy schema. Require positive integer `expected_duration_seconds`, aware ISO timestamps for stage/estimate timestamps, and non-empty strings for the note/provider/model fields. Add the heartbeat CLI flags and pass their values to `write_progress`. Keep `started_at` as the assignment start and treat `stage_started_at` as the current stage clock.

**Step 4: Document the authority rule**

Update the dashboard app README and coordinator reference so every new stage assignment records an explicit expected duration. State that historical data may later suggest a number, but only the coordinator-confirmed value is authoritative. State that resume after pause starts a new stage clock and estimate.

**Step 5: Run focused tests**

Run: `python3 -m unittest apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_progress_records_stage_estimate_and_runtime_intent apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_progress_rejects_invalid_stage_estimate apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_heartbeat_cli_records_stage_estimate_and_runtime_intent`

Expected: PASS.

### Task 2: Add privacy-bounded Claude telemetry and provider/model evidence

**Files:**
- Modify: `apps/workflow-dashboard/tests/test_workflow_dashboard.py`
- Modify: `apps/workflow-dashboard/tests/test_dashboard_server.py`
- Modify: `apps/workflow-dashboard/workflow_dashboard.py`
- Modify: `apps/workflow-dashboard/dashboard_server.ts`
- Modify: `apps/workflow-dashboard/cli.ts`

**Step 1: Write failing Claude adapter tests**

Create synthetic Claude JSONL containing assistant records with `sessionId`, `requestId`, `uuid`, `timestamp`, `message.model`, and `message.usage`. Include a prompt/tool canary under `message.content` and repeated streaming usage snapshots for one request. Assert the parser never decodes or returns the canary, deduplicates each request to its final usage snapshot, computes latest input-side context as input plus cache creation plus cache read tokens, sums exact request totals, reports `provider: claude` and the observed model, and reports context-window unavailability precisely.

Add discovery tests proving an explicit progress `session_id` selects an exact Claude transcript under a configured Claude root. Add server forwarding coverage for repeatable `--claude-sessions-root`.

**Step 2: Run the focused tests and verify they fail**

Run: `python3 -m unittest apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_claude_parser_is_private_and_deduplicates_streaming_usage apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_snapshot_discovers_explicit_claude_session`

Expected: FAIL because there is no Claude telemetry adapter or root plumbing.

**Step 3: Implement the adapter and discovery**

Add a selective Claude allowlist limited to top-level identity/time fields plus `message.model` and exact usage counters. Reuse the bounded selective JSON parser, maintain request-level final snapshots, and normalize output to the existing telemetry structure with `provider`, `model`, `model_observation`, token totals, and a precise `context_window_not_reported` reason. Generalize the incremental telemetry cache with a reader/identity strategy or add an equivalently bounded Claude cache; never materialize transcript message content.

Add `claude_session_roots` to `build_snapshot` as a backward-compatible optional parameter. In CLI/server entry points, default it to `~/.claude/projects` and accept repeatable `--claude-sessions-root`. Merge Codex and Claude observations before explicit session matching. Keep ambiguity unavailable rather than guessing.

**Step 4: Run focused telemetry and server tests**

Run: `python3 -m unittest apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_claude_parser_is_private_and_deduplicates_streaming_usage apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_snapshot_discovers_explicit_claude_session apps.workflow-dashboard.tests.test_dashboard_server.py`

Expected: PASS.

### Task 3: Derive independent liveness, schedule, and dependency outcomes

**Files:**
- Modify: `apps/workflow-dashboard/tests/test_workflow_dashboard.py`
- Modify: `apps/workflow-dashboard/workflow_dashboard.py`

**Step 1: Write failing projection tests**

Add a ticket graph fixture where T-002 directly unblocks T-003, T-004, and T-008, while T-003 also waits on T-004. Assert T-002 reports all three in `direct_unblocks`, only T-004 and T-008 in `ready_after_completion`, and T-003 with remaining dependency T-004 in `still_waiting_after_completion`.

Add agent fixtures for: recent progress = `healthy`; old progress plus recent telemetry = `quiet`; both old = `stale`; explicit blocker = `blocked`; terminal worker while its ticket remains active = `stopped_unexpectedly`; and expected terminal history = `stopped`. Assert `last_progress_at`, `last_activity_at`, and a human-readable `health_reason` are projected.

Add independent schedule tests for `not_estimated`, `on_schedule`, and `overdue`, including elapsed and overdue seconds. Prove a worker can be both healthy and overdue, and that context pressure remains an advisory instead of replacing liveness.

**Step 2: Run the focused tests and verify they fail**

Run: `python3 -m unittest apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_dependency_projection_distinguishes_direct_from_ready_next apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_liveness_uses_freshest_progress_or_telemetry apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_schedule_is_independent_from_liveness_and_context`

Expected: FAIL because the snapshot lacks these projections.

**Step 3: Implement snapshot derivation**

Compute `last_activity_at` as the freshest valid timestamp from progress and telemetry. Use the exact liveness states `blocked`, `healthy`, `quiet`, `stale`, `stopped`, and `stopped_unexpectedly`, with the configured stale threshold. Derive schedule from `stage_started_at` (falling back to `started_at`) and `expected_duration_seconds`; expose `stage_elapsed_seconds`, `schedule_status`, and `overdue_seconds` without changing liveness.

Build reverse dependency edges once, simulate only the selected ticket becoming available, and expose deterministic sorted `direct_unblocks`, `ready_after_completion`, and `still_waiting_after_completion` fields. Emit alerts only for actionable blocked, stale, unexpectedly stopped, overdue, and existing ownership/integration failures; keep quiet and missing model telemetry visible but non-alarming.

**Step 4: Run focused projection tests**

Run: `python3 -m unittest apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_dependency_projection_distinguishes_direct_from_ready_next apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_liveness_uses_freshest_progress_or_telemetry apps.workflow-dashboard.tests.test_workflow_dashboard.WorkflowDashboardTests.test_schedule_is_independent_from_liveness_and_context`

Expected: PASS.

### Task 4: Replace the ambiguous active-work view with an outcome and health card

**Files:**
- Modify: `apps/workflow-dashboard/tests/test_dashboard_asset.py`
- Modify: `apps/workflow-dashboard/dashboard.html`

**Step 1: Write failing asset tests**

Assert the first view contains labels for `Working now`, `Health`, `Elapsed / expected`, `Ready next`, and `Moves closer`, and that rendering reads the provider/model, `health_reason`, schedule fields, `ready_after_completion`, and `still_waiting_after_completion`. Preserve the read-only, self-contained, text-node-only, refresh-safety tests.

**Step 2: Run the asset tests and verify they fail**

Run: `python3 -m unittest apps.workflow-dashboard.tests.test_dashboard_asset`

Expected: FAIL because the page only shows phase/returned/context and a generic agent list.

**Step 3: Implement the first-view outcome card**

Render one prominent card per currently active ticket with ticket/stage, humanized owner, runtime provider plus observed or requested model, liveness badge and reason, elapsed/expected duration with schedule status, current milestone/next action or blocker, immediately ready downstream tickets, and downstream tickets that merely move closer with their remaining dependencies. Use explicit fallback copy such as `Model not reported by runtime` and `Expected duration not set`.

Keep the compact ticket catalog and agent list as secondary context. Expand alert rendering to the new actionable kinds. Use only `textContent`/text nodes for dynamic data and retain polling/backoff behavior.

**Step 4: Run asset tests**

Run: `python3 -m unittest apps.workflow-dashboard.tests.test_dashboard_asset`

Expected: PASS.

### Task 5: Full verification without interrupting the owned Polymarket run

**Files:**
- Verify: `apps/workflow-dashboard/**`
- Verify: `skills/coordinate-work/references/dashboard.md`

**Step 1: Run the full dashboard suite**

Run: `cd apps/workflow-dashboard && bun run test`

Expected: all dashboard unit, asset, CLI, and server tests pass.

**Step 2: Run repository-level tests**

Run: `python3 test_all.py`

Expected: all repository tests pass, or any unrelated pre-existing failures are recorded with exact evidence.

**Step 3: Exercise a representative local fixture in the browser**

Start a disposable dashboard server on an ephemeral loopback port with a fixture containing an estimated active ticket, a Claude session transcript, one ready-after child, and one still-waiting child. Use agent-browser to verify the visible card answers: what is running, whether it is healthy, whether it is overdue, which model is observed, what starts next, and what only moves closer. Capture a screenshot if it materially helps verify layout.

**Step 4: Do not restart the live Polymarket dashboard**

Inspect the existing live process only through read-only requests if needed. Report that the new implementation will appear when its owning coordinator restarts or upgrades the dashboard at a safe workflow boundary.

**Step 5: Review the final diff**

Run: `git diff -- apps/workflow-dashboard skills/coordinate-work/references/dashboard.md docs/superpowers/plans/2026-09-06-workflow-dashboard-outcomes-health.md`

Expected: only scoped dashboard/coordinator documentation changes, with no transcript content or unrelated user work included.
