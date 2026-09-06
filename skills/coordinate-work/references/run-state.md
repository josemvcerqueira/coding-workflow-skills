# Run state and recovery

Keep one canonical ticket directory, even when code is in several worktrees. Ticket files own requirements and lifecycle state. `INDEX.md` summarizes them. `<workflow>/RUN.md` owns coordination policy, dispatch history, and runtime/workspace mappings. Do not duplicate ticket bodies or test logs in the run record.

## Single coordinator

Before mutation, obtain exclusive coordinator ownership. Use an existing project coordination mechanism if available. Otherwise atomically create `<ticket-directory>/.coordinate-lock/` with the host's filesystem tools, such as `mkdir` without `-p`. If it already exists, do not treat that as success.

Inside the acquired directory, save `OWNER.md` with the run ID, coordinator runtime identity and host, and acquisition time. Record the same owner in `RUN.md`. Only this owner updates the run record and index. An implementer owns its assigned ticket's implementation fields while writing. The coordinator waits for that writer to stop before changing those fields or entering review. Reviewer children do not write ticket state.

An ownership directory is not a time-based lease. Inspect its owner and runtime before takeover. Age, an empty owner file, a timeout, or missing API access does not prove abandonment. If ownership cannot be established, stop mutation and ask the user to resolve it. Do not remove a competing owner's lock.

After confirming the old coordinator stopped, an authorized resuming coordinator may move its old lock directory to a unique history path inside the ticket directory, then attempt atomic acquisition again. A failed acquisition means another owner won; stop. Preserve existing work and dispatch records during takeover.

Release only your own ownership directory after saving a consistent checkpoint. Prefer moving it to a unique history path; do not recursively delete user data. Release means the coordinator stopped writing, not that its child agents stopped. A later coordinator must still reconcile every child. If you cannot confirm ownership, leave the lock intact and report the issue.

## RUN.md content

Keep a compact current-state section and append meaningful events. Include:

- Run ID; canonical project and ticket paths; spec path and observed digest; owner identity; last update.
- Run mode: `running`, `draining`, `paused`, `blocked`, `closing`, or `complete`. These are run modes, not new ticket statuses.
- User constraints; implementation concurrency ceiling; effective concurrency and reason; runtime capacity; workspace and test-resource policy.
- Integration policy: agreed consumer base, permitted actions, and explicit authority for any commit or integration action. Default: no such authority.
- Dashboard, when an active local run has one: dashboard script identity, command or arguments, owner runtime, process ID and start identity, bound host and port, URL, start time, final-snapshot path when stopped, and current process state. Record only a process that this coordinator started or safely inherited through the recorded coordinator-transfer procedure. Preserve the previous and new coordinator identities, verified old-owner stop, process identity check, transfer time, and transfer event. A dashboard URL is observational; it grants no workflow or process-control authority.
- Runtime map: each coordinator, implementer, delegated child, reviewer, and verifier's canonical agent path; parent agent path (or an explicit root marker); role; ticket and assignment when applicable; runtime ID and host; optional session ID; progress-record path; last observed liveness; and next action. This map is the dashboard ancestry join, not a replacement for dispatch and ownership evidence.
- Assignment table: ticket link, stable assignment ID, attempt number, stage, canonical agent path, runtime ID and host, code checkout, baseline/target, progress-record path, last observed runtime state, and next action.
- Workspace reservations: physical checkout path, repository identity, branch or detached state, exact base and prerequisite evidence, owner, and allocation/transfer/retention state. Link dirty-content manifests when applicable. Record actual test-resource identities, host, owner, permitted use, isolation settings, and release conditions. Preserve unknown reservations until runtime and filesystem evidence resolve them.
- Active review roles and their runtime IDs; report paths; paused or uncertain workers; required decisions and retry conditions.
- Final verification policy (requested or not requested); verifier assignment/runtime and resource reservation; combined target/spec identities; report path and current outcome. Feature verification is separate from ticket status and requires its own freshness check.
- Telemetry observations, when available: observation time, matched canonical agent path and session ID, model and context-window values when reported, exact latest-call input, separately reported cumulative token fields, and the resulting normal/warning/critical context action. Never copy session content into `RUN.md`, estimate a missing value, or use cumulative usage as context occupancy. For unavailable or malformed telemetry, record null token fields and the unavailable reason instead.
- Context-pressure actions: at 160,000 through 199,999 exact latest-call input tokens, record a warning, prepare a compact checkpoint or split, and preserve the proposed next action. An owner with an active delegation group also asks the coordinator to preserve, reduce, or revoke its child capacity. At 200,000 or more, record the critical observation, checkpoint the coordinator or affected worker, stop further broad work in that context, and record the fresh-context continuation inputs. A worker continuation stays subordinate: after the writer stops, the coordinator reconciles its ticket and reassigns or resumes it under the existing singular coordinator. These thresholds apply only to exact latest-call input; cumulative totals remain a separate cost/churn signal.
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

## User controls

- **Status:** inspect and explain progress. Do not start a stopped run or change assignments.
- **Finish active work, then stop:** set draining. Start no new implementation tickets or revision attempts. Existing implementers may finish; review their resulting implementations when capacity permits. Save required revisions for resume, then pause. If a required review is blocked, report it rather than waiting indefinitely.
- **Pause/stop now:** stop new dispatch, request active workers to checkpoint and stop, and use the runtime's interruption tool when needed. Preserve partial files. Record unconfirmed stops as unknown; do not report a clean pause until writers have stopped.
- **Resume:** re-establish ownership, reconcile runtime and files, restore running mode, then select work. Do not reset tickets to pending as a shortcut.
- **Change scope or limits:** save the instruction. Lowering concurrency stops new dispatch until the run fits the ceiling; do not kill active work unless requested or unsafe. Material spec changes require reconciliation, not silent ticket rewriting.

Keep pauses and questions proportional. Ask one focused question for a material decision, with a recommendation. Do not demand approval for each ordinary assignment or successful review.
