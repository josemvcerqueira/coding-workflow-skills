# Diagnostic method

Use this contract after the `systematic-debugging` trigger matches. It defines investigation and handoff. It does not grant a new file lease, mutable resource, external action, lifecycle transition, or product decision.

## Select the mode

The calling stage is authoritative:

| Caller | Mode | Permitted result |
| --- | --- | --- |
| Ticket reviewer | Diagnosis-only | Review evidence and a routed diagnosis; no product source or permanent-test edit. |
| Feature verifier | Diagnosis-only | Verification evidence, owned disposable harness corrections, and a routed diagnosis; no product source edit. |
| Ticket implementer | Implementation | A root-cause correction and regression test within the assigned lease, followed by current checks. |
| Coordinator | Routing only | Assignment, classification disposition, and escalation; no implementation by the coordinator. |

A diagnosis-only caller can create notes, captured output, and a reproduction in its assigned external evidence or scratch location. It can run safe checks and use existing diagnostic flags within its resource limits. If a hypothesis requires product instrumentation, record the exact instrumentation needed and return it to the coordinator or implementer. Do not edit the product temporarily and then restore it; that still exceeds diagnosis-only authority.

The ticket reviewer's separately documented bounded reviewer repair remains parent-authorized. Invoking debugging does not grant that repair, and a semantic correction never qualifies for it.

## Establish the failure

Record before experimenting:

- Calling stage and mode.
- Repository, checkout, baseline, target, and dirty-content identity when applicable.
- Exact command or user action, working directory, relevant configuration, and assigned resources.
- Expected result and its contract source.
- Actual result, timestamp, output location, and whether the failure is stable or intermittent.

Reproduce the smallest real boundary that still shows the symptom. If reproduction would spend money, contact production, mutate shared data, use unavailable credentials, or exceed the caller's authority, stop and record the blocker. A later pass under different conditions does not erase the original failure.

## Collect root-cause evidence

Read the complete error and the responsible path before proposing a correction. Inspect relevant recent changes, configuration, dependencies, and environment differences. Do not broaden into an unrelated audit.

At each component boundary, capture enough evidence to answer:

- What value, state, or request entered the boundary?
- What left it?
- Which configuration and version controlled the transformation?
- Where does the first observed divergence from the expected path occur?

Trace the bad output backward to its producer. When a working path exists, compare inputs, versions, ordering, permissions, and environment. List differences before choosing one as causal.

For concurrency or intermittent failures, preserve timing, competing operations, resource identities, and the original conditions. Repeating the check serially can be a useful experiment, but a serial pass is not proof that the concurrent failure was harmless.

## Test one hypothesis

Write one statement in this form:

> The symptom occurs because **cause**, supported by **observation**. If this is correct, **small experiment** will produce **predicted result**; otherwise this hypothesis is rejected.

Change one variable or observation boundary. Prefer read-only instrumentation, a focused existing check, a disposable reproduction, or a comparison against the accepted baseline. Do not bundle fixes. Record the result even when it rejects the hypothesis.

If the result is ambiguous, improve the experiment before changing the product. If it rejects the hypothesis, form the next hypothesis from the new evidence. If no safe discriminating experiment exists, return `inconclusive` with the missing evidence or authority.

## Classify and route

Choose one primary classification after the evidence loop:

| Classification | Meaning | Next owner |
| --- | --- | --- |
| `product_defect` | Product behavior violates an applicable contract. | Implementer, followed by independent review. |
| `test_or_harness_defect` | A test, fixture, assertion, or evaluation mechanism is wrong or stale. | Test or harness owner. |
| `environment_blocker` | Required infrastructure, credentials, dependency state, capacity, or isolation is unavailable or unsafe. | Coordinator or user with environment authority. |
| `pre_existing_failure` | The same failure is proven on the accepted starting target and is outside the current change. | Coordinator for scope and gate disposition. |
| `expected_behavior_or_spec_gap` | Current behavior has supporting product evidence, but the intended contract is missing or contradictory. | User or specification owner. |
| `inconclusive` | Available evidence cannot distinguish the remaining hypotheses. | Coordinator for a bounded next experiment or escalation. |

Classification explains the failed check; it does not decide the calling stage's verdict. A confirmed product defect normally creates or supports a required finding. An environment blocker does not become a product rewrite. A pre-existing failure does not disappear and does not automatically block an unrelated ticket; coordination applies the repository's scope and gate policy.

## Correct only in implementation mode

An implementer with an accepted product defect follows the existing TDD contract:

1. Write the smallest regression test that reproduces the confirmed cause at the appropriate observable boundary.
2. Run it and verify the expected failure.
3. Apply one root-cause correction within the assigned lease.
4. Run the focused test and affected checks.
5. Record the hypothesis, correction, and result as one attempt.

A failed correction starts a new evidence loop, not a larger guess. After three unsuccessful root-cause corrections for the same symptom, stop product edits. Return all three attempts and discriminating evidence to the coordinator for architectural reconsideration, ticket replanning, or contract clarification.

## Diagnosis record

Store the record with the calling stage's existing evidence. Use this shape:

```markdown
# Diagnosis D-001

- Caller and mode:
- Target identity:
- Authority and resource limits:
- Symptom and contract:
- Reproduction action:
- Evidence locations:
- Working-path comparison:
- Hypotheses and experiments:
- Root cause or remaining uncertainty:
- Classification:
- Affected contracts, files, and checks:
- Recommended next owner and action:
- Correction attempts, if implementation mode:
- Temporary artifacts, processes, and cleanup:
```

Use a stable local diagnosis ID. Link large logs instead of copying them. State unavailable evidence and unrun checks. Do not claim cleanup, reproduction, root cause, or correction without current supporting evidence.
