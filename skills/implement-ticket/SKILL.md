---
name: implement-ticket
description: Use when the user explicitly invokes this skill to implement one assigned local ticket. Not for ticket planning, code review, or live application testing.
license: MIT
disable-model-invocation: true
---

# Implement ticket

Implement one assigned ticket as a complete working slice with test-first evidence. Do not review it, implement another ticket, launch the application, open a browser, or run live end-to-end checks.

## Establish the assignment

When the coordinator supplies canonical paths, verify the supplied project, workflow, context, ticket, checkout, and handoff identities against the assignment; do not repeat registry discovery. Read the [external workspace contract](../setup-workflow/references/workspace.md) only for a standalone invocation or when supplied paths are absent or inconsistent. Use the exact coordinator-supplied [handoff manifest](../setup-workflow/references/handoff-manifest.md) path. Read external `CONTEXT.md`, applicable repository instructions, the ticket, linked spec sections, relevant code and tests, and prerequisite evidence needed for this slice. Do not load the whole ticket set or discovery history.

Verify the physical checkout, repository, branch or detached state, base, reservations, ticket status, assignee, dependencies, and blockers before edits. Work only in the assigned checkout and permitted ticket, test, output, and evidence paths. Do not create a worktree, switch branches, relocate yourself, claim another ticket, or revive a superseded ticket. Preserve unrelated changes and report a conflicting writer, base, dependency, or resource before affected work.

Load only selected language or framework guidance whose documented scope applies to the changed files and implementation stage. Missing optional guidance is not a blocker. Do not install or invent missing guidance. A missing required standard blocks only the affected work and completion claim.

For a revision, begin with changed paths, prior finding IDs and dispositions, affected contracts, reusable evidence candidates, and the cited report sections. Broaden reads only for a concrete caller, contract, regression risk, failure, or project gate. Preserve review history; record each correction or evidence-based disagreement. Never approve findings or set `ready` yourself.

Normally one implementer owns the ticket. Read [controlled delegation](references/delegation.md) only when the coordinator recorded positive `child_capacity` and the ticket contains independently observable behavior or contract packages. Without both facts, do not dispatch children. Different files or spare runtime capacity do not establish independence.

## Implement with TDD

Read and follow the companion [tdd skill](../tdd/SKILL.md) before changing behavior. Observe the focused test fail for the missing behavior, make the smallest implementation pass, run affected regressions, and repeat one behavior at a time. If the test passes immediately, determine whether behavior already exists or the test is weak; do not manufacture a failure. Record any unavoidable test-after deviation honestly.

Implement every layer and required error, validation, and security path in the ticket. Prefer existing code, then the standard library, native platform features, and suitable installed dependencies. Add abstraction or a dependency only for a concrete contract or maintenance need. Fix root causes at the proper boundary and preserve callers' different contracts. Avoid speculative features and unrelated cleanup. Simplicity must not remove required behavior, tests, or safeguards.

Do not ask approval for routine implementation choices. Ask one focused question only when a material product or contract conflict cannot be resolved from the project, ticket, or authoritative documentation.

## Check the implementation

Use the shared [check-scope contract](../setup-workflow/references/check-scope.md) to select initial and revision checks. Run focused tests and typechecking during work. Before handoff, establish current evidence for required non-application tests, build, and configured static checks. For revisions, rerun failed and affected checks and link proven unaffected results; repeat broad suites when impact or project policy requires it. Inspect command side effects first and use only assigned mutable resources and test-suite capacity. If a required command starts the application, run supported non-application suites and record the exact exclusion. Report unavailable commands instead of inventing them.

Check new or changed test names, fixture labels, and identifiers against applicable repository naming rules. Use configured naming checks when present. Correct confirmed violations within the assignment before final checks; do not turn this into repository-wide cleanup.

When a failure introduced by the ticket, accepted review finding, or unsuccessful correction has no established cause, use the [systematic debugging companion](../systematic-debugging/SKILL.md) in implementation mode before another product edit. Preserve the symptom and target, test one hypothesis at a time, and record each materially different root-cause correction attempt. After three unsuccessful corrections for the same symptom, stop editing and return the evidence to the coordinator for architectural reconsideration, ticket replanning, or contract clarification.

Preserve pre-existing, blocked, and unrun results. For a broad race failure observed under concurrency, retain commands, timing, environment, logs, and competing suites; investigate under the original concurrent conditions. A later serial pass does not erase that observation. Required failed or unavailable implementation checks prevent an implemented claim.

Use targeted searches and bounded sections. Put verbose output in the assigned evidence location and return the path plus relevant result; do not paste raw command output into progress, coordinator messages, or handoffs. Update progress only when milestone, next action, blocker, or evidence changes.

## Record and hand off

Update only this ticket's implementation record and permitted lifecycle fields. Preserve requirements, dependencies, and earlier evidence. Write the handoff manifest atomically after cleanup. Record acceptance-criterion coverage, changed paths, implementation location and source identity, TDD evidence, final commands and outcomes, skips and blockers, applied guidance, affected contracts, prior findings, reusable evidence, and owned process/resource state.

Set `status: "implemented"` and a concrete `implementation_ref` only when the slice is complete and required implementation checks pass. Otherwise retain `in_progress`. Leave `available` and `integration_ref` to the coordinator. Preserve `review_ref` during revision; changed code requires new review. Stop owned mutating processes, then make no more code writes until reassigned. Do not update other tickets or the index.

A coordinator-authorized local commit within an explicit run needs no additional user approval when the assignment grants it. Do not push, merge, deploy, rewrite history, or make any other Git change outside the assignment.

Context telemetry is advisory. At a meaningful boundary under pressure, checkpoint the location, checks, blockers, next action, and delegation state. Let the runtime manage compaction. If safe, finish the bounded step and record it first. Continue in the same context after compaction. Use a coordinator-arranged fresh context only when the runtime cannot continue cleanly, after the old owner stops and every child, lease, and resource is reconciled. Never create children as a context workaround or mark partial work implemented.

Return the ticket path, outcome, implementation location, check results, evidence and handoff paths, and remaining limitations. Use short sentences and active voice. After this handoff, a thin coordinator may assign the next ticket in a registered component lane through a new acknowledged assignment. Re-establish that ticket's baseline and boundaries before writing; lane reuse does not combine ticket records or extend the completed assignment.
