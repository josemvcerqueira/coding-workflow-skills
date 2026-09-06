---
name: coordinate-work
description: Use when the user explicitly asks to run, continue, resume, pause, or inspect implementation and review of an existing local ticket set through one coordinating agent.
license: MIT
disable-model-invocation: true
---

# Coordinate work

Be the user's single contact for an existing ticket set. Assign implementation, arrange independent review, return required revisions, and keep a resumable record. Do not implement tickets yourself. Ticket review does not prove integration, release, or whole-feature verification.

An execution request authorizes implementation and review within the selected ticket set and saved limits. Include whole-feature verification only when requested. A status request is read-only. Continue and resume preserve the recorded scope and authority; they do not expand it.

Treat run, continue, and resume as one persistent terminal objective. Follow [task goal and turn continuity](references/run-state.md#task-goal-and-turn-continuity): `RUN.md` drives persistence; use a task-level goal only when its tool contract authorizes it. A status-only inspection creates no goal.

## Load only what the current stage needs

Resolve the project and canonical workflow through the [external workspace contract](../setup-workflow/references/workspace.md). Read external `CONTEXT.md`, applicable repository instructions, `WORKFLOW.md`, the ticket index, active ticket metadata, and the compact current state in `RUN.md`. Do not load the full backlog, journals, transcripts, review history, or codebase.

Read [run state and recovery](references/run-state.md) before ownership or mutation. Before allocation or dispatch, read only the relevant sections of [workspaces and scheduling](references/scheduling.md): serial workspace, resources, capacity, and handoff are core; parallel worktrees, delegation groups, availability, and integration are conditional on using those paths. Read [durable pause and resume](references/pause-resume.md) only for those controls. Read [feature verification](references/feature-verification.md) only when entering or reporting that requested stage.

Resolve dashboard availability before reading its full contract by checking the recorded run state and resolving `workflow-dashboard` once from `PATH`. When the executable is absent and no dashboard process is recorded, note that once and do not load the dashboard reference. When it is available, running, stale, or being paused, read [dashboard visibility and context policy](references/dashboard.md) for that action.

Locate the companion `implement-ticket`, `tdd`, `review-ticket`, ticket validator, and ticket-format contract before first use. Do not preload worker entrypoints or review references: give workers their resolved skill paths, and read `review-ticket` when review begins. Report a missing required companion; do not silently install or substitute it.

Use the shared [handoff manifest](../setup-workflow/references/handoff-manifest.md). Allocate one exact path per implementation, review, integration, or verification assignment. Follow the manifest's recorded paths and source identity; never guess a handoff filename.

## Authority and boundaries

An explicit run request grants standing local execution authority for ordinary reversible work needed to finish the selected tickets. Record it once in `RUN.md`. It covers worker plans, worktrees and branches, code and workflow edits, repository-declared local dependencies, run-owned local processes and disposable data services, tests, browser checks, screenshots, local commits, and merge or cherry-pick of reviewed ticket commits into the selected local consumer. Do not ask the user again for these actions or create per-step approval artifacts.

This authority excludes credentials, paid services, external messages, pushes, pull requests, deployments, shared or production infrastructure, destructive handling of pre-existing data or user changes, history rewrites, and material product or scope decisions. Tool access is capability, not broader authority. Ask one focused question only when such an effect is necessary and no safe in-scope route remains; continue independent work when possible.

Every required user decision is a self-contained decision card, including a retry or final blocked response. Present, in order: each decision in plain language and why it blocks; the recommended option; its user-visible or operational consequence and material tradeoff; the affected tickets or stages; and the exact reply that approves the recommendation or supplies a replacement. Use internal gap or finding IDs only as secondary labels. When several decisions form one coherent package, number each decision under one approval question. Each request carries the complete card so the user can decide without recovering an earlier message.

Before first dispatch and after ticket or graph changes, validate the ticket directory with `validate_tickets.py`. Before each dispatch, reconcile current runtime and file evidence, confirm coordinator ownership, verify checkouts and resources, and save dispatch intent. Reuse unchanged structural validation; it does not prove liveness, review freshness, or checkout availability.

## Run the loop

Repeat while running:

1. Reconcile new user instructions, runtime results, handoffs, and physical workspace evidence. Save accepted state changes first.
2. Route a stable `implemented` ticket to review. Route findings through [healing and scope control](references/run-state.md#healing-and-scope-control), using the smallest sufficient repair and check scope.
3. Select eligible revisions or pending tickets within dependency, workspace, resource, and runtime limits. Prefer blocker-clearing work without starving independent tickets.
4. Record assignment ID, attempt, checkout, base, reservations, handoff path, progress path, and dispatch intent. Set `assignee` and `in_progress` before implementation dispatch; record the returned runtime ID separately.
5. Do useful coordination checks while workers run. Otherwise use the longest safe event wait. Keep the coordinator liveness pulse current around these waits when the dashboard is enabled. After an unchanged wait, do not re-read unchanged artifacts, rebuild status, or emit user-facing prose; pulse if due and wait again. A timeout is not failure.

### Final response gate

Apply the run-state final response gate before returning control. An owning execution task answers interjected status questions in commentary and returns to reconciliation, useful coordination, or an event wait. Dashboard startup, a milestone, a worker final message, context compaction, and a wait timeout are intermediate events.

Default to one ticket owner in the supplied checkout, followed by review. Parallel ticket owners require exclusive verified worktrees. A registered intra-ticket delegation group may use otherwise safe runtime capacity under scheduling's exact leases and resources. A concurrency limit is a ceiling, not a target. Use runtime subagents, not new user-owned tasks or background automations.

Assignment prompts contain pointers and the current delta, not copied documents. Use scheduling's [handoff shape](references/scheduling.md#handoff-shape) for identities, reservations, permitted writes, exact output paths, and revision evidence. The dashboard reference owns optional heartbeat fields and milestones.

## Review, integration, and completion

At review, follow `review-ticket` as its parent. Use one reviewer, independent of implementation, covering both axes by default; use two when its recorded risk rules require it. The coordinator decides. Freeze the target and reserve mutable test resources. A worker's final message is a signal to inspect evidence, not completion proof.

Respect `ready`, `revision_required`, and blocked `in_review` outcomes. Permit reviewer repair only through its explicit bounded contract and lease. Do not repeat an unchanged failed revision; obtain diagnosis or a missing decision.

Verify reviewed code in each selected consumer before marking `available`. After authorized integration, write the exact integration handoff and set `integration_ref`; availability alone is not integration evidence. Refresh the derived index after lifecycle changes. Before reopening an integrated ticket, preserve its former integration-manifest path in `RUN.md` or the review record, then clear `available` and set `integration_ref: null` in the same ticket update, before or with leaving `ready`. Publish renewed integration evidence only after review and consumer checks succeed.

For pause or resume, use the durable procedure and preserve unknown workers and reservations. When every non-superseded ticket is `ready`, report ticket-review completion separately from integration and final verification. Dispatch whole-feature verification only when requested and against a stable combined target. After a requested current pass, follow the setup-workflow closure contract; ticket-only, failed, paused, and blocked runs retain their specs.

## Context and reporting

Keep policy, live mappings, active blockers, current findings, and artifact pointers in coordinator context. Use targeted reads; raw evidence stays in files. Context telemetry is advisory. Save transition checkpoints under run-state; let the runtime manage compaction without interrupting active checks. After compaction, continue as the same coordinator with the same lock, dashboard, workers, reservations, and authority. Never stop, transfer, ask the user, or replace the coordinator solely because of token usage. If the runtime truly cannot continue, save an exact handoff and use normal ownership recovery.

Routine status reports contain only the ticket directory and `RUN.md`, completed and active counts, current phase, review returns or blockers, implementation locations, and next action. A required decision request uses the complete decision card above. Use short sentences and plain role names; omit runtime paths and technical telemetry unless requested.
