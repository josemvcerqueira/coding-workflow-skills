---
name: tdd
description: Use when the user explicitly requests this skill for test-first implementation or bug fixing. Also serves as the required testing reference for implement-ticket.
license: MIT
disable-model-invocation: true
---

# Test-driven development

Use this method during coding, in the same agent and context as the implementation task. It is not a later testing stage. The calling task controls scope, permitted commands, and completion state. This skill does not start reviews, launch the application, or create commits. In a coordinator-approved delegation group, each child applies these cycles in its own assigned agent and context, only for its leased behavior boundary; the ticket owner remains responsible for integration and final evidence.

## Select the behavior and boundary

Read the relevant acceptance criteria, existing tests, project instructions, and applicable architecture decisions. Use the project's domain terms, including the external context supplied by the assignment when present. Keep scratch evidence in the assigned external workspace; permanent tests and source edits remain in the product checkout. This helper does not create or discover a separate workflow.

Identify the next required behavior and the public interface where its result can be observed. A public interface can be a module function or component interface; it need not be an HTTP endpoint. Use boundaries specified by the ticket or spec. If none are specified, choose the smallest existing boundary that proves the required behavior. State the choice briefly. Ask only when the choice requires an unresolved product or contract decision. A delegated child must stay within the coordinator-recorded file lease, interface contract, and its own isolated test resources. It must stop and report a discovered cross-boundary dependency instead of changing a shared contract or another child's work.

Read [test design](references/test-design.md) before writing tests. Read [test doubles](references/test-doubles.md) when a test needs to replace a dependency.

## Run one cycle at a time

1. Write one focused test for the next behavior. For a bug, reproduce the reported failure. Name the observable result and identify what defect the test should detect.
2. Run the test before changing production behavior. Inspect the failure. It must show the missing behavior, not an unrelated setup problem. A missing required interface can be the initial failure; then establish a behavioral assertion as implementation becomes possible.
3. Implement enough to satisfy that behavior and its contract. Do not add speculative features. Run the test again and fix the implementation until it passes.
4. Run affected regression tests. With tests green, make only small local refactors needed for clarity or the current change. Rerun affected tests after each refactor.
5. Select the next required behavior and repeat. Do not write a large batch of tests and then a large batch of implementation.

Cover required success, failure, and boundary cases. Choose additional cases by the risk of incorrect behavior, not by a target test count or one test per private method. Keep focused test runs fast enough to use throughout coding.

## Handle exceptions honestly

If a new test passes immediately, determine whether the behavior already exists or the test misses the defect. Preserve existing correct code. Do not manufacture a failure. Record existing coverage separately from an observed test-first cycle.

If you changed behavior before testing, report that deviation. Add a meaningful regression test and, where safely possible, demonstrate its failure against the previous behavior in an isolated copy. Do not erase user changes or describe tests written afterward as TDD.

If tests cannot run, resolve the setup problem within scope or report the blocker. Do not guess a red or green result. Do not weaken valid assertions, skip failures, or add production bypasses for tests. Non-behavioral changes use applicable validation; a configuration change that affects behavior still needs behavioral coverage.

## Keep evidence

Record the focused test command, observed failure reason, and passing result in the task's existing implementation record. Summarize by behavior; do not copy large logs. Record unrun checks and limitations. In a delegation group, a child records its milestone, red/green summary, blocker, and file lease in the dashboard-compatible child progress record. It records detailed red/green evidence, changed leased paths, reserved-resource/process cleanup, and its handoff in the registered child handoff; resource reservations remain in `RUN.md`. It does not edit ticket lifecycle fields or the final implementation record. After every child has stopped, the parent inspects the handoffs, runs cross-boundary and required final checks, and records the combined evidence in the single ticket implementation record. Rerun affected tests after the final change, then follow the calling task's final build and test requirements.

Use short sentences, active voice, and consistent technical terms based on STE principles. Do not claim formal ASD-STE100 compliance.
