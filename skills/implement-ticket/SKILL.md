---
name: implement-ticket
description: Use when the user explicitly invokes this skill to implement one assigned local ticket. Not for ticket planning, code review, or live application testing.
license: MIT
disable-model-invocation: true
---

# Implement ticket

Implement the assigned ticket as a complete working slice. Use test-driven development (TDD). Finish with build and test evidence, and a clear implementation record for the next stage.

This stage does not perform code review, a separate spec review, or a style-improvement pass. Do not launch the application, open a browser, run live end-to-end checks, or start a review agent. Do not implement the next ticket.

## Read the assignment

Required reference: read this collection's [external workspace contract](../setup-workflow/references/workspace.md). Locate the installed setup-workflow companion if the sibling path is absent; do not install it silently. Resolve the selected project, external context, and active workflow from its registry and task identity. The user need not supply directory paths. Read the external CONTEXT.md and applicable repository instructions or user-maintained context. Keep their scopes explicit. Missing context alone does not block safe work; inaccessible required guidance needs its own blocker. Do not execute closing or completed workflows.

When assigned through an explicit `coordinate-work` run, follow this skill as the child task's required reference. Use the coordinator's canonical ticket path and separate code checkout path. Do not update a stale ticket copy inside another worktree. Your assignment ID is the recorded assignee; the coordinator tracks the runtime agent ID separately.

Normally one implementer and context complete this ticket. Read [controlled delegation](references/delegation.md) only when the coordinator has recorded a positive `child_capacity` for this assignment **and** you can identify independently observable behavior or contract work. Do not infer either condition from spare runtime slots, different filenames, or a request to finish faster. That reference is the only exception to this stage's single-owner, single-writer default. Without both conditions, do not dispatch a child.

The coordinator owns workspace allocation. Before edits, verify the assigned physical checkout, repository, branch or detached state, base, and resource reservation. Work only in that checkout and the assignment's permitted ticket, test, and output locations. Do not create another worktree, switch branches, change the working base, or use another worker's mutable resources independently. Report mismatches or unexpected shared resources before affected work. A revision reuses the assigned worktree; relocation requires a new coordinator handoff. These rules do not prevent source reads needed for the ticket.

Start with the exact ticket file. Read applicable project instructions, relevant source code, tests, and the spec sections linked by the ticket. Resolve relative links from their containing file. Read prerequisite handoff evidence as needed. Do not load the full ticket set or discovery conversation by default.

Load selected language/framework skill mappings whose file scope and stage apply to this implementation. Read each relevant SKILL.md and its required references as scoped guidance within this explicit invocation. Resolve skill paths from the context file and scope patterns from the documented project root. Pending recommendations are not selected standards. Preserve project rules and this stage's TDD, no-review, and no-application-startup boundaries; report material conflicts. Do not install missing guidance or invent its contents. Missing optional guidance is not a blocker. If required guidance is inaccessible, stop affected implementation and report the missing standard and resolution needed; do not claim the ticket implemented while that requirement remains unresolved. Record the applied skill paths and available revision identities in the implementation handoff.

Check the assignment and required dependencies before editing code. In this workflow, the coordinator sets `assignee` and `status: "in_progress"` before dispatch. Do not claim an unassigned ticket, take another agent's ticket, or revive a superseded ticket. Report an assignment conflict to the user or coordinator.

A prerequisite must have `status: "ready"` after review and be available in this ticket's working base. A completed branch alone is not sufficient. Report unresolved dependencies or external blockers. Do not implement around a missing prerequisite or silently change the dependency graph.

For a revision assignment, read the ticket's linked review report and accepted required finding IDs. The coordinator changes revision_required to in_progress and confirms the assignee before dispatch. Fix those findings within the ticket's scope. Preserve review history; record each correction or evidence-based disagreement in the implementation record. Do not mark review findings approved or set ready yourself.

Inspect existing changes and preserve work that is not yours. Find the project's test, typecheck, lint, and build commands. Inspect their scripts and configuration for application startup or external side effects before running them.

State the intended slice and immediate checks briefly. Do not require approval for routine implementation choices. Research facts available in the project or relevant primary documentation. Ask one focused question only when a material scope or contract conflict remains; give a recommendation and its tradeoff.

## Implement with TDD

Required reference: read the companion [tdd skill](../tdd/SKILL.md) before writing tests or production changes. Follow its test-first method throughout implementation in this agent and context. A coordinator-approved delegation group follows the child-local TDD and parent-integration rules in [controlled delegation](references/delegation.md); it is not a later testing stage. Read its supporting references as directed.

The companion is part of this workflow's explicit invocation. Read its files directly; do not depend on automatic skill selection or a model-invoked slash command. If the sibling path is absent, locate this collection's installed `tdd` skill. If it is unavailable, report the missing dependency before coding; do not substitute an unrelated TDD skill silently.

This stage's no-application-startup and no-review boundaries still apply. Use permitted in-process tests. Record checks that require a live application for the next stage.

Follow project conventions. Use clear names, cohesive modules, and explicit interfaces. Keep responsibilities separate where it improves understanding and testing. Avoid speculative abstractions and unrelated cleanup. Implement required validation, error handling, and security now; later review is not a reason to leave known defects.

Complete all layers required by this ticket. Do not leave a UI stub or defer a required layer to an unassigned future ticket. The slice must be ready for later whole-application testing even though this stage does not run that testing.

## Keep the implementation simple

Choose the simplest maintainable solution that satisfies every ticket requirement. Reduce unnecessary code, not required behavior, tests, or safeguards. Prefer clear code and useful module boundaries over fewer lines or files.

Before adding code, check for a suitable existing implementation. Then consider the standard library, native platform features, and installed dependencies. Reuse an option only when its behavior meets the required contracts. Add custom code or a new dependency when those options are insufficient; explain the concrete need and maintenance cost in the implementation record. Do not replace a well-supported dependency with fragile custom code merely to reduce the dependency count.

For a bug fix, trace the responsible code and relevant callers. Fix the cause at the appropriate boundary instead of repeating a workaround in each caller. Preserve callers' different contracts. Keep the fix within the ticket; report broader required changes rather than silently expanding scope.

Do not substitute a smaller feature for the agreed spec. Keep the TDD method, regression checks, and handoff evidence required above. Simplicity does not introduce a one-test limit or a separate review pass.

These principles draw on [Ponytail](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md). This link is attribution, not a required skill to load.

## Check the implementation

Run focused tests and typechecking during implementation. At the end, run the full applicable test suite that does not launch the application, the project build, and configured static checks relevant to the change. Run final checks after the last code edit.

If the full test command includes application startup, select the supported non-application suites. Record exactly which suites were excluded and why. Do not change the project's test configuration merely to avoid a failing check. If no build or other check exists, report that fact instead of inventing a command.

Diagnose failures and fix defects introduced by this ticket. Keep pre-existing failures, unavailable services, and skipped checks visible. Do not expand into unrelated repairs. A failed or unavailable required implementation check prevents a verified-completion claim.

Checking acceptance criteria against implementation evidence is part of finishing the ticket. It is not a separate audit. Do not add a code-review loop, broad polish pass, or live demonstration after these checks.

## Record and hand off

Update only the assigned ticket's implementation record and permitted lifecycle fields. Preserve its requirements, dependency fields, and existing evidence. Record:

- What changed, with relevant acceptance-criterion IDs and source paths.
- The implementation location: an existing commit, a branch with revision, or the exact workspace path and base revision with changed files when work is uncommitted.
- Test-first evidence, final check commands, results, and any failures or unrun checks.
- Remaining blockers and the live-application checks left for the next stage.
- Assigned workspace identity and resource/process state. Stop owned mutating test processes and report unresolved cleanup. After handoff, make no further code writes until the coordinator assigns a revision. Do not remove the worktree or release the coordinator's reservations yourself.

Set `status: "implemented"` and a concrete `implementation_ref` only when the ticket's implementation scope is complete and required implementation checks pass. Deferred live-application checks are not implementation checks; label them unrun. If work remains or required checks are blocked, retain `in_progress` and explain the blocker. Do not invent a new status.

Leave `available` to the coordinator, who verifies access from the consuming base. Preserve `review_ref` as a pointer to prior evidence during revisions; that report does not approve the new code. A changed implementation requires a new review. Do not update other tickets or the index. Do not commit, push, merge, or deploy unless separately requested. Outside a coordinator-registered delegation group, do not dispatch further work.

Keep context focused. Exact latest-call input telemetry from the active run, when available, drives the context policy; cumulative use does not. At 160k through 199,999 latest input tokens, checkpoint the current location, checks, blockers, next action, and delegation state, then ask the coordinator to preserve or adjust any child allowance. At 200k or above, stop broad work, checkpoint, request active children to checkpoint, and continue only through a coordinator-arranged fresh context. The coordinator must reconcile or drain the group, confirm this ticket owner stopped, and re-register any continuing children's ancestry, leases, and resources under the replacement owner before it writes. Do not dispatch new children while context-critical or treat child dispatch as a substitute for continuation. If telemetry is unavailable, do not estimate it; still checkpoint before context becomes unwieldy. Do not mark partial work implemented.

Return the ticket path, implementation outcome, check results, and remaining limitations. No final sign-off is required. Use short sentences, active voice, and consistent technical terms based on STE principles. Do not claim formal ASD-STE100 compliance.
