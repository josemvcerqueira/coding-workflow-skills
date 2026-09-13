---
name: thin-coordinator
description: Use when the user explicitly asks to run, continue, resume, or pause an existing local ticket workflow whose dependent assignments, shared resources, or independent reviews need coordination.
license: MIT
disable-model-invocation: true
---

# Thin coordinator

Optimize safe time to the next accepted release point. Agent utilization, artifact count, and narration are not progress. Own workflow state, scheduling, and handoffs; leave source changes and detailed investigation to assigned workers. Ticket review does not prove integration, release, or whole-feature verification.

An execution request authorizes implementation and review within the selected ticket set and saved limits. Include whole-feature verification only when requested. A status request is read-only. Continue and resume preserve the recorded scope and authority; they do not expand it.

Use coordination when three or more dependent assignments cross stage boundaries, workers contend for
mutable resources, or a run needs durable pause/resume. A single bounded source correction stays with
one implementer followed by one independent reviewer; a read-only status check acquires no workflow
ownership.

Treat run, continue, and resume as one persistent terminal objective. Follow [task goal and turn continuity](references/run-state.md#task-goal-and-turn-continuity): `RUN.md` drives persistence; use a task-level goal only when its tool contract authorizes it. A status-only inspection creates no goal.

## Load only what the current stage needs

Resolve the project and canonical workflow through the [external workspace contract](../setup-workflow/references/workspace.md). Read external `CONTEXT.md`, applicable repository instructions, `WORKFLOW.md`, the ticket index, compact `RUN.md`, and only tickets at the next release edge. Follow current handoff pointers for detail; do not load the full backlog, journals, transcripts, historical reviews, or codebase.

Read [run state and recovery](references/run-state.md) before ownership or mutation. Before allocation or dispatch, read only the relevant sections of [workspaces and scheduling](references/scheduling.md): serial workspace, resources, capacity, and handoff are core; component batches, database snapshots, same-lane review, parallel worktrees, delegation groups, availability, and integration are conditional on using those paths. Read [durable pause and resume](references/pause-resume.md) only for those controls. Read [feature verification](references/feature-verification.md) only when entering or reporting that requested stage.

Use the dashboard only when the user or workflow requires it or `RUN.md` already records one. Then resolve `workflow-dashboard` once and read [dashboard visibility and context policy](references/dashboard.md). Do not start a dashboard solely for coordination.

Locate the companion `implement-ticket`, `tdd`, `review-ticket`, [systematic-debugging](../systematic-debugging/SKILL.md), ticket validator, and ticket-format contract before first use. Do not preload worker entrypoints or review references: give workers their resolved skill paths, and read `review-ticket` when review begins. Systematic debugging is loaded only for an unexplained failure or failed correction. Report a missing required companion; do not silently install or substitute it.

Use the shared [handoff manifest](../setup-workflow/references/handoff-manifest.md). Allocate one exact path per implementation, review, integration, or verification assignment. Follow the manifest's recorded paths and source identity; never guess a handoff filename.

## Authority and boundaries

An explicit run request grants standing local execution authority for ordinary reversible work needed to finish the selected tickets. Record it once in `RUN.md`. It covers worker plans, worktrees and branches, code and workflow edits, repository-declared local dependencies, run-owned local processes and disposable data services, tests, browser checks, screenshots, local commits, and merge or cherry-pick of reviewed ticket commits into the selected local consumer. Do not ask the user again for these actions or create per-step approval artifacts.

This authority excludes credentials, paid services, external messages, pushes, pull requests, deployments, shared or production infrastructure, destructive handling of pre-existing data or user changes, history rewrites, and material product or scope decisions. Tool access is capability, not broader authority. Ask one focused question only when such an effect is necessary and no safe in-scope route remains; continue independent work when possible.

Before asking the user, recheck the standing authority recorded in `RUN.md`. When it covers the local correction, checks, cleanup, and required review, take the next action without another approval gate. A genuinely required decision is one self-contained natural-language question: explain what is blocked, recommend an option, and state its material consequence. Use internal gap or finding IDs only as secondary labels. Include an exact approving reply only when wording is genuinely needed to avoid ambiguity. When several decisions form one coherent package, number them under one question so the user can decide without recovering an earlier message.

Before first dispatch and after ticket or graph changes, validate the ticket directory with `validate_tickets.py`. Before each dispatch, reconcile current runtime and file evidence, confirm coordinator ownership, verify checkouts and resources, and save dispatch intent. Reuse unchanged structural validation; it does not prove liveness, review freshness, or checkout availability.

## Run the loop

Repeat only on a user instruction, worker result, blocker, review verdict, or runtime-state change:

1. Reconcile the new fact once and persist one atomic transition. Apply [live instruction delivery](references/run-state.md#live-instruction-delivery) when an active worker's scope, retry permission, or stop boundary changes.
2. Select the smallest ready action on the measured release critical path through [dependency-based scheduling](references/scheduling.md#dependency-based-scheduling). Reviewed work awaiting integration outranks unrelated new implementation; avoid starving independent work.
3. Dispatch only work that can finish usefully before the next release point with disjoint source and mutable-resource ownership. Record assignment identity, checkout, reservations, handoff, and intent before launch, then record the real or unknown runtime result.
4. Route stable implementation to review and findings through [healing and scope control](references/run-state.md#healing-and-scope-control). Use the smallest sufficient repair and carry valid evidence under the shared check-scope contract.
5. While work runs, perform only pending integration, decision, cleanup, or readiness work that advances the release edge. Otherwise use the longest safe event wait. An unchanged wait causes no artifact reread, status rebuild, or user message; pulse only when a required dashboard is enabled.
6. Treat a worker final message as a signal to verify its handoff, stopped writers, source identity, checks, and cleanup. Advance exactly one lifecycle boundary.

### Final response gate

Apply the run-state final response gate before returning control. An owning execution task answers interjected status questions in commentary and returns to reconciliation, useful coordination, or an event wait. Dashboard startup, a milestone, a worker final message, context compaction, and a wait timeout are intermediate events.

Default to one ticket owner in the supplied checkout, followed by review. Parallel ticket owners require exclusive verified worktrees. A registered intra-ticket delegation group may use otherwise safe runtime capacity under scheduling's exact leases and resources. A concurrency limit is a ceiling, not a target. Use runtime subagents, not new user-owned tasks or background automations.

Assignment prompts contain pointers and the current delta, not copied documents. Use scheduling's [handoff shape](references/scheduling.md#handoff-shape) for identities, reservations, permitted writes, exact output paths, and revision evidence. The dashboard reference owns optional heartbeat fields and milestones.

## Review, integration, and completion

At review, follow `review-ticket` as its parent and apply its [monotonic closure contract](../review-ticket/references/closure.md). Freeze the complete first finding batch, apply one coherent correction, then use a delta-focused independent successor review. Use one reviewer covering both axes by default and two only when recorded risk requires it. The coordinator accepts dispositions and changes lifecycle; reviewers recommend them.

Respect `ready`, `revision_required`, and blocked `in_review` outcomes. Permit reviewer repair only through its explicit bounded contract and lease. Do not repeat an unchanged failed revision; route it through systematic debugging with the calling stage's existing authority, then assign the classified next action.

Verify reviewed code in each selected consumer before marking `available`. After authorized integration, write the exact integration handoff and set `integration_ref`; availability alone is not integration evidence. Refresh the derived index after lifecycle changes. Before reopening an integrated ticket, preserve its former integration-manifest path in `RUN.md` or the review record, then clear `available` and set `integration_ref: null` in the same ticket update, before or with leaving `ready`. Publish renewed integration evidence only after review and consumer checks succeed.

For pause or resume, use the durable procedure and preserve unknown workers and reservations. When every non-superseded ticket is `ready`, report ticket-review completion separately from integration and final verification. Dispatch whole-feature verification only when requested and against a stable combined target. After a requested current pass, follow the setup-workflow closure contract; ticket-only, failed, paused, and blocked runs retain their specs.

## Context and reporting

Keep only policy, live mappings, active blockers, current findings, and artifact pointers in context. Raw evidence stays in files. Let the runtime manage compaction; continue with the same ownership and authority afterward. If it truly cannot continue, save an exact handoff and use normal ownership recovery.

Send user-facing updates only for a changed critical path, a new blocker or genuine decision, an implementation or review result, integration, verification, pause, or completion. Default each update to no more than three short sentences: what happened in ordinary language; the concrete fix or result and why it matters; and what happens next, including whether the user must act. Translate workflow terms before reporting and keep ticket/finding IDs, hashes, paths, counts, and commands in the artifacts unless the user asks or needs one to distinguish the target. Compress relevant safety context to one sentence such as “Nothing external or shared was touched”; omit inventories of untouched systems and unchanged waiting state.
