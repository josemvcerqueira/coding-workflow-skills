---
name: review-ticket
description: Use when the user explicitly requests code review and completion verification of one implemented local ticket, including a new review after implementation revisions.
license: MIT
disable-model-invocation: true
---

# Review ticket

Review one implemented ticket through an agent independent of implementation. Decide whether both quality/standards and specification/behavior pass, need revision, or are blocked. This completes one ticket slice, not the whole feature, integration, release, or deployment.

Reviewer children are read-only and never change ticket state. A parent-authorized [bounded reviewer repair](references/reviewer-repair.md) is the only code-edit exception. The parent owns review records and review lifecycle/index updates, synchronized with coordinator-owned availability changes. Within `thin-coordinator`, that coordinator is the parent; return control after this ticket.

## Establish the target

When the coordinator supplies canonical paths, verify the supplied project, workflow, context, ticket, frozen checkout, resources, and handoff identities against the assignment; do not repeat registry discovery. Read the [external workspace contract](../setup-workflow/references/workspace.md) only for a standalone invocation or when supplied paths are absent or inconsistent. Use the exact parent-supplied [handoff manifest](../setup-workflow/references/handoff-manifest.md) path and follow the implementation manifest's recorded source and report paths. Read the ticket, implementation record, linked spec sections, applicable project instructions and context, and relevant standards. Read the [ticket format](../spec-to-tickets/references/ticket-format.md) before changing lifecycle state. Do not load the backlog or discovery transcript.

Follow the [snapshot rules](references/snapshot.md). Resolve the repository, checkout, baseline, target, included paths, dirty-content identity when applicable, and spec digest. Do not review a changing target or revive a superseded ticket. Use `implemented` as the normal entry state; resume saved `in_review`. Before reopening `ready` or recording `revision_required`, check [availability invalidation](references/review-record.md#reopening-and-invalidation). When `available` is true or `integration_ref` is present, the coordinator clears both, preserving the former manifest as history; a standalone parent waits for that update. Already false/null fields need no coordinator wait unless ownership conflicts.

Read and apply [monotonic review closure](references/closure.md). For a first review, require its frozen acceptance and source record before dispatch. For re-review, use its bounded successor surface and start from changed paths, prior finding IDs and dispositions, affected contracts, reusable evidence candidates, and cited report sections. Apply the shared [check-scope contract](../setup-workflow/references/check-scope.md) when choosing checks, enforcing its setup-recovery boundary, and carrying evidence across stages or rounds. Every reviewer independently validates reused evidence against source identity, environment, command, and covered contract.

Coordinate ownership with the assignment owner, preserve the implementation assignee, and set `in_review` before dispatch. Resolve ambiguous source, spec, or competing ownership before mutation; ask one focused question only if evidence cannot resolve a material decision.

## Choose coverage and dispatch

Read [reviewer briefs](references/reviewer-briefs.md). One reviewer with fresh focused context covers both axes by default and reports separate outcomes and evidence. The coordinator decides reviewer count; the implementer does not choose. Use two independent reviewers for concrete security, authentication, authorization, privacy, secret-handling, concurrency, distributed-state, durability, recovery, database or schema migration, destructive data, financial, trading, billing, money-movement, public-contract, compatibility, large cross-subsystem, disputed-finding, or explicit-policy risk. Add a second reviewer after the first only when its evidence creates material uncertainty. If a required second reviewer is unavailable, retain `in_review`; do not certify readiness.

Locate the local [systematic debugging companion](../systematic-debugging/SKILL.md) and include its path in the reviewer assignment. When a permitted check fails or behavior is unexpected and direct evidence does not establish the cause, the reviewer invokes it in diagnosis-only mode. A demonstrated static finding can be reported directly. Debugging does not expand review authority.

Give reviewers file pointers and the current delta, not conversations or copied reports. Include their brief, ticket and spec pointers, exact target, standards, permitted environment, output contract, dashboard state, and reserved resources. Reviewer children return structured axis reports and evidence to the parent. Only the parent writes the numbered report, ticket state, index, and review manifest. With two reviewers, preserve independent first inspection.

Read [bounded reviewer repair](references/reviewer-repair.md) only before granting a review-stage edit. The rule must be explicit and unambiguous; the correction must be local, mechanical, leased, non-semantic, and proven by the smallest meaningful checks. It does not change production behavior or delete or weaken a test. Severity alone is not the gate. No second reviewer is needed solely because of a qualifying repair.

Confirm implementers and mutating processes stopped. Read-only inspection can share the frozen checkout; concurrent mutable checks require isolated resources or sequence. The combined reviewer, or behavior reviewer in a two-reviewer run, owns application startup by default. Use only isolated local/test services and data. Never spend money, send real messages, use production credentials, or mutate external or production systems. Wait for all reviewers and owned processes to stop before returning the target to implementation or integration.

## Evaluate and decide

Read every report and inspect its cited source, findings, checks, limitations, and cleanup. Both axes need explicit outcomes. A final message, majority vote, or one passing axis cannot replace evidence. Ask a reviewer to investigate unsupported claims or disagreements.

Apply the [review record and decision rules](references/review-record.md) and the closure contract's `BLOCK`, `DEFER`, and `ESCALATE` dispositions. A blocking finding identifies a violated contract or demonstrated maintenance cost, location, evidence, consequence, and bounded correction. Complexity scores and smell thresholds are advisory; preference alone does not block. Confirmed behavior and safety defects do block.

For an unexplained failure, inspect the linked diagnosis before deciding. Require a reproduction or recorded blocker, tested hypothesis, classification, affected contract, and routed next action. Keep the diagnosis distinct from both axis outcomes. A diagnosis does not authorize the reviewer to implement its recommended correction.

Inspect any reviewer-repair delta and checks before accepting it. Outside the bounded reviewer repair, do not fix code during aggregation. Semantic changes, public contracts, behavior, expectations, assertions, uncertain moves, and adjacent cleanup return to the implementer.

Before deciding, confirm the reviewed source, spec, standards, and checks remain current. Changed inputs invalidate affected evidence.

## Save the result

Write the next numbered report under `<workflow>/reviews/<ticket-id>/` and preserve earlier rounds. Include both axis outcomes, source identity, criterion evidence, checks and skips, findings and dispositions, repairs, cleanup, blockers, and next action. Write the handoff manifest atomically with the same exact evidence.

- Both axes and required checks pass with no blocking finding: set `ready`.
- An accepted code or test correction remains: after confirming `available: false` and `integration_ref: null`, set `revision_required`.
- Required evidence, access, reviewer, or decision is missing without a confirmed correction: retain `in_review` and record the resume condition.

Leave `available` and `integration_ref` to the coordinator; availability alone is not integration evidence. Run the ticket validator and refresh the derived index. Preserve tickets, dependency edges, and prior evidence. Report reopened prerequisite impacts rather than rewriting another assignment.

Return the ticket path, ready/not-ready result, both axis outcomes, reviewer count and escalation reason, report and handoff paths, and newly assignable candidates or blockers. Stop after this ticket. Do not implement, dispatch another ticket, commit, push, merge, or deploy.
