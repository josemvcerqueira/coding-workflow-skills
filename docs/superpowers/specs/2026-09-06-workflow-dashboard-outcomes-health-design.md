# Workflow dashboard outcomes and worker health design

## Purpose

Extend the existing read-only workflow dashboard so a user can answer three questions without opening ticket files or runtime logs:

1. What is happening now?
2. Is the work alive, healthy, and on schedule?
3. What becomes possible when the current ticket finishes?

This design extends `2026-09-05-workflow-dashboard-design.md`. Ticket files and `RUN.md` remain authoritative. The dashboard remains a projection and gains no workflow mutation controls.

## Chosen approach

Use explicit assignment estimates, provider-aware exact telemetry, and a derived dependency projection.

The coordinator supplies an expected duration for every newly active stage. The dashboard compares actual stage elapsed time with that estimate but never treats an estimate as proof of worker health. Separately, it derives liveness from progress milestones and exact runtime telemetry. Historical durations may later suggest an estimate, but the coordinator must explicitly accept or replace that suggestion before it becomes authoritative.

The dashboard computes direct dependents and immediate next candidates from canonical `blocked_by` metadata. It does not render a large graph. The primary surface explains the consequence of the current ticket in plain language.

Provider-specific telemetry adapters expose one normalized, privacy-safe record. Codex support remains unchanged. A new Claude Code adapter proves the observed provider and model and reports exact available token values without guessing a context-window size.

## Alternatives considered

### Infer all durations from history

This reduces coordinator input but is rejected as the authority. Tickets and stages vary too much for sparse historical timings to establish a trustworthy expectation. Pauses, environment waits, review returns, and differently scoped implementation stages would contaminate the estimate.

### Use only a fixed inactivity threshold

This is simpler but cannot answer whether active work is taking longer than planned. It also conflates a worker that is actively producing model events with a worker whose last progress milestone is old.

### Render the complete dependency graph

This exposes every relationship but makes the primary dashboard harder to scan. The chosen design emphasizes the active ticket, immediate next candidates, and remaining blockers. The API still exposes enough structured data for a future full graph view.

## User-facing dashboard

### Run summary

The summary keeps overall completion and capacity and adds a prominent attention count. Blocked, stale, unexpectedly stopped, and overdue work appears at the top with a plain-language reason and age.

### Active work card

Each active ticket receives a user-oriented card containing:

- Ticket ID and outcome title.
- Current stage and owner role.
- Runtime provider and observed model, for example `Claude Code · Claude Opus 5 (observed)`.
- Liveness status and its evidence, for example `Healthy · model activity 2m ago`.
- Schedule status, for example `42m elapsed / 60m expected` or `Overdue by 12m`.
- Latest meaningful milestone and its age.
- Current next action or recorded blocker.
- `Ready next` tickets that become immediately eligible if this ticket becomes ready and available.
- `Moves closer` direct dependents that retain another unmet dependency.

For the current Polymarket state, T-002 must read approximately:

```text
T-002 · Implementation
T-002 Implementer · Claude Code · Claude Opus 5 (observed)
Healthy · model activity 2m ago
42m elapsed / 60m expected
Ready next: T-004, T-008
Moves closer: T-003 (still needs T-004)
```

The ticket list may remain compact, but active rows include the owner and observed model. The separate Agents section remains available for coordinator and multi-worker detail.

### Unavailable evidence

The UI replaces generic `Not reported` labels with precise explanations:

- `Model not observed` when only a requested model is recorded.
- `Context window not reported` when exact input tokens exist without a denominator.
- `Session telemetry not found` when no provider adapter can match the session ID.
- `Estimate missing` when an active stage has no explicit expected duration.

Requested and observed models are never presented as equivalent. A requested `opus` value cannot produce an `Opus (observed)` badge; only a parsed assistant event can.

## Dependency projection

For every non-superseded ticket, the snapshot adds:

- `direct_unblocks`: tickets whose canonical `blocked_by` contains this ticket.
- `ready_after_completion`: pending direct dependents for which all dependencies would be ready and available after simulating this ticket as ready and available.
- `still_waiting_after_completion`: direct dependents paired with the other dependencies that would remain unmet.

This is a one-ticket counterfactual, not a scheduler promise. Resource conflicts, user authority, checkout availability, and runtime capacity can still prevent dispatch. The UI labels the result `Ready next by dependency` and avoids saying a ticket will start automatically.

For T-002, `direct_unblocks` is T-003, T-004, and T-008. `ready_after_completion` is T-004 and T-008 because T-007 is already ready and available. T-003 remains in `still_waiting_after_completion` with T-004.

## Explicit stage estimates

Future active progress records add these optional, backward-compatible fields:

- `stage_started_at`: UTC timestamp for the current implementation, review, revision, integration, or verification stage.
- `expected_duration_seconds`: positive integer chosen by the coordinator for this stage.
- `estimate_set_at`: UTC timestamp when the current estimate was established.
- `estimate_note`: short reason when an estimate is changed after stage start.
- `runtime_provider`: normalized provider hint such as `codex` or `claude_code`.
- `requested_model`: the requested model label, never treated as observed evidence.

The coordinator includes the stage estimate in the assignment. The runtime records it with the accepted assignment and preserves it in subsequent progress updates. Starting a new stage creates a new stage start and estimate. Resuming after a deliberate pause creates a new stage start and estimate so paused wall time is not counted as active execution time.

Changing an estimate after work starts requires `estimate_note`. The dashboard exposes that the estimate changed and does not silently reset elapsed time. Existing progress records without these fields remain valid and display `Estimate missing` rather than receiving an inferred value.

Historical timings may later produce a labeled suggestion such as `Suggested 55m from 8 implementation stages`. The suggestion is not authoritative until the coordinator records an explicit estimate. No historical inference is required in this implementation.

## Health and schedule semantics

Health and schedule are independent axes.

### Liveness health

The dashboard derives `last_activity_at` as the newest exact timestamp among the progress milestone and matched provider telemetry. It also retains `last_progress_at` and `last_telemetry_at` so the UI can explain the conclusion.

- `blocked`: an explicit blocker is recorded.
- `healthy`: a progress milestone is recent.
- `quiet`: the milestone is older than the configured inactivity interval but exact provider telemetry is recent.
- `stale`: neither progress nor provider telemetry is recent enough to show continued activity.
- `stopped`: the progress record and ticket/run boundary both report an expected terminal state.
- `stopped_unexpectedly`: the agent reports a terminal state while its ticket remains active in a running workflow.

The existing `--stale-after` interval remains the configurable boundary and defaults to 600 seconds. `Stale` means observable activity is stale; it does not claim the process is dead. The page states the evidence, for example `Stale · no progress or model activity for 14m`.

Context pressure remains a separate advisory derived only from exact context-window telemetry. It does not override liveness.

### Schedule status

- `not_estimated`: no explicit estimate exists.
- `on_schedule`: elapsed stage time is within the expected duration.
- `overdue`: elapsed stage time exceeds the expected duration.

The UI shows exact elapsed and expected values and, when overdue, the amount beyond the estimate. It does not infer completion probability or silently extend a deadline because activity continues. A worker may therefore be `healthy` and `overdue`, which tells the user that work is continuing but deserves a coordinator check.

Active overdue, stale, blocked, and unexpectedly stopped assignments contribute to the summary attention count. Quiet work remains visible but does not become a red failure alert while exact runtime activity continues.

## Provider-aware telemetry

Telemetry discovery becomes a small adapter boundary that accepts explicit session IDs and configured roots:

- The Codex adapter reads the existing `.codex/sessions` JSONL format.
- The Claude Code adapter searches configured `.claude/projects` roots for an exact `<session-id>.jsonl` filename.

The Claude Code adapter reads only these allowlisted fields from assistant records:

- Top level: `type`, `sessionId`, `timestamp`, `requestId`, and `uuid`.
- Message: `model` and `usage`.
- Usage: `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`, and reported thinking-token counts.

It never reads, stores, or serves message content, prompts, tool inputs, tool outputs, attachments, authentication data, or environment values.

Claude Code can append repeated streaming snapshots for one request. The adapter groups records by exact request identity and retains the last complete usage observation for each request. Latest input-side context is the sum of `input_tokens`, `cache_creation_input_tokens`, and `cache_read_input_tokens` from the latest request. Cumulative totals sum only the deduplicated final observation for each request.

The adapter reports `provider: claude_code` and the observed message model such as `claude-opus-5`. If the transcript does not report a model context window, the dashboard shows the exact input-side token count with `Context window not reported`; it does not hard-code a window from a model name or infer one from an autocompaction threshold.

Provider failures degrade only the affected agent. An unreadable or malformed Claude transcript does not remove its progress record, ownership, dependency projection, or stage timing.

## Snapshot contract

The normalized agent telemetry gains `provider`, `model_observation: observed | unavailable`, `last_telemetry_at`, and precise unavailability reasons. Agent and ticket views gain:

- `last_progress_at`
- `last_activity_at`
- `health`
- `health_reason`
- `stage_elapsed_seconds`
- `expected_duration_seconds`
- `schedule_status`
- `overdue_seconds`
- `direct_unblocks`
- `ready_after_completion`
- `still_waiting_after_completion`

Existing keys remain available for backward compatibility. Snapshot generation remains deterministic and read-only.

## Error handling and alerts

One evidence problem must not erase other evidence. If Claude telemetry fails, the dashboard still shows the registered owner, requested provider, milestone age, schedule, and dependency consequences. If the estimate is missing, liveness remains usable. If dependency metadata is invalid, the existing ticket-validation error remains authoritative and the dashboard shows a precise relationship error instead of guessing.

Alerts use actionable language:

- `T-002 is stale: no progress or Claude activity for 14m.`
- `T-002 is healthy but overdue by 12m; coordinator check recommended.`
- `T-002 model telemetry is unavailable; requested Opus is not verified.`

No alert stops, restarts, reassigns, or messages a worker. Those actions remain coordinator decisions.

## Coordinator contract

At assignment or stage transition, the coordinator records the stage start, expected duration, provider hint, requested model, and exact session ID. It checks the dashboard attention states during normal coordination turns.

When an assignment is stale or overdue, the coordinator reconciles the runtime and worktree before deciding whether to wait, request a milestone, checkpoint, or recover the assignment. A dashboard alert is a reason to inspect, not authority to duplicate or terminate a worker.

The coordinator records a changed estimate with a reason. It never edits an estimate solely to clear an overdue badge.

## Verification

Data-layer tests cover:

- Direct dependents, immediate readiness after completion, and remaining blockers.
- The T-002 graph shape where only T-004 and T-008 become immediately ready.
- Explicit stage timing, pause/resume stage resets, overdue duration, and missing estimates.
- Independent combinations such as healthy and overdue, quiet and on schedule, and stale and overdue.
- Claude session discovery by exact session ID, observed model identity, input-side context calculation, streaming-record deduplication, malformed usage, and per-agent degradation.
- Privacy enforcement proving message and tool content is neither parsed into nor emitted from snapshots.

Asset tests cover the user-facing labels, active-ticket outcome summary, observed-versus-requested model wording, exact unavailable reasons, elapsed/expected display, and attention states.

Browser verification uses a representative workflow containing healthy, quiet, stale, overdue, blocked, Codex, Claude Code, and unavailable-telemetry agents. It confirms the first viewport answers the three purpose questions at desktop and narrow widths, has no console errors, and updates from one completed snapshot to the next without a page reload.

The complete dashboard and repository test suites must pass. The installed live dashboard is not replaced or restarted while another coordinator owns it; the owning coordinator performs a verified restart at a safe boundary after the new application build is available.

## Success criteria

- The current active ticket visibly names its owner, provider, and observed model.
- An Opus worker can be proven as `Claude Opus 5 (observed)` from its exact session transcript.
- Missing context-window data is precise and never estimated.
- Every active stage shows elapsed time and an explicit expected duration or an `Estimate missing` warning.
- Health identifies stale work from both milestone and provider-activity evidence.
- Schedule identifies overdue work independently of liveness.
- The dashboard tells the user which tickets become dependency-ready next and which direct dependents remain blocked.
- T-002 completion is represented as immediately enabling T-004 and T-008 while moving T-003 closer but leaving it dependent on T-004.
- Alerts explain what evidence is old or missing and recommend coordinator inspection without mutating workflow state.
- No prompts, messages, tool data, credentials, or guessed telemetry enter the snapshot or page.
