# Close a verified workflow and delete its specs

This collection deletes workflow-owned specifications at verified completion. It does not archive or maintain them as a second source of product truth. Do not copy their full contents into a renamed document, context file, receipt, or log to defeat deletion. Product code and maintained tests are the implementation reference after closure; retained workflow records are historical execution evidence, not current requirements.

The coordinator owns closure during an explicit run that includes final verification. A standalone verifier returns evidence without deleting files or taking lifecycle ownership. The user can ask the coordinator to close an already verified workflow; it must still check freshness. Setup and status requests never purge specs. A ticket-only run has not verified the feature and retains its spec.

## Check the gate

Read the workspace contract, WORKFLOW.md, RUN.md, ticket state, and final verification evidence. Establish exclusive workflow ownership using the existing coordinator lock. Confirm all of the following before deletion:

- Every non-superseded ticket is reviewed ready, with no pending implementation or revision.
- The combined code is available in the agreed destination. A worktree awaiting integration is not a completed feature.
- Final verification passed on the exact current combined code, spec, and relevant configuration. Inspect evidence; a report filename or final message is insufficient.
- All workers, reviewers, verifier processes, and other consumers of this spec have stopped. No active workflow depends on the live spec; resolve such a dependency first.
- Required cleanup is confirmed, or retention of specific safe resources is explicitly authorized. Preserve implementation worktrees until their code and evidence are safely retained under their separate policy.

Failed, blocked, paused, draining, uncertain, or merely implemented work never qualifies. A changed target requires renewed review/verification as appropriate. Do not delete a spec to hide a failed check or make a task appear done.

## Record intent before deletion

Enumerate `spec_files` and inspect each exact file. Include owned drafts or duplicate spec files identified during this workflow; register them before cleanup. Keep deletion within this workflow's external directory. Reject symlinks, directories, paths that escape the workflow, and files whose ownership or identity is unclear. Do not use recursive deletion, globs, guessed paths, or broad repository scans as deletion targets. Never delete context, source, permanent tests, discovery, tickets, reports, unrelated workflows, or user-owned input documents under this rule.

Create CLOSING.md before the first delete. It records the workflow/project identity, owner, current verification report and digest, tested code/config identity, gate evidence, and each exact spec path with SHA-256 and deletion state. Save no spec contents in it. Mark WORKFLOW.md closing and remove the workflow from active dispatch discovery. Keep its RUN.md and unresolved or retained resource claims discoverable in the project index's separate reservation table, including after completion. Retain this gate marker throughout cleanup; all stage skills and the ticket validator must refuse normal work when it exists.

Before deletion, update INDEX.md under its metadata lock: move the active entry to its recovery list, preserving feature-name lookup and all reservation claims. If that update fails, retain the closing marker and stop before deleting files. Before each file deletion, recheck identity and stopped consumers. Delete only the enumerated unchanged file, then record confirmed absence. No routine user approval is required for these registered owned specs under this policy. A changed file or unconfirmed consumer stops cleanup; do not widen the deletion scope.

## Finish or recover

Once all listed specs are absent, write COMPLETED.md with the completion date, project/workflow ID, final code identity, verification report path, deleted spec paths/digests, retained evidence locations, and cleanup result. It contains no replacement specification. Mark WORKFLOW.md completed and RUN.md complete. Update the project index under its metadata lock. Remove only confirmed released claims from the reservation table; preserve authorized retained resources with their owner and release conditions. Keep CLOSING.md as the deletion journal; COMPLETED.md identifies successful closure. A marker alone is not proof that these gates passed.

Replace the recovery-list entry with the completion receipt only after successful closure. Mark the retained discovery, ticket index, and RUN.md as closed execution records. Their prior spec paths and requirement IDs are historical identifiers whose source was intentionally deleted, not live links to recover or instructions to execute. Reports retain actual observations, not a reconstructed full spec. Do not rewrite old review verdicts to claim they describe later code.

The active ticket validator intentionally rejects closing/completed sets instead of bypassing its missing-spec checks. Validate tickets before closure. After closure, check the receipt, deletion journal, absence of all listed files, and exclusion from active discovery; do not recreate the spec to make active validation pass. A later defect starts a new workflow from current code and user intent, with relevant old failure evidence read only when useful.

If interrupted, retain the closing marker and reservations. A resuming owner checks runtime state, identities, journal, and each exact file before continuing. Absence is acceptable only for a path already listed in the journal. If metadata/index updates fail, report closing/incomplete cleanup and finish them on resume. Do not claim closure until the receipt, state, index, and file absence agree. Do not automatically reopen a partially cleaned workflow.

Tell the user which specs were deleted and that no workflow-managed recovery copy was retained. Do not promise secure erasure from external backups or Git history, and do not rewrite repository history. Keep other workflows and the shared context unchanged.
