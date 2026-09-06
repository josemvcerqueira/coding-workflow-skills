# Dashboard visibility and context policy

## Scope and authority

This reference applies to an active local coordination run. Read it with [run state and recovery](run-state.md); that reference remains the source for coordinator ownership, dispatch recovery, pause controls, and safe takeover.

Baseline: before this contract, `coordinate-work` emitted Markdown status only. It had no dashboard process, progress-record, runtime-ancestry, heartbeat, or telemetry contract. This contract adds a local read-only projection; it does not change ticket ownership, lifecycle authority, scheduling, or user authorization.

Ticket files remain authoritative for requirements and lifecycle. `RUN.md` remains authoritative for coordination policy and history. The dashboard cannot mutate either, dispatch work, stop an agent, or confer authority to commit, integrate, or clean up resources.

## Required records

For an active local run, each runtime that is visible to the coordinator keeps one atomic JSON progress record under `<workflow>/progress/`, using the dashboard CLI. Required record fields are schema version, canonical `agent_path`, `parent_agent_path` (or an explicit root value), `role`, `stage`, `state`, `summary`, `started_at`, `updated_at`, and `next_action`. Include `ticket_id` for ticket work. Include the runtime `session_id`, blocker, file lease, and safe reserved-resource identifiers only when they are known and applicable. Keep the authoritative resource ownership and release conditions in the `RUN.md` runtime and reservation maps.

Use the CLI's progress interface:

```text
python3 <coordinate-work>/scripts/workflow_dashboard.py heartbeat <workflow> \
  --agent-path <canonical-agent-path> --role <role> --stage <stage> \
  --state <state> --summary <short-summary> --next-action <next-action> \
  [--parent <canonical-parent-path>] [--ticket <ticket-id>] \
  [--session-id <runtime-session-id>] [--blocker <blocker>] \
  [--file-lease <path>] [--reserved-test-resource <safe-resource-id>]...
```

Mirror only safe resource identifiers already registered in `RUN.md` through the repeatable `--reserved-test-resource` option; `RUN.md` remains authoritative for their ownership and release conditions. Write a record at meaningful changes only: assignment accepted, code or evidence located, failing test observed, implementation underway, checks running, blocked, checkpointed, or handoff complete. Do not send unchanged periodic heartbeats merely to appear active. A stale record means `Check recommended`, not that the runtime failed or stopped.

Before or immediately after dispatch, the coordinator records the same canonical agent path, parent path, role, ticket/assignment, runtime/host, optional session ID, and progress path in `RUN.md`. Reconcile runtime liveness using the existing run-state rules; a progress record is evidence of a report, not proof that a runtime is live. Keep unknown mappings and unknown liveness visible.

## Start and update

Start the server only when all of these are true: the run is active and local, Python and the dashboard CLI are available, local process retention is available, and the coordinator owns the run. Bind only to `127.0.0.1`; let the CLI select a free port unless a documented local port is required.

```text
python3 <coordinate-work>/scripts/workflow_dashboard.py serve <workflow> \
  --host 127.0.0.1 --port 0 [--sessions-root <local-codex-sessions>] \
  [--capacity <runtime-capacity>]
```

Capture the URL and process identity returned by the command. In `RUN.md`, record the script/command identity, owner runtime, PID plus a start-time or equivalent identity check, bind host and port, URL, start time, and `running` state. Give the user the localhost URL. Do not start a second server when a recorded owned process is still live; first reconcile its identity. A dashboard start failure is a visibility issue, not permission to stop or reassign workers. Record it and continue the coordination workflow without the dashboard.

Update progress records at meaningful milestones and update the compact `RUN.md` mapping, telemetry observation, and event log when facts change. The server refreshes its own read-only projection. Do not manually copy dashboard cards or session content into progress records or `RUN.md`. The telemetry reader's prohibition on working-directory and Git metadata applies only to data read from session telemetry; the coordinator must still record independently observed checkout, branch, base, and reservation evidence required by [run state and recovery](run-state.md).

## Coordinator fresh-context server transfer

When the coordinator reaches the critical context policy and must continue in a fresh context, it first writes a compact checkpoint and records the candidate dashboard-process tuple: script/command identity, PID, start identity, bind host/port, URL, and current owner runtime. The old coordinator stops writing and releases ownership only through the existing run-state procedure; it does not start another server or silently declare the process transferred.

The fresh coordinator first confirms that the old coordinator stopped, obtains the normal coordinator lock, and reconciles the recorded process tuple. If the same process is live with the same PID, start identity, command, and local bind, it records a dashboard ownership-transfer event with both coordinator identities and transfer time, changes the dashboard owner runtime in `RUN.md`, and continues to use that one server. The inherited, verified process is now eligible for cleanup by the new coordinator. Do not start a duplicate server.

If the old owner has not stopped, the lock cannot be acquired, or the process tuple cannot be verified, do not inherit or kill the process. Preserve the record as uncertain, continue only safe reconciliation permitted by the run-state rules, and ask the user to resolve a material ownership conflict. A fresh coordinator may start a new server only after the prior process is confirmed stopped or otherwise resolved and its own ownership is established.

## Status-only, pause, and completion

For a status-only request, inspect the existing `RUN.md`, ticket state, progress records, and an already-running dashboard or its snapshot. Do not start a server, create or rewrite a progress record, change assignments, or clean up a process merely to answer status.

For **pause/stop now**, follow the run-state stop procedure first: stop new dispatch, request checkpoints, interrupt only as authorized, and retain unknown workers and reservations. Write a final meaningful coordinator progress record and record the pause/unknown outcomes in `RUN.md`. Obtain a final read-only snapshot through the CLI and retain its path in the run record. After that checkpoint is consistent, stop only the dashboard process whose recorded PID and start identity still match this coordinator's owned process. Mark it stopped; never kill a process based on port, name, or a stale PID alone.

For **completion**, do not treat dashboard completion as ticket completion or feature verification. First satisfy the existing ticket, verification, and closure rules. Write only a final coordinator-owned completion progress record; preserve each stopped runtime's own terminal record unchanged, and never rewrite a worker, reviewer, child, or verifier progress record. Retain a final read-only snapshot path and record the completion event. Then stop only the verified owned dashboard process and mark it stopped. If the process identity cannot be confirmed, leave it running, record the concern, and ask the user for direction rather than terminating a possibly unrelated process.

## Exact telemetry and smart context

The dashboard joins a progress runtime to Codex telemetry by an explicit session ID first. Only when no explicit session ID is available may it fall back to canonical agent path, and then only when exactly one discovered session unambiguously matches that path; zero or multiple matches are unavailable telemetry. It reads only rollout/session identifiers, parent ancestry, timestamps, model identity, context-window values, and token-count fields. From telemetry logs, it must not read, retain, display, or return conversation prompts, messages, summaries, instructions, tool arguments or outputs, working-directory or Git metadata, or authentication data.

When available, record and display exact latest-call input separately from cumulative input, cached-input, output, reasoning-output, and total token fields. Latest-call context occupancy is latest-call input divided by the reported model context window. Cumulative totals may reset across resumes and are useful only as cost/churn information; they are never context occupancy and cannot trigger a context alert.

If a session cannot be found, cannot be joined, is missing token data, or contains malformed telemetry, show `Not reported`, use null token fields, and save an `unavailable_reason`. Do not estimate, interpolate, expose raw log content, or infer that the runtime has failed. Missing telemetry never blocks safe ticket scheduling or recovery.

Apply the smart-context policy only to exact latest-call input tokens:

- Below 160,000: record normal context state when an exact observation exists.
- 160,000 through 199,999: record a warning; prepare a compact checkpoint or split the next work, and update the progress next action. Keep work bounded and avoid loading broad new material into that context. An owner with an active delegation group checkpoints and asks the coordinator to preserve, reduce, or revoke child capacity; it does not decide capacity alone.
- 200,000 or more: record critical context state; checkpoint the coordinator or affected runtime, then stop further broad work in that context. A coordinator continuation receives the compact `RUN.md`, ticket/index state, current artifact pointers, runtime/workspace evidence, active blockers, and exact next action—not a large transcript—and follows the coordinator-transfer procedure above before dispatching. A worker continuation remains subordinate: after the old writer has stopped, the coordinator reconciles its ticket evidence and resumes or reassigns that ticket under singular coordinator ownership. A worker never takes over the coordinator lock or dashboard process.

The 200,000 policy boundary is not a model maximum, a completion shortcut, or permission to omit verification. It is also not a signal to create new workers as a substitute for a required fresh-context handoff.
