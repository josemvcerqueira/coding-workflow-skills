# Dashboard visibility and context policy

## Scope and authority

This reference applies to an active local coordination run. Read it with [run state and recovery](run-state.md); that reference remains the source for coordinator ownership, dispatch recovery, pause controls, and safe takeover.

The dashboard is a standalone application distributed outside the skill package. `thin-coordinator` contains its coordination contract only. It never searches its own directory for an HTML page or runtime script, copies the application into a skill installation, or installs it during a run. This separation does not change ticket ownership, lifecycle authority, scheduling, or user authorization.

Ticket files remain authoritative for requirements and lifecycle. `RUN.md` remains authoritative for coordination policy and history. The dashboard cannot mutate either, dispatch work, stop an agent, or confer authority to commit, integrate, or clean up resources. Its dependency projection answers what a ticket will unblock; it never authorizes the projected work to start.

Project four lifecycle facts separately: `implemented`, `reviewed`, `integrated`, and `whole-feature verified`. A ticket at `implemented` has not passed review. A reviewed ticket can still be integration pending. An integrated ticket can still lack whole-feature verification. Count integration only when a ready, available ticket has a valid `integration_ref` to the coordinator's exact integration handoff; availability alone supports dependency scheduling but does not prove that gate. Display `Not reported` when the authoritative records do not prove a gate; never collapse these into a single ready or complete count.

## Required records

At run start, the coordinator resolves `workflow-dashboard` once from `PATH` and supplies that availability state to workers; workers do not repeat discovery. When it is available, each visible runtime keeps one atomic JSON progress record under `<workflow>/progress/` through that command. Required record fields are schema version, canonical `agent_path`, `parent_agent_path` (or an explicit root value), `role`, `stage`, `state`, `summary`, `started_at`, `updated_at`, and `next_action`. Include `ticket_id` for ticket work. For every newly assigned stage, the coordinator also records an aware `stage_started_at`, positive `expected_duration_seconds`, aware `estimate_set_at`, and optional short `estimate_note`. Include `runtime_provider` and `requested_model` when dispatch intent is known. Include the runtime `session_id`, blocker, file lease, exact `handoff_path`, and safe reserved-resource identifiers only when they are known and applicable. A coordinator record may also contain `heartbeat_at`, maintained only through the liveness pulse below. Keep the authoritative resource ownership and release conditions in the `RUN.md` runtime and reservation maps.

The explicit coordinator estimate is authoritative. Historical ticket data may later provide a suggested duration, but it cannot silently replace or revise the recorded estimate. When work resumes after a pause, record a new stage clock and estimate; preserve the assignment-level `started_at` for audit history.

Use the CLI's progress interface:

```text
workflow-dashboard heartbeat /absolute/canonical/workflow \
  --agent-path <canonical-agent-path> --role <role> --stage <stage> \
  --state <state> --summary <short-summary> --next-action <next-action> \
  [--parent <canonical-parent-path>] [--ticket <ticket-id>] \
  [--session-id <runtime-session-id>] [--blocker <blocker>] \
  [--stage-started-at <aware-iso-time>] \
  [--expected-duration-seconds <positive-seconds>] \
  [--estimate-set-at <aware-iso-time>] [--estimate-note <short-reason>] \
  [--runtime-provider <provider>] [--requested-model <model>] \
  [--file-lease <path>] [--handoff-path <exact-handoff-json-path>] \
  [--reserved-test-resource <safe-resource-id>]...
```

Mirror only safe resource identifiers already registered in `RUN.md` through the repeatable `--reserved-test-resource` option; `RUN.md` remains authoritative for their ownership and release conditions. Add `handoff_path` when the assignment has written its allocated manifest. Write a record at meaningful changes only: assignment accepted, code or evidence located, failing test observed, implementation underway, checks running, blocked, checkpointed, or handoff complete. Do not send unchanged periodic heartbeats merely to appear active. Record age is diagnostic evidence for coordinator reconciliation, not a user-facing state.

Use terminal states precisely. A worker that finishes its assigned stage, writes its required handoff, and releases its owned resources records `completed`. Reserve `stopped` for a worker that ends before a successful stage handoff, and `paused` for an intentional workflow pause with a durable checkpoint. The coordinator advances the ticket only after reconciling the handoff; it does not rewrite the worker's terminal record. For compatibility with older runs, the dashboard treats a stopped implementation worker as historical once the ticket has advanced to `implemented`, `in_review`, `revision_required`, or `ready`, and treats a stopped reviewer as historical once the ticket reaches `revision_required` or `ready`.

An owning coordinator is the exception because it can be alive while its milestone stays unchanged during an event wait. When the dashboard is enabled, pulse before the stale threshold would expire and around bounded event waits:

```text
workflow-dashboard pulse <workflow> --agent-path <coordinator-agent-path>
```

The pulse atomically updates only `heartbeat_at`. It preserves `updated_at`, `started_at`, the milestone summary, and the next action. Pulse is liveness evidence, not progress evidence: an old milestone plus a fresh pulse projects as `quiet`, not `healthy`. Workers continue to use meaningful progress and exact runtime telemetry; do not generate synthetic worker pulses. A standalone status-only inspection never pulses. When a status question interrupts an already-owned execution run, answer in commentary, pulse if due because the run continues, then return to the coordination loop.

Before or immediately after dispatch, the coordinator records the same canonical agent path, parent path, role, ticket/assignment, runtime/host, optional session ID, and progress path when enabled in `RUN.md`. Reconcile runtime liveness using the existing run-state rules; a progress record is evidence of a report, not proof that a runtime is live. Keep unknown mappings and unknown liveness visible.

## Start and update

If the recorded dashboard command resolves inside a legacy `coordinate-work/assets` or `coordinate-work/scripts` directory, preserve that installed directory and process for the current run. Do not install or migrate dashboard software during coordination. Defer migration until the run is paused or complete and the user explicitly requests maintenance. During that explicit maintenance, verify the recorded PID and start identity, stop the legacy server and worker, confirm both exited, then replace the skill installation and install the standalone application outside `skills/`. Never delete or overwrite a live legacy server's files in place.

Start the server only when all of these are true: the run is active and local, `workflow-dashboard` is available, local process retention is available, and the coordinator owns the run. Bind only to `127.0.0.1`; let the CLI select a free port unless a documented local port is required. The external command starts a long-lived Bun server process. That server owns a persistent Python snapshot worker, refreshes telemetry in the background every 30 seconds without overlapping refreshes, and serves the last completed snapshot immediately. The coordinator and dashboard server are separate processes.

```text
workflow-dashboard serve <workflow> \
  --host 127.0.0.1 --port 0 [--sessions-root <local-codex-sessions>] \
  [--claude-sessions-root <local-claude-projects>] \
  [--capacity <runtime-capacity>]
```

Capture the URL and process identity returned by the command. In `RUN.md`, record the resolved executable and command, owner runtime, PID plus a start-time or equivalent identity check, bind host and port, URL, start time, and `running` state. Give the user the localhost URL. Do not start a second server when a recorded owned process is still live; first reconcile its identity. If the executable is absent or startup fails, record the precise visibility reason once, omit dashboard heartbeats, and continue coordination without the dashboard.

Update progress records at meaningful milestones and update the compact `RUN.md` mapping and event log when coordination facts change. Leave recurring telemetry samples in the dashboard; a changed token count alone does not require a `RUN.md` write. The server refreshes its own read-only projection. HTTP requests never scan session files; they read the last completed in-memory snapshot. The persistent worker incrementally reads appended telemetry records and retains the last exact observation when a later read fails. Snapshot sequence changes only when a new snapshot is accepted, so three-second browser polls do not rerender unchanged data or trigger telemetry work.

The page is an executive snapshot. Its first strip shows completed tickets, active agents, and an attention count. The prominent `Working now` cards answer which ticket and stage is running, who owns it, which provider/model is observed or merely requested, whether activity is healthy, whether elapsed time is within the coordinator's estimate, exact available token use, the current milestone and next action, which direct dependents become dependency-ready after completion, and which only move closer because other dependencies remain. The compact ticket list shows every ticket's title, phase, number of review returns, and current context or token use; the agent list remains secondary context. Use human role labels such as `Coordinator`, `T-002 Implementer`, and `T-002 Reviewer`; canonical runtime paths stay in the data and audit records. Show blockers, stale activity, unexpected stops, and overdue stages in plain language. Never infer a model, context percentage, deadline, or ready-next relationship when the records do not prove it.

Keep summaries, next actions, health reasons, estimates, and compact token-use labels short enough to scan. Show only the exact latest input and cumulative session total on the page; keep the input/cache/output breakdown, resource leases, handoff paths, raw telemetry reasons, and historical agents out of the page.

Liveness, schedule, and context are independent signals. Liveness uses the freshest valid timestamp from progress, coordinator `heartbeat_at`, or exact runtime telemetry: `healthy` means a recent progress milestone, `quiet` means progress is old but a coordinator pulse or runtime telemetry is recent, `stale` means no signal is recent, `blocked` means an explicit blocker exists, and stopped work is distinguished as expected or unexpected against the ticket/run boundary. `last_progress_at` is always `updated_at`; `last_activity_at` is the newest of `updated_at`, `heartbeat_at`, and telemetry time. The default stale threshold is 600 seconds. Schedule is `not_estimated`, `on_schedule`, or `overdue` from `stage_started_at` plus the coordinator estimate. A worker can be healthy and overdue. Context pressure remains advisory and never replaces liveness.

A terminal coordinator progress record governs the run projection: older nonterminal worker records become historical, consume no active capacity, and raise no age alert. A ready ticket's lingering implementer or reviewer record is also historical. During an active run, progress age remains a coordinator diagnostic and never appears as the ticket or agent's user-facing phase. Count a ticket return only from a numbered review report whose decision is `revision_required`. Count completion only when a ready, available ticket has valid integration evidence. Do not manually copy dashboard cards or session content into progress records or `RUN.md`. The telemetry reader's prohibition on working-directory and Git metadata applies only to data read from session telemetry; the coordinator must still record independently observed checkout, branch, base, and reservation evidence required by [run state and recovery](run-state.md).

## Coordinator context compaction

Follow run-state's [transition checkpoints](run-state.md#transition-checkpoints); use its compact current state without creating an immutable pause manifest for ordinary compaction. When the runtime reports context pressure or performs compaction, preserve active checks and record or follow the existing dashboard-process tuple: resolved executable and command, PID, start identity, bind host/port, URL, and owner runtime. The same coordinator keeps the coordinator lock, dashboard ownership, active workers, reservations, and authorization throughout runtime-managed compaction. The dashboard process continues unchanged.

After compaction, read the compact checkpoint, the compact current-state fields in `RUN.md`, changed or active ticket metadata, changed or active progress records, and current runtime evidence. Do not reload complete journals, historical tickets, or unchanged progress records. Reconcile active workers and the recorded dashboard-process tuple before dispatching. Record a compaction event and exact before/after observations when available. Continue as the same coordinator; temporarily unavailable telemetry remains `Not reported` under the rules below.

Never stop, pause, return, ask the user, or transfer the coordinator solely because of a token count, percentage, or context warning. If the runtime cannot compact or continue, preserve the checkpoint and exact failure, then use the normal run-state recovery rules. Keep the existing coordinator and dashboard ownership whenever the runtime remains viable.

## Status-only, pause, and completion

For a status-only request, inspect the existing `RUN.md`, ticket state, progress records, and an already-running dashboard or its snapshot. Do not start a server, create or rewrite a progress record, change assignments, or clean up a process merely to answer status.

For **pause/stop now**, follow the durable pause procedure first: enter `pausing`, stop new dispatch and lifecycle transitions, request role-specific checkpoints, interrupt only as authorized, and retain unknown workers and reservations. After deciding the pause outcome, write coordinator progress state `paused` or `blocked` and save the final read-only dashboard snapshot path in both `RUN.md` and the new immutable pause manifest. Then stop only the dashboard process whose recorded PID and start identity still match this coordinator's owned process. Mark the dashboard stopped, write terminal coordinator progress state `stopped` with the checkpoint path and first resume action, and update `RUN.md` before releasing ownership. Never kill a process based on port, name, or a stale PID alone.

For **continue/resume**, reconcile the pause manifest, `RUN.md`, canonical runtime handoffs, current progress records, runtime liveness, and the old dashboard-process tuple before starting a server. Safely inherit a live recorded process only through the coordinator-transfer procedure. Otherwise confirm the old process stopped before starting a new server and recording its new identity.

For **completion**, do not treat dashboard completion as ticket completion or feature verification. First satisfy the existing ticket, verification, and closure rules. Write only a final coordinator-owned completion progress record; preserve each stopped runtime's own terminal record unchanged, and never rewrite a worker, reviewer, child, or verifier progress record. Retain a final read-only snapshot path and record the completion event. Then stop only the verified owned dashboard process and mark it stopped. If the process identity cannot be confirmed, leave it running, record the concern, and ask the user for direction rather than terminating a possibly unrelated process.

## Exact telemetry and smart context

The dashboard joins a progress runtime to telemetry by an explicit session ID first. Codex sessions may fall back to canonical agent path only when exactly one discovered session unambiguously matches that path; zero or multiple matches are unavailable telemetry. Claude sessions require the explicit session ID and are selected from the configured Claude projects roots. The adapters read only rollout/session and request identifiers, parent ancestry when reported, timestamps, model identity, context-window values, and exact token-count fields. Streaming Claude usage snapshots are deduplicated by request identity before totals are accumulated. From telemetry logs, the dashboard must not read, retain, display, or return conversation prompts, messages, summaries, instructions, tool arguments or outputs, working-directory or Git metadata, or authentication data.

When available, display exact current context from latest-call input as a percentage plus a compact used/window value. Latest-call context occupancy is latest-call input divided by the reported model context window. When exact latest input exists but the runtime does not report a context-window size, display the input count without a percentage. The page may also show the exact cumulative session total, clearly labeled and separate from current context; this total includes reported cached-input processing. The data layer retains the input/cache/output breakdown for validation or diagnostics, but the page does not show that breakdown. Cumulative totals may reset across resumes; they are never context occupancy and cannot trigger a context alert.

If a session cannot be found, cannot be joined, is missing token data, or contains malformed telemetry, show `Not reported`, use null current token fields, preserve a known session ID, and save the precise safe `unavailable_reason`. A prior exact observation may be shown only as explicitly stale history. Do not estimate, interpolate, expose raw log content, or infer that the runtime has failed. Missing telemetry never blocks safe ticket scheduling or recovery.

Use exact latest-call input only to display context occupancy and help runtimes keep the next read bounded. Record normal, warning, or critical display state relative to the runtime-reported context window rather than a fixed token boundary. At meaningful milestones, checkpoint enough focused state for verification and cleanup plus the next action. A parent with a delegation group asks the coordinator to adjust child capacity only when actual work, isolation, or continuity risk warrants it.

Context telemetry never controls lifecycle. Runtime-managed compaction retains the same coordinator or worker when safe. A runtime that truly cannot continue follows the normal stop, handoff, and singular-owner recovery rules. Never create a new worker, omit verification, or seek user approval solely to respond to context telemetry.
