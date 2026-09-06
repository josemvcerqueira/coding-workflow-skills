# Workflow Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a token-free local workflow dashboard with exact Codex context telemetry and safe intra-ticket child delegation.

**Architecture:** A Python standard-library CLI owns progress-record writes, telemetry parsing, snapshot assembly, and localhost HTTP. A single HTML/CSS/JavaScript asset renders the read-only snapshot. Existing Markdown ticket and run artifacts remain authoritative.

**Tech Stack:** Python 3 standard library, `unittest`, HTML, CSS, browser JavaScript.

**Spec:** `docs/superpowers/specs/2026-09-05-workflow-dashboard-design.md`

## Global Constraints

- Add no third-party dependency, package manager, database, external service, or monitoring model.
- Bind the server to `127.0.0.1` by default and expose no workflow mutation endpoint.
- Read no session prompt, message, tool argument, tool output, or authentication content.
- Treat 160,000 latest-call input tokens as warning and 200,000 as critical.
- Show unavailable telemetry explicitly; never estimate tokens.
- Preserve one ticket owner and the existing lifecycle authority.
- Do not commit, merge, push, or publish; this task has file-edit authority only.

---

### Task 1: Progress and telemetry data layer

**Files:**

- Create: `skills/coordinate-work/scripts/workflow_dashboard.py`
- Create: `skills/coordinate-work/scripts/test_workflow_dashboard.py`

**Interfaces:**

- Produces `write_progress(workflow: Path, record: dict) -> Path` with atomic per-agent files under `progress/`.
- Produces `read_token_telemetry(path: Path) -> dict | None` using only `session_meta`, `turn_context`, and `event_msg.token_count` fields.
- Produces `build_snapshot(workflow: Path, session_roots: list[Path], now: datetime, stale_after: int, capacity: int | None) -> dict`.
- Snapshot keys: `generated_at`, `run`, `summary`, `tickets`, `agents`, `alerts`, and `telemetry_available`.

- [ ] Write failing `unittest` cases for valid/invalid ticket metadata, atomic progress writes, session discovery by session ID and agent path, latest token-event selection, missing/malformed JSONL, 160k/200k thresholds, agent ancestry, ticket token rollups, and lifecycle-gate progress.
- [ ] Run `python3 -m unittest skills/coordinate-work/scripts/test_workflow_dashboard.py -v`; verify failures identify missing functions.
- [ ] Implement the parser and snapshot functions with `json`, `pathlib`, `tempfile`, `datetime`, and no prompt-content reads.
- [ ] Add CLI subcommands:

```text
workflow_dashboard.py heartbeat WORKFLOW --agent-path PATH --role ROLE --stage STAGE --state STATE --summary TEXT --next-action TEXT [--parent PATH] [--ticket ID] [--session-id ID] [--blocker TEXT] [--file-lease PATH] [--reserved-test-resource ID]...
workflow_dashboard.py snapshot WORKFLOW [--sessions-root PATH] [--capacity N]
workflow_dashboard.py serve WORKFLOW [--sessions-root PATH] [--capacity N] [--host 127.0.0.1] [--port 0]
```

- [ ] Run the focused test module and confirm all data-layer cases pass.

### Task 2: Read-only browser surface and server

**Files:**

- Create: `skills/coordinate-work/assets/dashboard.html`
- Modify: `skills/coordinate-work/scripts/workflow_dashboard.py`
- Modify: `skills/coordinate-work/scripts/test_workflow_dashboard.py`

**Interfaces:**

- Consumes the Task 1 snapshot keys.
- Produces `GET /`, `GET /api/status`, and `GET /health`; every other method or path returns an error and performs no mutation.

- [ ] Write failing tests for the three allowed routes, rejected mutation methods, JSON content type, local default host, and required page labels.
- [ ] Run the focused tests and verify the server/page cases fail for missing behavior.
- [ ] Build one responsive working surface. First viewport: run summary, pipeline progress, active ticket cards, context warnings, and agent tree. Use semantic HTML, 16px body text, visible focus states, restrained green/amber/red status colors, and no animation.
- [ ] Implement the threaded local server and three-second browser polling. Escape all text before inserting it into the DOM.
- [ ] Run the focused tests and a temporary localhost smoke request for `/health`, `/`, and `/api/status`.

### Task 3: Coordinator visibility and context policy

**Files:**

- Modify: `skills/coordinate-work/SKILL.md`
- Modify: `skills/coordinate-work/references/run-state.md`
- Create: `skills/coordinate-work/references/dashboard.md`

**Interfaces:**

- Consumes the dashboard CLI from Tasks 1–2.
- Produces required run fields for dashboard URL/process, progress records, runtime ancestry, exact telemetry observations, smart-context alerts, and checkpoint/continuation actions.

- [ ] Preserve the baseline evidence that the old skill emits Markdown only and has no telemetry, ancestry, heartbeat, or dashboard contract.
- [ ] Add a short entrypoint pointer requiring `references/dashboard.md` for active local coordination runs.
- [ ] Define start, update, status-only, pause, completion, unavailable-telemetry, and owned-process cleanup behavior in the reference.
- [ ] Update `RUN.md` requirements with dashboard process identity, agent-parent mappings, progress paths, telemetry observations, and context-pressure actions.
- [ ] Require a warning response at 160k and checkpoint/fresh-context continuation at 200k without treating cumulative token use as context occupancy.

### Task 4: Controlled intra-ticket delegation

**Files:**

- Modify: `skills/implement-ticket/SKILL.md`
- Modify: `skills/tdd/SKILL.md`
- Modify: `skills/coordinate-work/references/scheduling.md`
- Create: `skills/implement-ticket/references/delegation.md`

**Interfaces:**

- Consumes coordinator-recorded `child_capacity`, checkout, file leases, interface contracts, and isolated test resources.
- Produces registered child progress records and child handoffs; the parent alone produces ticket lifecycle changes and the final implementation record.

- [ ] Preserve the baseline evidence that current instructions require one agent/context and have no child ownership, resource, recovery, or review-freeze model.
- [ ] Add a conditional delegation pointer to `implement-ticket`: read the new reference only when the coordinator grants child capacity and independent work exists.
- [ ] Define independence by observable behavior/contract rather than filename alone.
- [ ] Define same-checkout delegation groups with non-overlapping file leases, no child Git state changes, isolated mutable test resources, parent write exclusion, and overlap stop/recovery.
- [ ] Require child-local TDD evidence, parent integration checks, registered ancestry/liveness, and all-child shutdown before review.
- [ ] Limit depth to one and make runtime capacity a coordinator-owned ceiling.
- [ ] Define 160k checkpoint preparation and 200k stop-and-continue behavior.

### Task 5: Documentation and complete verification

**Files:**

- Modify: `README.md`
- Verify all files from Tasks 1–4.

**Interfaces:**

- Documents the dashboard command, exact-versus-cumulative telemetry, smart-context boundary, and controlled delegation behavior.

- [ ] Add a concise dashboard section to the workflow usage documentation.
- [ ] Run `python3 -m unittest discover -s skills -p 'test_*.py' -v`.
- [ ] Run `python3 skills/spec-to-tickets/scripts/test_validate_tickets.py`.
- [ ] Run the available Agent Skills validator against each changed skill folder.
- [ ] Start the dashboard against a temporary representative workflow and confirm the rendered page loads with active, blocked, warning, and unavailable states.
- [ ] Run a fresh-context behavioral check of the changed coordinator and implementer instructions. Confirm exact-only telemetry, singular ticket ownership, bounded child depth, file/resource isolation, and fresh-context continuation at 200k.
- [ ] Inspect `git diff --check` and the final scoped diff. Leave all changes uncommitted.
