---
name: coordinate-work
description: Use when the user explicitly asks to run, resume, pause, or inspect implementation and review of an existing local ticket set through one coordinating agent.
license: MIT
disable-model-invocation: true
---

# Coordinate work

Be the user's main contact for an existing ticket set. Assign focused implementation work, coordinate independent review, return required revisions, and maintain a resumable record. Do not implement the tickets yourself or claim that ticket review proves the whole feature is integrated, released, or verified end to end.

An explicit request to run this workflow authorizes its implementation and review assignments within the selected ticket set and stated limits. Whole-feature verification is included only when the user's request includes that stage; a request limited to completing tickets ends at ticket review. A status question authorizes inspection only. Do not begin execution while answering a status question or treat a resume request as permission to expand scope.

## Establish the run

Required reference: read this collection's [external workspace contract](../setup-workflow/references/workspace.md). Locate the installed setup-workflow companion if the sibling path is absent; do not install it silently. Resolve the selected project, external context, and active workflow from its registry and task identity. The user need not supply directory paths. Read the external CONTEXT.md and applicable repository instructions or user-maintained context. Keep their scopes explicit. Missing context alone does not block safe work; inaccessible required guidance needs its own blocker. Do not execute normal stages in closing or completed workflows. Resolve their markers before ticket validation: a closing workflow may resume only the required closure contract; a completed workflow returns its receipt without dispatch or spec reconstruction.

Resolve WORKFLOW.md and its ticket directory and code target. Read applicable project instructions, the ticket `INDEX.md`, ticket metadata, and `<workflow>/RUN.md`. Read ticket bodies and linked spec sections when selecting work or resolving a conflict. Do not load the full ticket set's code, transcripts, or review logs into this context.

Before dispatch, locate this collection's [implement-ticket](../implement-ticket/SKILL.md), [tdd](../tdd/SKILL.md), [review-ticket](../review-ticket/SKILL.md), and [ticket format](../spec-to-tickets/references/ticket-format.md) plus its validator. Read the format and the implementation and review entrypoints. Each worker reads its own skill and required references. Locate installed companions from this collection if sibling paths are absent. Report missing dependencies; do not silently install or substitute skills.

Read [run state and recovery](references/run-state.md) before claiming ownership or changing files. Read [workspaces and scheduling](references/scheduling.md) before assigning work. Use runtime subagent tools, not new user-owned conversations, unless the user requests those. Do not create background automations as an implied part of this skill.

For every active local coordination run, also read [dashboard visibility and context policy](references/dashboard.md). It defines the optional local, read-only dashboard, meaningful progress updates, exact-telemetry handling, and fresh-context continuation. The dashboard is a projection: it does not replace ticket files, `RUN.md`, runtime reconciliation, or this skill's authorization and recovery rules.

Preserve explicit user limits. Otherwise use one ticket owner at a time in the supplied checkout, followed by its review. When that ticket contains independently observable packages with disjoint leases and isolated resources, register a delegation group that fills the safely available runtime slots without creating a second ticket owner. A requested concurrency limit is a ceiling, not a target; if the user limits all implementation runtimes rather than ticket owners, delegated children count toward it. For parallel ticket ownership in a Git project, create or assign one exclusive worktree per concurrent ticket owner before dispatch. You own workspace allocation, verified bases, test-resource reservations, and later ownership transfers. Workers do not choose another checkout. Follow the scheduling reference for isolation, capacity, and the agreed integration plan. Explain these defaults briefly; no routine approval gate is needed.

Record the ticket set, current spec digest, coordinator identity, limits, workspace policy, integration authority, and stop conditions in `RUN.md`. Do not infer permission to commit, merge, cherry-pick, push, deploy, or overwrite user changes. If progress needs such an action, state the precise blocker and ask for direction. Continue independent safe work only when ownership and scheduling checks permit it.

Run `python3 <spec-to-tickets-directory>/scripts/validate_tickets.py <ticket-directory>`. Reconcile stale state using runtime and file evidence. Do not dispatch new work while structural or ownership errors remain. A valid graph is necessary, not sufficient: the script cannot prove agent liveness, review freshness, or checkout availability.

## Run the loop

Repeat while the run is active:

1. Reconcile new worker results and user instructions. Save accepted state changes before selecting more work.
2. Route an `implemented` ticket into review once its writer is stopped and its target is stable. Resume blocked reviews only when their missing condition changes.
3. Select eligible revision work or pending tickets within the workspace, resource, and runtime limits. Recheck dependencies immediately before dispatch. Prefer work that resolves blockers; do not starve independent tickets by repeating a stalled revision.
4. Record a unique assignment ID, attempt, checkout, and dispatch intent. Set that ticket's `assignee` and `in_progress` before sending its implementation task. Record the returned runtime ID separately. Follow the recovery rules if dispatch fails or its outcome is unknown.
5. While workers run, perform useful coordination checks. Otherwise use the runtime's event-based wait mechanism. A wait timeout is not proof of failure. Keep updates concise: completed outcomes, active work, next step, and blockers.

Every implementation, revision, reviewer, and verifier assignment prompt contains the canonical ticket or verification path when applicable; assigned checkout and base; branch or detached state; assignment ID; reserved test/output resources; applicable skill paths; constraints; expected handoff; and the assignment's coordinator-owned `child_capacity` (zero unless a delegation group is registered). It also contains the [dashboard reference](references/dashboard.md), the runtime's canonical agent path, canonical parent agent path, actual assigned progress-record path under `<workflow>/progress/`, and this populated heartbeat contract:

```text
python3 <coordinate-work>/scripts/workflow_dashboard.py heartbeat <workflow> \
  --agent-path <assigned-canonical-agent-path> --parent <assigned-canonical-parent-path> \
  --role <assigned-role> --stage <assigned-stage> --state <current-state> \
  --summary <short-meaningful-summary> --next-action <next-action> \
  [--ticket <ticket-id>] [--session-id <runtime-session-id>] \
  [--blocker <blocker>] [--file-lease <path>]
```

Require the runtime to write at assignment acceptance and every meaningful milestone from the dashboard reference, never as an unchanged liveness pulse. Before dispatch, create its runtime-map and progress-path entry in `RUN.md`; after dispatch, add the returned runtime ID without inventing one. For revisions, add the review report and accepted required finding IDs. The child reads these files as part of the user's explicit workflow request; this does not enable implicit skill selection. It must not create another worktree, switch branches, claim more tickets, run its own review, or update the index.

Give new tickets fresh, focused implementation contexts. For a revision, resume the original implementer when it is reachable, has stopped writing, and still has useful focused context. Otherwise confirm it cannot write, record reassignment, and give a replacement the saved artifacts. The approximate 200k context size remains a ticket-planning guide, not a token target or permission to omit work.

## Coordinate review and revisions

For review, read and follow `review-ticket` and its required references. Act as its parent coordinator in this same context; launch its two independent reviewer agents. Do not create a second state-writing coordinator. Reserve runtime capacity and a stable test target for both roles. Give each reviewer the dashboard-reference and populated heartbeat contract required for every assignment prompt. Do not replace an independent reviewer with the implementer or your own inspection.

The review stage's stop-after-one-ticket rule ends that stage. Control then returns to this authorized coordination loop. Reviewers and ordinary workers cannot dispatch further implementation. The only worker exception is a ticket owner dispatching already registered children within its current `child_capacity` and exact delegation-group contract.

Inspect actual implementation records, target identities, reviewer evidence, and required check results. A worker's final message is a signal to inspect, not completion proof. Respect the review outcomes: `ready`, `revision_required`, or blocked `in_review`. Do not mark work ready to clear a queue.

Return accepted required corrections through `implement-ticket`. Keep optional polish optional. If the same finding survives a fix attempt, obtain a concrete diagnosis or missing decision before retrying. Record each round and the change in approach. Do not repeat unchanged failing assignments indefinitely.

Verify availability in each proposed consumer's actual base before dispatch. Clear stale availability claims. Preserve dependency edges and completed ticket files. Refresh `INDEX.md` after lifecycle changes; it is a derived summary, not an assignment lock.

## Pause, resume, and finish

Apply the control and recovery rules in [run state and recovery](references/run-state.md). On resume, reconcile live agents and workspaces before dispatching anything. Missing runtime access means unknown state, not an abandoned worker.

When every non-superseded ticket is `ready`, report ticket review completion. Separately list unavailable implementations and final verification still needed. Follow [the feature-verification handoff](references/feature-verification.md): dispatch verify-feature in a fresh context only when requested, installed, and given a stable combined target. Otherwise return its exact invocation inputs as the next step. Do not equate ready tickets with a verified feature.

After a current final-verification pass in a run that includes that stage, read and follow the required [closure and spec-deletion contract](../setup-workflow/references/close-workflow.md). You own closure, not the verifier. Check all closure gates, write the closing journal before deleting exact registered specs, then save the completion receipt and index state. Do not call the workflow complete while deletion or its state updates are unfinished. Ticket-only, failed, paused, and blocked runs retain their specs. A status request performs no cleanup.

If no eligible action remains, distinguish waiting for live work from a real blocker. Wait for live work within the active run. If progress requires unavailable access, new authority, or a material decision, save a resumable checkpoint and return the blocker. Name any workers still active; never imply they stopped when they have not.

Return the ticket directory and `RUN.md` path, completed and active counts, revision or review blockers, implementation locations, and the next action. Use short sentences, active voice, and consistent terms based on STE principles. Do not claim formal ASD-STE100 compliance.
