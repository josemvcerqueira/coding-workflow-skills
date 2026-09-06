# Durable pause and resume

Use this procedure when the user asks to pause, stop, continue, or resume a coordination run. Dashboard snapshots, JSON progress writes, and dashboard process actions below apply only when the dashboard is enabled; otherwise record its absence once and follow the Markdown handoff and liveness procedure. A pause is a controlled workflow transition, not a conversation summary. Preserve enough external evidence for the same coordinator or a replacement coordinator to continue without relying on hidden model context or an old transcript.

## Artifact location

Keep pause artifacts in the canonical external workflow directory shared by every assignment:

```text
<workflow>/
  RUN.md
  checkpoints/
    CP-<UTC-basic-timestamp>/
      CHECKPOINT.md
      agents/
        A-001.md
  progress/
  tickets/
  reviews/
  verification/
```

Use a collision-resistant UTC basic timestamp such as `CP-20260906T142305Z`; add a short unique suffix if the path already exists. Reject symlinks and paths outside the selected workflow, and reject an existing checkpoint directory. Create a new directory for every pause attempt. Allocate one exact agent path such as `agents/A-001.md` for each active or uncertain runtime; map it to the stable assignment and runtime IDs in `RUN.md` before sending the pause request. Do not construct filenames from untrusted runtime labels. Each runtime writes its complete handoff atomically and at most once. After the coordinator finalizes `CHECKPOINT.md`, never revise that manifest or an existing agent handoff. An unknown runtime may create its previously missing assigned handoff once; treat it as later recovery evidence, not as a retroactive change to the manifest.

`RUN.md` remains the current coordination record. `CHECKPOINT.md` is an immutable point-in-time resume manifest, and `agents/*.md` are the runtimes' focused pause handoffs. Ticket files own ticket lifecycle and implementation records; review and verification directories own completed stage evidence; progress JSON owns compact runtime milestones. Product edits remain in the recorded code checkout or worktree. Do not copy source changes, full ticket bodies, test logs, secrets, or conversation transcripts into the checkpoint.

## Pause now

Treat `pause` or `stop` as pause now unless the user asks to finish active work first.

1. Record the user control event in `RUN.md`, set run mode to `pausing`, and stop all new dispatch, review, revision, verification, integration, and cleanup transitions.
2. Allocate the new checkpoint directory and one non-overlapping Markdown path for every active or uncertain implementer, delegated child, reviewer, and verifier. Record those paths in the runtime map. Deliver the cooperative checkpoint/stop revision through [live instruction delivery](run-state.md#live-instruction-delivery), naming the exact handoff path and next action. Use the runtime interruption mechanism when needed. An interruption request is not proof that the runtime or its mutating child processes stopped.
3. Reconcile runtime liveness, owned processes, checkout contents, test resources, and saved artifacts. Preserve partial edits. Keep uncertain workspaces, leases, capacity, and resources reserved.
4. Decide the pause outcome. Set run mode to `paused` only when every writer and owned mutating process is confirmed stopped and no stop outcome is unresolved. Otherwise set `blocked`, record that the requested target mode is `paused`, name each unknown or active runtime, retain its reservations, and report that the pause is incomplete.
5. Write coordinator progress state `paused` or `blocked` and obtain the final dashboard snapshot under the dashboard contract. Finalize `CHECKPOINT.md` with that snapshot path, update the current checkpoint pointer, digest, and pause outcome in `RUN.md`, then refresh `INDEX.md` only if its existing summary contract includes run mode.
6. Stop the verified coordinator-owned dashboard process as specified by the dashboard reference. Write terminal coordinator progress state `stopped` with the checkpoint path and first resume action, update `RUN.md`, and release only this coordinator's ownership after the checkpoint and run records agree. A lock release does not release a worker or resource.

For `finish active work, then pause`, set `draining`. Start no new ticket, revision, or feature-verification assignment. Let already active implementation or verification reach its normal handoff and let an already started review finish. Save resulting required revisions for resume. Then run steps 2 through 6 for anything still active or uncertain. Do not begin the next lifecycle unit merely to make the pause cleaner.

## Runtime checkpoint destinations

The coordinator assigns each runtime one exact `agents/*.md` path when pausing. The pause request makes that path a permitted external output for the assignment. No other runtime or the coordinator writes it.

- A ticket owner records the assignment, checkout/base, completed behavior or TDD boundary, changed paths, last focused and full checks with outcomes, owned process/resource state, blockers, and exact next action. It keeps an incomplete ticket `in_progress`; the pause artifact does not mark it implemented.
- A delegated child records the same facts plus its lease, preserved contract, parent integration need, and existing registered child-handoff pointer. It does not update the ticket, `RUN.md`, or another lease.
- A reviewer records current target identity, completed axes or checks, provisional findings, owned process/resource state, and exact next action. This runtime checkpoint is not the parent-owned review report or a verdict and does not advance ticket lifecycle.
- A verifier records completed criterion coverage, evidence pointers, current target identity, owned process/resource state, cleanup state, and exact next action. This runtime checkpoint is not a verification pass or failure.
- Every runtime writes progress state `checkpointed` after saving its Markdown handoff, then cleans up its owned mutating processes and updates that progress record to `stopped` as its final runtime-side action before exit. The final record retains a concise summary and exact next action. Progress state is a dashboard signal, not the detailed handoff or independent proof of stopped liveness.

If a runtime cannot write its checkpoint, the coordinator records that gap and preserves its checkout and resources as uncertain. The coordinator may record independently observed file and process state, but it must not invent the runtime's reasoning, completed checks, or intended next action.

## Checkpoint manifest

The checkpoint must be compact, concrete, and sufficient to orient a fresh coordinator. Include:

- Checkpoint ID, creation time, run ID, pause command, pause outcome (`paused` or `incomplete`), coordinator identity, and prior run mode.
- Canonical PROJECT.md, CONTEXT.md, WORKFLOW.md, RUN.md, ticket directory, spec path and observed digest, agreed code target, and dashboard snapshot path when available.
- The last completed coordinator transition and the first exact resume action. Add a short ordered queue only when more than one already determined action is needed.
- One row for every active, stopped, or uncertain assignment: role, ticket/stage, assignment and runtime IDs, checkout/base, lifecycle state, liveness/stop evidence, assigned checkpoint handoff path and SHA-256 when present, canonical stage-handoff path when one exists, progress path, blocker, and next action.
- Each retained workspace, file lease, integration claim, and test/output resource with owner, current state, and release condition. Link an existing dirty-content manifest or list the independently observed changed paths when no manifest exists.
- Current review and verification targets and artifact paths; required findings or incomplete criteria; last relevant check command, result, and evidence pointer. Link detailed logs instead of copying them.
- Preserved user scope, limits, stop conditions, final-verification choice, and explicit integration or external-mutation authority. Record missing decisions without manufacturing permission.
- Resume gates: unknown liveness to resolve, identities or digests to recheck, cleanup to confirm, blockers whose condition must change, and any action that still needs user authority.

Use `None` for an empty field and `Unknown — <reason>` for unavailable evidence. Never convert unknown state into a clean stop. Finalize the manifest only after collecting available runtime handoffs and independently observed stop evidence. Save its path and digest in `RUN.md` and append the pause outcome to the event log.

Use this compact manifest shape:

```markdown
# Pause checkpoint <checkpoint-id>

## Pause outcome
Run, command, requested target, outcome, coordinator, created time, and prior mode.

## Workflow identity
Canonical workflow records, spec digest, agreed code target, and dashboard snapshot.

## Resume position
Last completed transition, first resume action, and any already determined follow-up queue.

## Assignment handoffs
One row per assignment with identity, target, liveness evidence, checkpoint and canonical handoff paths, blocker, and next action.

## Retained workspaces and resources
One row per checkout, lease, integration claim, or test/output resource with owner, state, and release condition.

## Evidence and incomplete stages
Review/verification targets, required findings or incomplete criteria, and last check evidence pointers.

## Preserved controls
Scope, limits, stop conditions, verification choice, and explicit authority.

## Resume gates
Conditions to reconcile before affected mutation, or `None`.
```

Each runtime handoff uses headings for identity and target, completed boundary, changed or produced paths, checks and evidence, processes and resources, blockers, and exact next action. A role can mark a heading `Not applicable`; it must not omit an applicable unknown.

## Continue or resume

Treat `continue` and `resume` as the same control. They authorize continuation only within the saved workflow scope, stages, limits, and permissions.

1. Resolve the workflow from the registry and task identity. Read `WORKFLOW.md`, `RUN.md`, its current checkpoint pointer, the checkpoint manifest, and the linked canonical agent artifacts. The user does not need to repeat paths or prior decisions.
2. Establish coordinator ownership through the normal recovery rules. Reconcile runtime state before replacing or reactivating an assignment. A reachable stopped runtime with useful focused context may continue; otherwise give a replacement the canonical checkpoint and handoff paths. Never leave two live owners for one ticket.
3. Verify the recorded spec and code-target identities, worktree contents, dirty paths, ticket state, review or verification target, reservations, processes, and blockers against current evidence. Preserve later valid changes. Record contradictions and resolve them before affected dispatch.
4. Restart or safely inherit the optional dashboard under its process-identity rules. Write the coordinator progress state and a resume event naming the consumed checkpoint.
5. Set run mode to `running` only after reconciliation succeeds. Execute the checkpoint's first resume action, or report the exact blocker if a resume gate remains closed. Do not reset tickets, discard partial files, recreate worktrees, release uncertain resources, or repeat completed work as a shortcut.

The checkpoint accelerates recovery; it does not override newer authoritative files or live runtime evidence. When they disagree, preserve both observations in `RUN.md` and reconcile the physical state before mutation.

If the coordinator task or connection disappears before a delivered pause command can finish, use the ordinary interruption recovery rules. `RUN.md`, ticket state, progress records, and physical worktrees remain the evidence; do not manufacture a clean pause manifest after the fact.
