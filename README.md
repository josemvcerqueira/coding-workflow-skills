# Coding Workflow Skills

Reusable skills for coding agents, following the [Agent Skills specification](https://agentskills.io/specification). Install with the [skills CLI](https://github.com/vercel-labs/skills).

See the [workflow cohesion audit](docs/audits/2026-09-06-workflow-cohesion.md) for the current design assessment, resolved conflicts, scenario checks, and remaining tradeoffs.

## Available skills

| Skill | Purpose |
| --- | --- |
| [setup-workflow](skills/setup-workflow/SKILL.md) | Prepare the external workflow workspace, project lookup, context, and scoped skill guidance. |
| [setup-project-context](skills/setup-project-context/SKILL.md) | Compatibility entrypoint for setup-workflow. |
| [make-it-clear](skills/make-it-clear/SKILL.md) | Explain a concept or restore context during a task. |
| [shape-the-idea](skills/shape-the-idea/SKILL.md) | Turn an idea into a discovery brief through research and one decision at a time. |
| [write-the-spec](skills/write-the-spec/SKILL.md) | Define engineering contracts and testable acceptance criteria. |
| [spec-to-tickets](skills/spec-to-tickets/SKILL.md) | Create local vertical tickets with dependencies and parallel-work constraints. |
| [implement-ticket](skills/implement-ticket/SKILL.md) | Implement one assigned slice with TDD, builds, and tests, without review or application startup. |
| [review-ticket](skills/review-ticket/SKILL.md) | Run independent quality and behavior reviews and record required revisions. |
| [verify-feature](skills/verify-feature/SKILL.md) | Test the combined feature against its full active spec and save runtime evidence. |
| [coordinate-work](skills/coordinate-work/SKILL.md) | Coordinate worktrees, implementation, review, durable pause/resume, final verification, and safe spec cleanup. |
| [tdd](skills/tdd/SKILL.md) | Apply behavior-focused test-first development in the implementing agent. |
| [backend-architecture](skills/backend-architecture/SKILL.md) | Evaluate backend design, data, caching, latency, and scaling tradeoffs. |

## Install

From a local checkout:

```sh
npx skills add . --list
npx skills add . --skill setup-workflow -a codex -a claude-code
# Authoring stages and their required companions:
npx skills add . --skill setup-workflow shape-the-idea write-the-spec backend-architecture spec-to-tickets -a codex -a claude-code
# Coordinated implementation, review, and final verification:
npx skills add . --skill setup-workflow coordinate-work implement-ticket tdd review-ticket spec-to-tickets verify-feature -a codex -a claude-code
# Compatibility entrypoint, if needed:
npx skills add . --skill setup-project-context setup-workflow -a codex -a claude-code
```

The stage skills require setup-workflow's shared file contract; install it alongside individually selected stages too. implement-ticket also requires tdd. review-ticket and verify-feature require spec-to-tickets. Backend specifications require backend-architecture. Companion reads do not install missing skills automatically. make-it-clear, tdd, and backend-architecture can also be used independently within their scope.

The optional dashboard is a separate application, not part of any skill installation:

```sh
cd apps/workflow-dashboard
npm pack
bun install --global ./coding-workflow-dashboard-0.1.1.tgz
```

This installs the publishable runtime artifact and its `workflow-dashboard` command outside the skills directory. It requires Bun 1.3+ and Python 3.10+. A coordinator discovers it from `PATH`; when it is absent, coordination continues without the browser projection or JSON progress heartbeats. After package publication, `bun install --global coding-workflow-dashboard` replaces the pack-and-install steps.

After publication to the planned public GitHub repository, the source can be `josemvcerqueira/coding-workflow-skills` instead of `.`. That repository must exist first. Add `-g` for a global installation.

## Start and discover work

Select the product project and say:

> Use $setup-workflow to prepare this project for our coding workflow.

Setup explores the project, using focused read-only subagents for larger projects. The parent writes the external context and registry. It does not run project builds, tests, setup scripts, or services, install skills, create implementation worktrees, or invent feature tickets. It preserves user-maintained repository instructions and selected standards. Missing optional context does not block safe work; missing required guidance remains an explicit gap. This collection does not include a curated language-skill catalog.

The default layout is outside the main product checkout:

```text
<main-checkout-parent>/.coding-workflow/
  PROJECTS.md
  <project-id>/
    PROJECT.md
    CONTEXT.md
    INDEX.md
    workflows/<workflow-id>/
      WORKFLOW.md
      discovery.md
      spec.md
      tickets/
      reviews/
      verification/
      RUN.md
      checkpoints/
      scratch/
    worktrees/
```

The registry binds repository identity to its workspace. Linked worktrees share one project mapping. Each feature gets its own workflow directory. All stages follow WORKFLOW.md pointers instead of searching arbitrary old documents. A unique matching active workflow is found automatically; genuine ambiguity produces one question about the feature, not a demand for filesystem paths. Existing user-supplied artifact paths remain useful inputs after identity and lifecycle checks.

Generated workflow records stay external. Product source, permanent tests, and required configuration stay in the code checkout. The external records need their own backup/sharing policy; setup does not configure one. Existing in-repository records are not silently moved or purged while agents use them. An explicit migration preserves ownership, links, and one canonical tracker.

## Work through the stages

Use shape-the-idea for a new idea, write-the-spec for its discovery brief, and spec-to-tickets for its engineering spec. Each stage finds the selected active workflow and writes only its own artifacts. The interview asks one decision at a time and recommends tradeoffs. These stages save their results without routine final approval gates.

Tickets deliver the smallest useful, observable outcome through its necessary layers, including its essential validation, permissions, failure handling, and focused checks. Split independently useful behavior; keep atomic correctness together. Optimize verified outcomes and total effort rather than ticket count. Dependencies identify real producer capabilities; temporary file or test-resource conflicts constrain parallel scheduling separately. Count-based sizing warnings prompt judgment and never reject a coherent slice by themselves. See the [slicing examples](skills/spec-to-tickets/references/slicing.md).

Each ticket separates its focused checks from combined-feature scenarios and required project gates. Context size is a planning signal rather than a workflow boundary. An assigned worker starts with its ticket and follows pointers only when needed. Unexpected breadth returns to the coordinator for safe replanning of the unfinished remainder, preserving code, evidence, and criterion ownership.

Then say:

> Use $coordinate-work to finish this feature, including final verification. Use at most two implementation agents.

The coordinator resolves the project, active workflow, ticket directory, and agreed code target. It gives fresh workers exact paths internally. It runs implement-ticket with its TDD companion, then acts as review-ticket's parent. One reviewer covers both axes by default; the coordinator adds a second independent reviewer for higher-risk or uncertain work. Implementers do not choose reviewer count, run their own review, or start the live application; later stages perform applicable real working-path checks. Reviewers propose corrections. A reviewer may complete a narrowly leased mechanical repair during the same round; the implementer makes every other accepted fix.

Implementation, review, and final verification share one [check-scope policy](skills/setup-workflow/references/check-scope.md). After a correction, rerun failed and affected checks and retain only independently validated unaffected evidence. A mechanical test-name fix does not by itself justify repeating an hour-long suite. A small authorization or concurrency change may justify broad regression checks. Required failures remain unresolved until corrected and verified; a current report distinguishes new observations, carried evidence, and blocked checks.

The coordinator owns scheduling, reservations, recovery, integration, and lifecycle evidence. Workers own code and detailed investigation. A repeated failure changes the next action to diagnosis, a bounded repair, or replanning; it does not restart an unchanged implementation/review loop. Existing timestamps and measured check durations can show where effort went without another tracker. Durable `RUN.md` state supports continuity; creating a separate task-level goal requires an explicit goal request and permitted tool support.

Parallel implementers receive separate coordinator-owned worktrees and isolated mutable test resources. Workers do not switch branches or create replacement worktrees independently. Review waits for writers and their processes to stop. Starting an explicit coordination run grants standing authority for local commits and serialized integration of reviewed work into its selected local consumer; continue and resume preserve the recorded policy without expanding it. Pushes, pull requests, deployments, shared infrastructure changes, history rewrites, and destructive handling of existing work still require separate authority.

Use the coordinator to ask for status, pause, continue, or resume by feature name. Status is read-only. `pause` stops new dispatch, gives every active runtime its own Markdown handoff path, and creates an immutable resume manifest under the external workflow's `checkpoints/` directory. `continue` and `resume` reacquire ownership, reconcile that manifest with current files and runtime state, and execute its first saved resume action. Source changes remain in their recorded code worktrees; canonical tickets, handoffs, progress records, `RUN.md`, and pause artifacts remain together in the external workflow shared across worktrees. Unknown liveness never permits a clean-pause claim, duplicate worker, or workspace reuse.

> Use $coordinate-work to pause this feature.
>
> Use $coordinate-work to continue this feature.

For an active local run, the coordinator can also start the separately installed read-only dashboard on `127.0.0.1`. The coordinator and Bun dashboard server run as separate processes. The server refreshes telemetry through a persistent background worker every 30 seconds and serves the last completed snapshot immediately, so a slow session scan cannot hold up the page. The page gives a compact view of ticket completion, phase, review returns, active agents, and current context. Detailed runtime records remain in the API and workflow artifacts. Three-second browser polls rerender only when the snapshot changes.

Exact latest-call input shows occupancy against the runtime-reported context window, but no fixed token count stops or transfers work. The runtime manages compaction; the same coordinator reloads compact run records and continues with its existing workers and dashboard. The page shows only current occupancy and a compact used/window value. Cumulative counters and precise telemetry failure reasons remain diagnostic data rather than user-facing status.

Large tickets may use a coordinator-approved delegation group when the work has independently observable contracts, disjoint file leases, and isolated mutable resources. One implementer remains the ticket owner. Its children cannot spawn further children, change lifecycle records, or overlap leased paths; integration and review wait until the whole group has stopped.

A ticket-only run stops after review and keeps its spec for final verification. To run verification separately, say “Use $verify-feature to verify this feature.” It resolves the active spec, tickets, and combined checkout. Docker and browsers are used when appropriate, not for every project. A standalone verifier returns evidence; the coordinator owns subsequent closure.

## Completion and spec deletion

A ready ticket is not a verified whole feature. Final verification tests the combined implementation against the active spec, with criterion-level evidence and confirmed cleanup. Failures return through implementation and independent review.

A confirmed feature defect can go directly to an accepted revision through the review parent's record contract, followed by implementation and independent review of the fix. Uncertain findings need diagnosis first. Repeated feature verification reruns failed and affected integrated scenarios and accounts for every criterion in a new report; validated unaffected feature observations can carry forward.

After current whole-feature verification passes and the closure gates hold, the coordinator deletes the exact registered workflow-owned spec files, including registered drafts. It writes a closing journal before deletion and a completion receipt afterward. No archive, hidden backup, or replacement spec is created. Product code and maintained tests are the implementation reference after closure.

Discovery, tickets, reports, and pause checkpoints remain closed execution evidence, not active requirements. Pause checkpoints retain identities and artifact pointers, not replacement specification contents. Former spec paths and IDs are historical identifiers. Closing/completed workflows are excluded from active discovery, and the ticket validator refuses to schedule them. Later changes start a new workflow from current code and user intent; agents do not reconstruct deleted specs from old records.

Paused, failed, blocked, merely implemented, or ticket-only work keeps its spec. Cleanup never deletes product code, context, another workflow, user-owned input documents, or the sole implementation copy. Existing unrelated specs are not retroactively purged. The coordinator reports exact deletions and the absence of a workflow-managed recovery copy; external backups and Git history are not rewritten.

See the [workspace contract](skills/setup-workflow/references/workspace.md) and [closure contract](skills/setup-workflow/references/close-workflow.md).

## Invocation and format

All skills are explicit-only. Codex uses `$skill-name`; Claude Code uses `/skill-name`. Codex policy sets `allow_implicit_invocation: false`; Claude metadata sets `disable-model-invocation: true`. Reading a required companion during an explicit workflow does not enable implicit model invocation.

Each skill folder contains `SKILL.md` and `agents/openai.yaml`, with instruction references or bounded deterministic validation helpers where useful. Long-lived applications and browser assets live outside `skills/`. Instructions use short, direct English based on STE principles, without claiming formal ASD-STE100 compliance.

TDD and review guidance build on [Matt Pocock's TDD](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) and [code-review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) skills. Implementation simplicity also draws on [Ponytail](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md).

## License

MIT. See [LICENSE](LICENSE).
