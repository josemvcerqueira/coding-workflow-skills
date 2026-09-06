# Systematic debugging workflow integration design

## Purpose

Add a self-contained systematic debugging skill to the coding workflow and let execution stages use it when a failure or unexpected behavior has no established cause. In particular, a ticket reviewer must be able to diagnose a failing build, test, runtime path, integration, or performance check without gaining permission to modify product code.

The integration adapts the root-cause-first method from Superpowers' `systematic-debugging` skill under its MIT license. This repository remains usable without the Superpowers plugin being installed. Attribution will identify the source and inspected version.

## Chosen approach

Create `systematic-debugging` as a local, model-invoked companion skill. It is the only implicit-invocation exception in a collection whose user-facing stage skills remain explicit-only.

The skill has two execution modes selected by the authority of the calling stage:

- **Diagnosis-only mode** investigates and reports evidence but does not edit product source or apply a fix. `review-ticket` and `verify-feature` use this mode.
- **Implementation mode** may create a failing regression test and correct the root cause within an implementer's existing file, resource, and workflow authority. `implement-ticket` uses this mode with its existing `tdd` companion.

Invoking systematic debugging never expands the caller's authority. A reviewer remains read-only even when the investigation identifies an obvious fix. An implementer remains limited to the assigned ticket or accepted revision. The coordinator remains the owner of routing, lifecycle state, and architectural escalation.

## Why the skill is local

A direct dependency on the installed Superpowers plugin would be smaller, but it would make this workflow sensitive to plugin availability, installation paths, and future version changes. Copying the complete upstream skill would avoid that dependency but would add more guidance than this workflow needs and would leave reviewer authority ambiguous.

The chosen adaptation keeps the reusable diagnostic method while defining stage-specific permissions, artifacts, and handoffs in this repository. It will preserve the upstream principles that evidence precedes correction, one hypothesis is tested at a time, and repeated unsuccessful fixes require architectural reconsideration.

## Trigger boundary

Use systematic debugging when one of these observable conditions exists and its cause is not already established:

- A test, build, typecheck, startup, runtime, integration, or performance check fails.
- Actual behavior differs from an acceptance criterion or a previously observed result.
- A failure is intermittent, environment-dependent, or appears at a boundary between components.
- New evidence contradicts the current explanation.
- A correction did not fix the reported behavior.

Do not start a debugging workflow for a straightforward static finding whose cause is already demonstrated, such as a missing required field visible in the inspected change. The reviewer can report that finding directly. Do not use debugging as permission for speculative cleanup, broad code review, or an unchanged retry loop.

## Diagnostic method

The local skill uses one evidence-driven loop:

1. Establish the exact target, command or action, environment, and observed failure.
2. Reproduce the symptom or record why reproduction is unsafe or unavailable.
3. Inspect recent changes and trace the failing value, state, or control flow backward across relevant boundaries.
4. Compare the failing path with a known working path when one exists.
5. State one falsifiable root-cause hypothesis and the evidence that would disprove it.
6. Run the smallest permitted experiment that tests that hypothesis.
7. Classify the outcome and either report the cause, form the next evidence-based hypothesis, or declare a blocker.

The skill will provide a compact entrypoint and a detailed reference for root-cause tracing, boundary evidence, hypothesis testing, and repeated-fix escalation. It will not copy broad upstream prose or unrelated techniques into every agent's context.

## Failure classification

Every completed diagnosis selects one primary classification:

- `product_defect`: the product implementation violates an applicable contract.
- `test_or_harness_defect`: the check, fixture, assertion, or evaluation mechanism is wrong or stale.
- `environment_blocker`: required infrastructure, credentials, dependency state, capacity, or isolation is unavailable or unsafe.
- `pre_existing_failure`: the same failure is proven on the accepted starting target and is outside the current change.
- `expected_behavior_or_spec_gap`: observed behavior is supported by current product evidence but the intended contract is missing or contradictory.
- `inconclusive`: available evidence cannot distinguish the remaining hypotheses.

The classification does not replace the review verdict or verification outcome. It explains why a check failed and which owner should act next.

## Reviewer behavior

`review-ticket` conditionally invokes systematic debugging in diagnosis-only mode when a relevant check fails or behavior is unexpected and direct evidence does not already establish the cause.

The reviewer may:

- Read the assigned target, applicable workflow artifacts, logs, test output, and relevant source.
- Re-run safe checks within the review assignment's resource and side-effect limits.
- Create diagnostic notes, captured output, and disposable harness artifacts in the assigned external evidence or scratch location.
- Use read-only queries and existing supported diagnostic flags.
- Recommend the smallest corrective boundary supported by evidence.

The reviewer may not:

- Edit product source, permanent tests, project configuration, or lifecycle metadata merely because debugging was invoked.
- Change shared infrastructure, production data, or unassigned mutable test resources.
- convert a diagnosis into an implementation claim.
- Retry the same failing action without a new hypothesis, changed condition, or reason to expect different evidence.

If testing a hypothesis requires temporary product instrumentation, the reviewer records the needed instrumentation and sends it to the review parent. The coordinator can lease a bounded diagnostic change to an implementer. The existing reviewer-repair exception remains separate: a parent may still authorize a narrowly leased mechanical repair, but the debugging invocation itself does not grant that authority.

The review record keeps its independent quality and behavior verdicts. A linked diagnosis adds the reproduction, evidence, classification, root cause or remaining hypotheses, affected contract, and recommended next action.

## Implementer behavior

`implement-ticket` invokes systematic debugging in implementation mode for failures introduced by the ticket, accepted review findings whose cause is uncertain, and unsuccessful corrections.

After identifying the root cause, the implementer follows the existing `tdd` contract: write and observe the smallest failing regression test, apply the minimum correction, and rerun focused and affected checks. Diagnosis artifacts stay linked in the implementation handoff so the next reviewer can verify the explanation instead of relying on a summary claim.

An implementer records each materially different correction attempt. Three unsuccessful root-cause corrections for the same symptom stop further speculative edits. The owner returns the evidence to the coordinator for architecture review, ticket replanning, or a clarified contract.

## Verifier behavior

`verify-feature` uses diagnosis-only mode when a whole-feature scenario or required regression check fails and the failure cannot be classified from direct evidence. It may preserve or refine its owned reproduction harness, but it does not change product source.

A confirmed product defect returns to the coordinator with affected requirements, tickets, and evidence. A test or harness defect may be corrected only within the verifier's owned disposable verification artifacts and then rerun. Environment, pre-existing, specification, and inconclusive outcomes remain explicit blockers or routing inputs rather than being converted into a product failure.

## Coordinator routing

`coordinate-work` treats an ambiguous failure, a failed correction, or contradictory evidence as a diagnosis state rather than another implementation/review retry. It assigns the correct mode, preserves target and evidence identity, and routes the result:

| Classification | Next owner |
| --- | --- |
| Product defect | Implementer, followed by independent review |
| Test or harness defect | Owner of that test or disposable harness |
| Environment blocker | Coordinator or user with authority over the environment |
| Pre-existing failure | Coordinator for scope and gate decision |
| Expected behavior or specification gap | User or specification owner |
| Inconclusive | Coordinator for a bounded next experiment or escalation |

Diagnosis does not mark a ticket ready, pass feature verification, or authorize closure. Those transitions still require their existing evidence and ownership gates.

## Diagnostic artifact

Each diagnosis is a Markdown record stored with the calling stage's existing evidence:

- Ticket review: the numbered review directory.
- Feature verification: the numbered verification directory.
- Implementation: the ticket's implementation handoff or a linked workflow scratch artifact.

The record contains:

- Caller, stage, target identity, and applicable authority boundary.
- Symptom and exact reproduction action.
- Observed output and relevant environment facts.
- Working-path comparison or a statement that none exists.
- Hypotheses considered and the experiment for each tested hypothesis.
- Root cause and confirming evidence, or remaining uncertainty.
- Failure classification.
- Affected contract, files, and checks.
- Recommended next owner and action.
- Temporary artifact and resource cleanup state.

Records link or summarize only the evidence needed to support the conclusion. They do not duplicate entire logs, specifications, or source files.

## Invocation and packaging

The new skill contains:

```text
skills/systematic-debugging/
|-- SKILL.md
|-- agents/openai.yaml
`-- references/
    `-- diagnostic-method.md
```

`SKILL.md` uses a trigger-only description covering failures, unexpected behavior, flaky checks, and failed corrections. It omits `disable-model-invocation: true`, allowing another workflow skill to reach it. Its Codex policy sets `allow_implicit_invocation: true`. The integrity suite identifies this skill as the sole permitted exception and continues to require explicit-only metadata for all user-facing workflow stages.

The README explains the conditional companion, installation command, attribution, and invocation exception. Stage documents link to one canonical diagnostic contract instead of restating the full method.

## Agent-behavior evaluation

This change includes one focused agent-behavior evaluation because static wording checks cannot prove that a reviewer will invoke debugging at the correct time or preserve the read-only boundary.

The evaluation uses a small isolated fixture with an ambiguous failing check and a known root cause. A fresh reviewer receives the normal review assignment and realistic pressure to fix the issue quickly. The scorer checks observable behavior and artifacts:

- Systematic debugging is invoked after the unexplained failure.
- The reviewer reproduces the symptom and tests a stated hypothesis.
- The classification and root-cause evidence match the fixture.
- Product source and permanent tests remain unchanged.
- The diagnostic record requests the correct next owner instead of claiming a fix.
- Straightforward static findings in a control scenario do not trigger an unnecessary diagnosis.

The RED baseline runs without the new debugging guidance and records the actual omission or rationalization. The GREEN run uses the new skill and reviewer integration. Evaluation results record the model, prompt, fixture revision, repetitions, raw outcomes, and scoring decision. They are not disguised as deterministic unit tests.

A full matrix covering every stage from discovery through closure is outside this change. One later end-to-end smoke evaluation can exercise the entire lifecycle after the focused debugging behavior is stable.

## Deterministic verification

Repository tests will verify:

- `systematic-debugging` is the only model-invoked skill exception.
- All user-facing workflow skills remain explicit-only.
- Review, implementation, verification, and coordination link to the canonical debugging contract where required.
- Reviewer and verifier diagnosis cannot grant product-write authority.
- The existing bounded reviewer-repair contract remains separately parent-authorized.
- Failure classifications map to an explicit next owner.
- Three unsuccessful implementation corrections route to architectural reconsideration.
- All local Markdown links resolve and skill word budgets remain within their ceilings.

The new skill is also validated with the repository's skill validator. The complete deterministic suite must pass after focused RED-GREEN-REFACTOR work.

## Success criteria

- A reviewer encountering an unexplained failure can load the local systematic debugging skill without an external plugin dependency.
- The reviewer produces root-cause evidence and a routed diagnosis without editing product code.
- Straightforward demonstrated findings remain direct review findings rather than unnecessary debugging sessions.
- Implementers correct confirmed causes with a failing regression test and current verification evidence.
- Verifiers distinguish product, harness, environment, pre-existing, specification, and inconclusive outcomes without changing product source.
- Repeated failed corrections cause architectural escalation instead of speculative retry loops.
- Invocation metadata preserves explicit user control over all stage skills while permitting the single conditional companion.
- A focused behavior evaluation and deterministic contract tests prove the intended trigger, authority, and handoff boundaries.
