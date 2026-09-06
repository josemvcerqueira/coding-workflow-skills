---
name: review-ticket
description: Use when the user explicitly requests code review and completion verification of one implemented local ticket, including a new review after implementation revisions.
license: MIT
disable-model-invocation: true
---

# Review ticket

Review one implemented ticket with at least two independent agents. Decide whether the ticket is ready or needs revision. Save evidence and update local ticket state. Code quality and correct behavior are separate requirements; neither can replace the other.

The review agents propose improvements and diagnose defects. They do not edit production code, rewrite tests to pass, or change ticket state. The implementer makes accepted fixes in the next implementation pass. The parent agent coordinates the review and is the only writer of the review record, ticket, and index.

Within an explicit `coordinate-work` run, that coordinator acts as this skill's parent and launches the independent reviewers. Use the canonical ticket path and assigned code checkout. Do not create a second state-writing coordinator. After this one-ticket review ends, return control to the coordination loop; reviewer children still cannot dispatch more work.

## Establish the review target

Required reference: read this collection's [external workspace contract](../setup-workflow/references/workspace.md). Locate the installed setup-workflow companion if the sibling path is absent; do not install it silently. Resolve the selected project, external context, and active workflow from its registry and task identity. The user need not supply directory paths. Read the external CONTEXT.md and applicable repository instructions or user-maintained context. Keep their scopes explicit. Missing context alone does not block safe work; inaccessible required guidance needs its own blocker. Do not execute closing or completed workflows.

Read the exact ticket, its implementation record, and the linked spec sections. Read applicable project instructions and relevant `CONTEXT.md`, `context.md`, context-map entries, and architecture decisions. Do not load all tickets or the discovery conversation. Inspect the index and prerequisite metadata only for lifecycle checks and dependency updates.

Read [the ticket format](../spec-to-tickets/references/ticket-format.md). This collection's format and validator are required companions. Locate the installed `spec-to-tickets` skill if the sibling path is absent. If it is unavailable, report the missing dependency before changing state. Read companion files directly as part of this explicit invocation; do not depend on implicit skill selection.

Use `implemented` as the normal entry state. Resume `in_review` from its saved record. A ticket in `revision_required` returns through implementation before another review. For an explicit re-review of a `ready` ticket, record why it is reopened and notify the assignment coordinator about affected consumers. Do not review an active implementer's changing checkout or revive a superseded ticket.

Resolve the implementation location and exact baseline from evidence. Follow [snapshot rules](references/snapshot.md) before dispatch. If the source, spec, or comparison is materially ambiguous, research first. Ask one focused question only if it remains unresolved, with a recommended answer and its tradeoff.

Coordinate a single writer with the assignment owner. If no other coordinator is active, this parent owns this ticket's review transition and index refresh. Record that ownership and the review target in the ticket. Set `in_review` before dispatch. Preserve the implementation assignee. File state is not an atomic lock; resolve competing ownership before writing.

## Dispatch two independent reviews

Read [the reviewer briefs](references/reviewer-briefs.md). Start at least two distinct agents with fresh, focused contexts. Run them in parallel when tools and isolated test resources permit. Never ask the implementer to approve its own work. Do not substitute one agent role-playing two reviewers.

Give each agent its role brief, ticket path, spec pointers, exact review target, relevant standards paths, skill paths, permitted test environment, and report requirements. Give file pointers and necessary facts, not the whole conversation or the other reviewer's conclusions. Keep initial findings independent.

- **Quality and standards:** inspect maintainability, language idioms, project rules, and design costs. Read relevant language or framework skills named by project context files. Distinguish required fixes from optional suggestions.
- **Spec and behavior:** compare the slice with its requirements. Check integrations, error paths, regressions, and applicable security boundaries. Investigate suspected defects with evidence. Run the required working-path checks in a safe local test environment, including application startup when needed.

Both agents may inspect related code as needed. Only the behavior reviewer owns application startup and mutable test fixtures by default. Give other checks separate resources or run them in sequence. No agent may mutate production services, real user data, or external systems merely to finish a review.

Within a coordinated run, the coordinator supplies and retains checkout and test-resource reservations. Confirm the implementer and its mutating processes stopped before review. Do not create or switch worktrees to bypass the assigned target. Read-only reviewers can share the frozen checkout, but concurrent checks need isolated mutable outputs and fixtures. Wait for both reviewers and their processes to stop, and reconcile cleanup, before returning that checkout to implementation or integration.

If the runtime cannot supply two independent agents, record the limitation. Do not certify readiness. No routine user sign-off is needed when both reviews and required checks succeed.

## Evaluate evidence and decide

Read both reports and verify the cited source, findings, and check evidence. Resolve duplicate findings without losing their axis or source. Ask the relevant reviewer to investigate unsupported claims or disagreements. Do not hide a failure behind the other axis's pass, majority voting, or a lower issue count.

Apply [the review record and decision rules](references/review-record.md). A finding must explain the actual defect or maintenance cost, its location, the violated contract or rule, and a bounded requested change. Personal preference alone does not block completion. A valid spec or safety defect blocks even if an existing style rule endorses the code.

Before a final decision, confirm that the code snapshot, relevant spec, and required checks still match the reviewed versions. A changed target invalidates the affected evidence. Do not apply fixes during aggregation. Return code defects to the implementer; return unresolved product-contract conflicts to the user with one recommendation.

## Save the handoff

Write a numbered Markdown report under `<workflow>/reviews/<ticket-id>/`, outside the ticket and product directories. Preserve earlier rounds. Link it from `review_ref` and the ticket's Review record. Include both axis outcomes, check evidence, open findings, and the next action.

- Both axes pass and required checks pass: set `ready`. This completes the ticket's slice, not the whole feature, a merge, or a release.
- Accepted blocking code or test findings: set `revision_required` and `available: false`. Give the implementer the ticket and report paths, with stable finding IDs and expected verification.
- Required evidence or access is missing: retain `in_review`, record the blocked check and resumption action, and report not ready. Do not invent a code revision merely because a test service is unavailable.

Do not delete or move completed ticket files. Keep dependency edges. Remove ready tickets from open-work lists, but retain their index rows and history. Verify availability in the consumers' agreed base separately from review success; do not mark `available: true` merely because a branch exists.

Run `python3 <spec-to-tickets-directory>/scripts/validate_tickets.py <ticket-directory>`, then refresh the index from current metadata. The script checks structure, not the truth of review evidence. Resolve errors before reporting new assignment candidates. A dependent can start only after all prerequisites are `ready` and available, with no external or resource blockers.

Report reopened-prerequisite impacts to the assignment coordinator and pause affected consumers through that owner. Do not erase dependency edges or rewrite another agent's assignment to make validation pass. Do not merge code to establish availability without authority.

Return the ticket path, ready/not-ready outcome, the two review outcomes, report path, and newly assignable candidates or blockers. Stop after this ticket. Hand off the next candidate; do not automatically implement or dispatch it, commit, push, or deploy.

Use short sentences, active voice, and consistent technical terms based on STE principles. Do not claim formal ASD-STE100 compliance.
