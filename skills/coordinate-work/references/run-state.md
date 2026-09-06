# Run state and recovery

Keep one canonical ticket directory, even when code is in several worktrees. Ticket files own requirements and lifecycle state. `INDEX.md` summarizes them. `<workflow>/RUN.md` owns coordination policy, dispatch history, and runtime/workspace mappings. Do not duplicate ticket bodies or test logs in the run record.

## Single coordinator

Before mutation, obtain exclusive coordinator ownership. Use an existing project coordination mechanism if available. Otherwise atomically create `<ticket-directory>/.coordinate-lock/` with the host's filesystem tools, such as `mkdir` without `-p`. If it already exists, do not treat that as success.

Inside the acquired directory, save `OWNER.md` with the run ID, coordinator runtime identity and host, and acquisition time. Record the same owner in `RUN.md`. Only this owner updates the run record and index. An implementer owns its assigned ticket's implementation fields while writing. The coordinator waits for that writer to stop before changing those fields or entering review. Reviewer children do not write ticket state.

An ownership directory is not a time-based lease. Inspect its owner and runtime before takeover. Age, an empty owner file, a timeout, or missing API access does not prove abandonment. If ownership cannot be established, stop mutation and ask the user to resolve it. Do not remove a competing owner's lock.

After confirming the old coordinator stopped, an authorized resuming coordinator may move its old lock directory to a unique history path inside the ticket directory, then attempt atomic acquisition again. A failed acquisition means another owner won; stop. Preserve existing work and dispatch records during takeover.

Release only your own ownership directory after saving a consistent checkpoint. Prefer moving it to a unique history path; do not recursively delete user data. Release means the coordinator stopped writing, not that its child agents stopped. A later coordinator must still reconcile every child. If you cannot confirm ownership, leave the lock intact and report the issue.

## Task goal and turn continuity

Use `RUN.md` to pursue an explicit run, continue, or resume through its requested terminal boundary. When goal tools are available, `get_goal` may identify an existing compatible goal. Call `create_goal` only when the user explicitly requested a goal or a higher-priority instruction authorizes it, and no unfinished goal exists; a coordination request alone does not imply goal creation. When authorized, use exactly one workflow-level goal and add no token budget unless explicitly requested. Preserve an unrelated unfinished goal and follow the tool's conflict rules. A status-only inspection creates no goal. Execution persists without a goal tool; `RUN.md` remains the durable cross-runtime authority.

Apply a final response gate only in the task that owns the execution objective. While its goal is unfinished or its owned `RUN.md` is `running`, `draining`, `pausing`, or `closing`, give requested status in commentary and continue the loop. The explicit exceptions are a durable user-requested pause and a genuine blocker requiring user input; either may return control with the goal unfinished. A separate read-only status inspector may answer normally and never assumes ownership. A dashboard URL, accepted milestone, worker final message, context compaction, or wait timeout is not a terminal boundary. For an existing compatible goal, call `update_goal` with `complete` only after the requested terminal boundary and all required evidence and cleanup exist. A requested pause leaves the goal unfinished for runtime-controlled pause/resume. Mark it `blocked` only when the goal tool's repeated-blocker rule is satisfied and no safe progress remains.

## RUN.md content

Keep a compact current-state section and append meaningful events. Update only changed fields; batch related observations into one transition write. Persist dispatch intent before the external action and its confirmed or unknown result immediately afterward. Refresh the derived index only for fields it summarizes. Telemetry samples, unchanged polls, and repeated status reads do not each produce journal entries. Include applicable fields below; dashboard and pause fields stay absent until used:

- Run ID; canonical project and ticket paths; spec path and observed digest; owner identity; last update.
- Run mode: `running`, `draining`, `pausing`, `paused`, `blocked`, `closing`, or `complete`. These are run modes, not new ticket statuses.
- User constraints; implementation concurrency ceiling; effective concurrency and reason; runtime capacity; workspace and test-resource policy.
- Integration policy: agreed selected local consumer and the standing local execution authority granted when the run starts. This includes local commits and integration of reviewed ticket commits into that consumer. Continue and resume preserve this recorded policy and every narrower saved limit; they do not expand it. Record any external or destructive action that remains outside the authority.
- Dashboard, when an active local run has one: resolved standalone executable, command and arguments, owner runtime, process ID and start identity, bound host and port, URL, start time, final-snapshot path when stopped, and current process state. Record only a process that this coordinator started or safely inherited through the recorded coordinator-transfer procedure. Preserve the previous and new coordinator identities, verified old-owner stop, process identity check, transfer time, and transfer event. A dashboard URL is observational; it grants no workflow or process-control authority.
- Runtime map: each coordinator, implementer, delegated child, reviewer, and verifier's canonical agent path; parent agent path (or an explicit root marker); role; ticket and assignment when applicable; runtime ID and host; optional session ID; progress-record path; pause-handoff path when allocated; last observed liveness; and next action. This map is the dashboard ancestry join, not a replacement for dispatch and ownership evidence.
- Assignment table: ticket link, stable assignment ID, attempt number, stage, canonical agent path, runtime ID and host, code checkout, baseline/target, progress-record path, allocated handoff-manifest path, last observed runtime state, and next action. Reconciliation follows that manifest's exact source identity and report paths.
- Workspace reservations: physical checkout path, repository identity, branch or detached state, exact base and prerequisite evidence, owner, and allocation/transfer/retention state. Link dirty-content manifests when applicable. Record actual database, port, test-suite capacity, and other test-resource identities, host, owner, permitted use, isolation or concurrency settings, and release conditions. Preserve unknown reservations until runtime and filesystem evidence resolve them.
- Active review roles and their runtime IDs; report paths; paused or uncertain workers; required decisions and retry conditions.
- Lifecycle evidence: keep `implemented`, `reviewed`, `integrated`, and `whole-feature verified` as four distinct gates. Record the source identity and handoff manifest that proves each reached gate. Set a ticket's relative `integration_ref` only after its integration manifest is written. Implementation does not imply review; review does not imply integration; integration does not imply whole-feature verification. Never use a ticket's `ready` or `available` value alone as proof of integration or whole-feature verification.
- Pause state: requested target mode, current immutable checkpoint path and digest, pause outcome, last completed coordinator transition, first exact resume action, and unresolved resume gates. Keep detailed point-in-time state in the linked checkpoint instead of accumulating it in the current-state section.
- Final verification policy (requested or not requested); verifier assignment/runtime and resource reservation; combined target/spec identities; report path and current outcome. Feature verification is separate from ticket status and requires its own freshness check.
- Telemetry: link the dashboard/progress observation when available. Copy exact values into an event only when they explain a coordination decision; recurring samples stay in telemetry storage. Keep context occupancy distinct from cumulative token usage, preserve unknown values, and never copy session content.
- Context-pressure actions: record exact telemetry when available, but treat it as advisory. Checkpoint at meaningful boundaries and before broad new reads when context pressure is high. Let the runtime manage compaction; after it compacts, the same coordinator re-reads the compact checkpoint and authoritative records and continues with its lock, dashboard, workers, reservations, and authorization intact. Never stop, transfer, replace, or ask the user solely because of token usage. If a runtime cannot continue, preserve its exact handoff and apply normal liveness, ownership, and reassignment rules. Cumulative usage remains a separate cost/churn signal and never controls lifecycle.
- Event log: dispatch intent/result, reassignment, review outcome, availability evidence, pauses, user policy changes, and completion. Link detailed records instead of copying them.

Example assignment row:

| Ticket | Assignment | Stage | Runtime | Checkout | Last observation | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| T-004.md | run-7:T-004:2 | implementation revision | host/agent-id | /project/worktree | running at recorded time | wait for implementation record |

Use real identifiers and paths, not these examples. The stable assignment ID can populate `assignee` before the runtime returns an agent ID. Pass that same ID to the worker. Do not invent a runtime ID.

For external workflows, record WORKFLOW.md and the closure policy. CLOSING.md and COMPLETED.md block new assignments before ticket validation. A closing workflow resumes only the spec-deletion recovery procedure. A completed workflow is read-only historical evidence; later work gets a new workflow. A ticket-only run may finish while WORKFLOW.md stays active with final verification still needed. Whole-workflow completion requires verified closure and deletion receipts.

## Dispatch and interruption

Save dispatch intent before calling the runtime. Once the call returns, record its actual outcome immediately.

- Confirmed start: save the runtime ID and observe that agent; do not start a duplicate.
- Confirmed failure before any worker started: record it. Restore a new unstarted assignment to pending, or a revision to revision_required, preserving its previous evidence. Clear only this failed assignment's reservation. Retry only after addressing the cause.
- Unknown outcome: retain the reservation and count it against capacity. Search the runtime by the saved ID or assignment label. Do not retry a potentially successful dispatch.

When resuming, compare the run journal, ticket files, runtime state, and workspace contents. Reconcile existing worktrees, branch/base identities, and test-resource reservations before allocation. Do not create a second workspace for an unresolved assignment. Recover missing journal entries from verifiable runtime results. Do not infer that a worker is active from `in_progress`, or infer it stopped from a missing ID.

If a worker is running, observe or reconnect. If it is confirmed stopped, inspect its partial edits and saved checks before resuming or reassigning. Require the replacement to preserve that work and verify the current target. If liveness is unknown, reserve its capacity and checkout. Continue only work proven isolated from it.

If a prerequisite becomes invalid or a shared contract changes, stop new affected assignments and ask affected active workers to checkpoint and stop. Confirm they stopped. Preserve ticket evidence and blockers; do not change statuses or erase edges merely to make the validator pass. Reconcile the affected graph before new dispatch.

## Healing and scope control

Classify a failure before assigning more work. Keep the finding, target, relevant check evidence, next action, and reason that action can make progress in the existing assignment record.

- **Mechanical rule violation:** use review-ticket's bounded reviewer repair when eligible. An advisory preference alone does not reopen a ticket.
- **Behavior defect:** return the accepted finding to the implementer with the failing scenario and affected contract. Prefer the same available worker and checkout when its focused context remains useful; preserve independent review afterward.
- **Environment or resource failure:** repair only owned, authorized resources, then retry the affected check after the condition changes. A missing service is not evidence for a product rewrite.
- **Oversized or mis-sliced ticket:** after the owner checkpoints and stops, route remaining work to spec-to-tickets. Preserve completed behavior, evidence, IDs, and graph history through its re-planning contract. Re-slice only when new evidence reveals separable observable outcomes or an excessive review/check surface; elapsed time alone does not justify splitting a coherent slice.
- **Repeated unchanged finding:** request a focused diagnosis with a new hypothesis and discriminating check before another revision. Continue isolated tickets while a real missing decision or dependency is resolved; avoid redispatching the same prompt against unchanged conditions.

Use the shared [check scope and evidence reuse](../../setup-workflow/references/check-scope.md) contract for revision, re-review, integration, and final verification. A small correction needs current proof for its impact; it does not reset unrelated passing evidence. The coordinator routes and reconciles these results, keeps ownership and integration safe, and writes lifecycle records; implementing code remains with assigned workers.

## Transition checkpoints

Use the compact current state in `RUN.md` as the routine checkpoint. Save the last completed transition, pending external action or result, evidence pointers, active owners/resources, and exact next action at dispatch, accepted handoff, review decision, integration, or blocker changes. Before a broad read or long command, make the current position durable and send verbose output to an evidence file. Reserve immutable pause manifests for user-requested pause/resume.

Context pressure is advisory: finish the bounded action and checkpoint at its next meaningful boundary. Keep in-flight tests, reviews, and live owners intact; do not restart a passing baseline or transfer a runtime to manufacture an empty context. If compaction occurs during a pending tool call, reconcile that call's existing runtime or process result before issuing it again. Recover through the same ownership rules only when the runtime truly cannot continue.

## User controls

For pause, stop, continue, or resume, read and follow [durable pause and resume](pause-resume.md). It defines the canonical artifacts, role-specific handoffs, clean-pause gate, and resume reconciliation procedure.

- **Status:** inspect and explain progress. Do not start a stopped run or change assignments.
- **Finish active work, then stop:** set draining. Start no new assignment or lifecycle unit. Existing implementation, review, or verification assignments may reach their normal handoff. Save implemented tickets, review outcomes, required revisions, and verification evidence for resume, then pause. Do not start a follow-on review, revision, or ticket merely to make the pause cleaner.
- **Pause/stop now:** enter `pausing`, stop new dispatch and lifecycle transitions, save role-specific checkpoints, and request active workers to stop. Preserve partial files. Set `paused` only after the durable checkpoint is complete and every writer and owned mutating process is confirmed stopped.
- **Continue/resume:** re-establish ownership, read the current pause checkpoint and linked handoffs, reconcile runtime and files, restore running mode, then execute its first resume action. Do not reset tickets to pending or rely on hidden conversation context as a shortcut.
- **Change scope or limits:** save the instruction. Lowering concurrency stops new dispatch until the run fits the ceiling; do not kill active work unless requested or unsafe. Material spec changes require reconciliation, not silent ticket rewriting.

Keep pauses and questions proportional. The coordinator holds standing local execution authority for the selected ticket set: do not ask for ordinary local assignments, checks, local commits, or integration into the selected local consumer. Ask one focused question, with a recommendation, only for a material product decision or an external, shared, credentialed, destructive, or otherwise unapproved effect.
