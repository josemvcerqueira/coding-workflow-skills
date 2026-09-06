# Coding Workflow Skills

Reusable skills for coding agents, following the [Agent Skills specification](https://agentskills.io/specification). Install with the [skills CLI](https://github.com/vercel-labs/skills).

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
| [coordinate-work](skills/coordinate-work/SKILL.md) | Coordinate worktrees, implementation, review, final verification, and safe spec cleanup. |
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
      scratch/
    worktrees/
```

The registry binds repository identity to its workspace. Linked worktrees share one project mapping. Each feature gets its own workflow directory. All stages follow WORKFLOW.md pointers instead of searching arbitrary old documents. A unique matching active workflow is found automatically; genuine ambiguity produces one question about the feature, not a demand for filesystem paths. Existing user-supplied artifact paths remain useful inputs after identity and lifecycle checks.

Generated workflow records stay external. Product source, permanent tests, and required configuration stay in the code checkout. The external records need their own backup/sharing policy; setup does not configure one. Existing in-repository records are not silently moved or purged while agents use them. An explicit migration preserves ownership, links, and one canonical tracker.

## Work through the stages

Use shape-the-idea for a new idea, write-the-spec for its discovery brief, and spec-to-tickets for its engineering spec. Each stage finds the selected active workflow and writes only its own artifacts. The interview asks one decision at a time and recommends tradeoffs. These stages save their results without routine final approval gates.

Tickets are vertical, observable slices. The approximate 200k context envelope covers implementation and necessary checks, not later reviews or a token target to fill. An assigned worker starts from its own ticket and follows pointers only when needed.

Then say:

> Use $coordinate-work to finish this feature, including final verification. Use at most two implementation agents.

The coordinator resolves the project, active workflow, ticket directory, and agreed code target. It gives fresh workers exact paths internally. It runs implement-ticket with its TDD companion, then acts as review-ticket's parent with separate quality and behavior reviewers. Implementers do not run a review or start the live application; later stages perform applicable real working-path checks. Reviewers propose corrections; implementers make them.

Parallel implementers receive separate coordinator-owned worktrees and isolated mutable test resources. Workers do not switch branches or create replacement worktrees independently. Review waits for writers and their processes to stop. Integration into the agreed consumer base is serialized and requires explicit authority. No skill gains automatic commit, merge, push, or deployment permission. Without a permitted integration method, use safe serial work when it meets the request or report the precise blocker.

Use the coordinator to ask for status, pause, or resume by feature name. Status is read-only. RUN.md preserves assignments, ownership, constraints, resources, and uncertain outcomes. Unknown liveness never permits duplicate workers or workspace reuse.

For an active local run, the coordinator can also start the bundled read-only dashboard on `127.0.0.1`. It summarizes pipeline progress, active tickets, blockers, runtime ancestry, and exact Codex token telemetry without sending another model request. Progress updates are small atomic JSON records written only at meaningful milestones; the browser reads the local projection every few seconds.

The dashboard keeps current context pressure separate from cumulative usage. Exact latest-call input tokens trigger a warning at 160k and a fresh-context checkpoint at 200k. Cumulative input, cached input, output, reasoning, and total tokens remain visible for cost and churn, but never drive the context alert. Missing or ambiguous telemetry is shown as unavailable instead of estimated.

Large tickets may use a coordinator-approved delegation group when the work has independently observable contracts, disjoint file leases, and isolated mutable resources. One implementer remains the ticket owner. Its children cannot spawn further children, change lifecycle records, or overlap leased paths; integration and review wait until the whole group has stopped.

A ticket-only run stops after review and keeps its spec for final verification. To run verification separately, say “Use $verify-feature to verify this feature.” It resolves the active spec, tickets, and combined checkout. Docker and browsers are used when appropriate, not for every project. A standalone verifier returns evidence; the coordinator owns subsequent closure.

## Completion and spec deletion

A ready ticket is not a verified whole feature. Final verification tests the combined implementation against the active spec, with criterion-level evidence and confirmed cleanup. Failures return through implementation and independent review.

After current whole-feature verification passes and the closure gates hold, the coordinator deletes the exact registered workflow-owned spec files, including registered drafts. It writes a closing journal before deletion and a completion receipt afterward. No archive, hidden backup, or replacement spec is created. Product code and maintained tests are the implementation reference after closure.

Discovery, tickets, and reports remain closed execution evidence, not active requirements. Former spec paths and IDs are historical identifiers. Closing/completed workflows are excluded from active discovery, and the ticket validator refuses to schedule them. Later changes start a new workflow from current code and user intent; agents do not reconstruct deleted specs from old records.

Paused, failed, blocked, merely implemented, or ticket-only work keeps its spec. Cleanup never deletes product code, context, another workflow, user-owned input documents, or the sole implementation copy. Existing unrelated specs are not retroactively purged. The coordinator reports exact deletions and the absence of a workflow-managed recovery copy; external backups and Git history are not rewritten.

See the [workspace contract](skills/setup-workflow/references/workspace.md) and [closure contract](skills/setup-workflow/references/close-workflow.md).

## Invocation and format

All skills are explicit-only. Codex uses `$skill-name`; Claude Code uses `/skill-name`. Codex policy sets `allow_implicit_invocation: false`; Claude metadata sets `disable-model-invocation: true`. Reading a required companion during an explicit workflow does not enable implicit model invocation.

Each folder contains SKILL.md and agents/openai.yaml, with supporting references or scripts where useful. Instructions use short, direct English based on STE principles, without claiming formal ASD-STE100 compliance.

TDD and review guidance build on [Matt Pocock's TDD](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) and [code-review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) skills. Implementation simplicity also draws on [Ponytail](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md).

## License

MIT. See [LICENSE](LICENSE).
