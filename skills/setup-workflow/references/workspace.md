# External workflow workspace

Read this contract before resolving or writing workflow artifacts. The product checkout and workflow workspace are different roots. Source code, permanent tests, and required product configuration belong in the checkout. Generated context, discovery, specs, tickets, reports, scratch files, and coordination records belong in the external workspace. Do not store them in the installed skills repository either.

## Resolve the project and workspace

1. Start from the selected project or an explicit assignment. Resolve physical paths. In Git, inspect the shared Git directory and worktree inventory to identify the repository and its main checkout. Linked worktrees use that same project identity, not a new workspace for each branch. For a non-Git project, use its selected physical root. Separate clones are separate local identities unless explicitly mapped together.
2. Reuse the assignment's verified PROJECT.md or registered workspace. Otherwise inspect `<main-checkout-parent>/.coding-workflow/PROJECTS.md`. Match the exact repository identity, not just a name or remote URL. For non-Git projects, use the selected root's parent. Do not search the user's entire filesystem or select the most recent unrelated directory.
3. The registry maps project ID, repository identity, main checkout, host, and workspace path. Verify each match against PROJECT.md and the actual repository. A moved repository, inaccessible path, or conflicting mapping needs reconciliation, not an automatic duplicate. Ask one focused question only when evidence cannot identify the project or intended workflow.
4. Default new workspace: `<main-checkout-parent>/.coding-workflow/<project-id>/`. Choose a readable unique ID and persist it; do not recompute it on each run. A user-selected external location is allowed and must be registered at the same discoverable registry. The resolved workspace must be outside all product checkouts. If the default is inside another repository or unavailable, select a permitted external location with the user; do not fall back to product docs.

Read-only/status requests only resolve existing files. During an explicit authoring or execution request, a stage may initialize the missing external directory and registry through this contract. This does not invoke setup's exploration, install skills, or start another stage. Suggest setup-workflow once when project context is missing. Missing context alone does not block safe work; missing required standards still block affected conclusions.

If no project is identified, ask for the project before saving project-specific artifacts. Do not choose the skill collection as the project by accident. An external brief supplied by the user can be read as input without moving or deleting it.

## Layout and records

```text
<workspace>/
  PROJECT.md
  CONTEXT.md
  INDEX.md
  workflows/<workflow-id>/
    WORKFLOW.md
    discovery.md
    spec.md
    tickets/INDEX.md
    tickets/T-001.md
    reviews/T-001/R-001.md
    verification/V-001/REPORT.md
    RUN.md
    checkpoints/
    scratch/
  worktrees/<assignment-id>/
```

Create directories as needed. Setup creates the project container, workflows/, and worktrees/, not fictional tickets or empty specs. If the user already names a feature, setup can register that workflow and create its tickets/, reviews/, verification/, and scratch/ directories. Its authoring stage creates each real document when it has content. Worktrees are created later by the coordinator, not by setup.

PROJECT.md records the project ID, host, exact repository identity, main checkout, workspace path, external context path, and links to applicable repository instructions. CONTEXT.md is a maintained navigation/command/standards map, not a copy of specs. Existing repository instructions and user-maintained docs keep their authority.

INDEX.md lists active workflows with ID, title, WORKFLOW.md path, and current stage. Keep a separate compact completed list that links only to completion receipts. Also keep a state-independent reservation table with workflow ID/state, RUN.md path, owner/host, physical resource identity, and release condition. Include closing workflows and completed workflows with retained resources. Exclusion from active dispatch never releases a reservation. WORKFLOW.md records ID, project ID, title, state (`active`, `closing`, or `completed`), goal summary, and relative paths for discovery, spec, tickets, reviews, verification, and RUN.md. On the first pause, create the conventional `checkpoints/` directory if it is absent. It holds immutable coordinator pause manifests and per-runtime pause handoffs; agent implementation, review, verification, and progress records stay in their existing canonical locations. Register every workflow-owned spec or spec draft by exact relative path under `spec_files`; use `spec.md` for the canonical spec. Do not register user-owned external inputs for deletion. Record closure policy: delete owned specs after verified completion. No archive or hidden backup of those specs is created.

Registry/index updates require a single writer. Use the project's established mechanism or atomically acquire `.registry-lock/` beside PROJECTS.md and `.project-lock/` inside the workspace for short metadata updates. Record owner/runtime identity; release only your own lock. Unknown ownership is not abandoned. Hold no metadata lock while waiting for an interview or worker. Per-workflow execution still uses `<tickets>/.coordinate-lock/`. Different workflows have different execution locks but must reconcile shared code and test resources. Under the short project metadata lock, check existing resource claims and record a new claim before allocation or dispatch. Then release that lock before slow operations. Record outcomes in RUN.md and the reservation table. An uncertain or interrupted allocation keeps its claim; a failed metadata update blocks conflicting work. Remove claims only after runtime and resource checks confirm release.

## Select one workflow

An exact assignment wins after identity checks. Otherwise use the current task's explicit feature and INDEX.md. Select the sole matching active workflow. When more than one remains plausible, ask which feature by title; do not ask the user to reconstruct filesystem paths. Create a new ID only for a new idea or an explicit new workflow, not because the current stage changed. Follow WORKFLOW.md pointers; never pick a spec merely because it is newest.

Keep closing workflows in a separate recovery list in INDEX.md, with their ID, title, WORKFLOW.md, CLOSING.md, and RUN.md paths, even when they have no retained resources. A coordinator resume or close request resolves that list by feature identity before selecting active work. A status request may inspect recovery or completed records without mutation. Do not make the user supply lost paths to resume interrupted cleanup.

Check for CLOSING.md and COMPLETED.md in the workflow or ticket directory before authoring, dispatch, review, or verification. Either marker blocks normal execution even when the index or ticket status is stale. Closing permits only ownership reconciliation and the closure procedure. Completed records are excluded from ordinary discovery and cannot be resumed as active tickets. Later changes start a new workflow from current code and current user intent.

Pass resolved workspace, workflow, context, ticket, and code-checkout paths to children. Resolve document links from the containing document, not cwd. Source paths and scope patterns use the explicitly stated code root; standard-skill paths must identify their actual installed locations. Absolute host paths are not portable across machines. On another host, register its actual checkout and accessible artifact location; never assume equal basenames imply equal projects.

## Existing layouts

Do not silently move records used by live or uncertain agents. Inspect old conventions and references first. For an explicitly requested migration, stop affected writers, inventory exact owned artifacts, move them into one external workflow, rewrite links and command/source roots, and validate them before removing old copies. Do not retain two active trackers. User-maintained project documents are not disposable workflow files. Report migration needs when authority or ownership is unclear; do not purge old docs or change AGENTS.md, CLAUDE.md, or host settings as an implied step.

The external workspace needs its own backup/sharing policy. Setup does not configure syncing or version control. Do not commit workflow specs into another repository as a workaround for the deletion policy.
