# Workflow cohesion audit — 2026-09-06

The collection has a coherent purpose: turn product intent into a precise spec, independently verifiable slices, reviewed code, and evidence that the combined feature works. The main friction was conflicting execution rules and incomplete handoffs, rather than missing stages. This audit used three parallel agents plus a parent review of the remaining skills and shared contracts. Existing uncommitted work was the baseline and was preserved.

The right optimization target is time and cost per verified outcome. Maximizing ticket count, agent count, or context utilization can make that worse. A fivefold improvement is an aspiration; this audit does not establish a measured speedup.

## Findings and changes

| Finding in the working-tree baseline | Consequence | Change |
| --- | --- | --- |
| Implementation demanded the full applicable suite after the last edit; re-review permitted selective reuse. Behavior review also limited reuse to the current round. | A mechanical fix could restart expensive work despite sufficient evidence. | One [check-scope contract](../../skills/setup-workflow/references/check-scope.md) now governs implementation, review, repeated verification, and closure. Failed and affected checks run again; unaffected successful evidence needs explicit provenance and impact proof. |
| Ticket sizing could hard-fail new tickets on counts of criteria, spec references, and exclusive resources. | One atomic behavior with many invariants could be rejected, while a vague oversized behavior could pass. | Counts are advisory. [Ticket planning](../../skills/spec-to-tickets/SKILL.md) evaluates the observable path, uncertainty, real dependencies, and verification cost. |
| Three draft passes were mandatory even for small ticket sets. Active resizing required user intervention. | Planning overhead and unnecessary approval loops. | A proportional draft challenge; coordinator-managed replanning after writers stop and evidence/coverage are reconciled. |
| Specs and tickets did not clearly separate focused acceptance checks from expensive integrated scenarios. | Every slice could inherit the same broad verification cost. | Spec template, context command map, and ticket format distinguish focused checks, combined scenarios, required gates, and known versus unknown costs. |
| Feature failures returned through review before implementation, then review again. | Confirmed defects paid for an unnecessary reviewer dispatch. | The review parent can accept an evidenced defect directly into a revision record. Uncertain findings get diagnosis; corrections still receive independent review. |
| Coordinator goal instructions implied automatic goal creation; scheduling could terminate a stage for context size. | Host-tool conflict and avoidable handoff churn. | Goal creation requires explicit authority. Runtime compaction preserves ownership and pending commands; semantic checkpoints support recovery. |
| Coordinator guidance lacked a concrete recovery choice and could repeatedly reload validation, worker instructions, and telemetry. | Repeated attempts, excess reads, and state write overhead. | [Recovery](../../skills/thin-coordinator/references/run-state.md) chooses reconciliation, diagnosis, repair, replanning, or a real user decision. Scheduling reuses unchanged validation while checking live safety; telemetry stays in telemetry storage. |
| Verifier did not explicitly write the handoff required by its coordinator; shared outcome vocabulary could not express a failed verification. | A report could exist without the expected transition evidence, or failure could be mislabeled. | Verifier writes the assigned manifest after cleanup. The [shared handoff](../../skills/setup-workflow/references/handoff-manifest.md) distinguishes success gates, revision required, failed, and blocked. |
| Reopening an integrated ticket cleared readiness while leaving a live integration reference that the validator permits only on ready, available work. | Correction routing could immediately produce invalid metadata or stale integration claims. | The coordinator invalidates current availability/integration fields during reopening and preserves the old integration manifest as historical evidence. |

## Skill-by-skill assessment

| Skill | Assessment |
| --- | --- |
| setup-workflow | Appropriate foundation and scope. Keep read-only project exploration separate from execution. Added known selectors, required gates, capacity, and measured cost to its command map. |
| setup-project-context | Small compatibility wrapper; retain while the old entrypoint is supported. No second setup implementation. |
| make-it-clear | Cohesive explanation helper; correctly preserves the active task and does not create another lifecycle. No change needed. |
| shape-the-idea | Sound ownership of product decisions and factual research. Shortened repeated writing guidance and avoided full brief rewrites after each answer. |
| write-the-spec | Correct owner of behavior, contracts, and whole-feature scenarios. Added verification boundaries/cost inputs without prescribing tickets. |
| backend-architecture | Useful conditional companion. Existing guidance already resists speculative infrastructure and requires evidence for consequential design choices. No new architecture stage needed. |
| spec-to-tickets | Highest-value intervention. Added useful-outcome sizing, a real starting-base check, anti-fragmentation guidance, acceptance ownership, and safe replanning. |
| implement-ticket | Keep one owner and behavior-focused TDD. Removed unconditional broad reruns on revisions through the shared check policy. |
| tdd | Existing red/green cycles, honest exceptions, and contract tests fit the workflow. Its caller controls final checks, so no duplicate scope policy needed. |
| review-ticket | Keep independent quality and behavior assessment, one reviewer by default, and risk-based escalation. Preserve bounded mechanical repair and remove contradictory reuse rules. |
| verify-feature | Necessary separate gate for combined behavior. Clarified repeated-run evidence and completed its handoff contract. |
| thin-coordinator | Keep scheduling, reservations, integration, lifecycle ownership, and recovery. Detailed implementation and diagnosis remain with workers. It cannot safely be only a status/healing agent. |

## Ticket boundaries in practice

For saved filters, create, list, and delete may be three useful outcomes. Each includes its necessary data, API, interface, failure handling, and checks. Existing authentication does not make a new storage schema available: consumers depend on the slice that supplies it. A list-action deletion depends on a usable list. A seeded test is useful once the real schema exists; a mock of a future producer does not prove a working production path.

Keep one atomic payment outcome together even when it has eight correctness invariants. Separate payment methods or independent journeys when useful, rather than postponing authorization or idempotency. If every fragment is unobservable alone and needs the same hour-long check, combine the fragments and retain the honest check cost. See [slicing examples](../../skills/spec-to-tickets/references/slicing.md).

## Size and context

The baseline contained 12,416 words in skill entrypoints and approximately 36,200 across entrypoints and references. Total library size is not the same as the material an assignment loads. The coordinator's scheduling, run-state, and optional dashboard references dominate its potential read cost.

This pass kept the existing 1,800-word entrypoint ceiling and 1,600-word orchestration ceilings. It reduced the coordinator entrypoint from 1,312 to 1,300 words and kept ticket planning within its ceiling. The shared check policy adds a necessary contract; it replaces conflicting instructions rather than claiming an overall word-count reduction. Conditional references stay conditional. The useful next measure is actual reads and repeat work per stage, not a universal token limit.

## Scenario evaluation and verification limits

Agents cross-evaluated other agents' edited instructions using concrete scenarios:

- A passed hour-long suite plus a required naming correction: leased mechanical repair, affected naming/collection checks, and justified carried evidence; no automatic full rerun.
- A one-line authorization correction: failed tenant/permission checks and affected callers run again, with security review and affected integrated flows. Diff size cannot waive these.
- Old green logs without source identity, or changed test configuration: re-establish provenance and rerun checks whose applicability cannot be proved.
- A concurrent failure followed by a serial pass: retain and investigate the original concurrent failure.
- A pricing defect in final verification: accept the evidenced revision, fix and independently review it, then rerun failed/affected integrated scenarios and produce a complete current criterion map.
- Context pressure during a healthy long test: preserve pending session, command, evidence, and reservations; reconcile the same process after compaction instead of restarting it.
- Repeated unsuccessful repairs or a new material spec change: diagnose or stop affected owners and reconcile the remaining graph; do not dispatch overlapping replacements.
- Atomic payment, schema-dependent CRUD, and fragments sharing an expensive suite: maintain genuine observable boundaries rather than forcing parallelism.

These were instruction-driven scenario walkthroughs, not executions of a product workflow. Existing phrase-presence tests passed despite the original contradictions; they cannot establish semantic cohesion. Mechanical checks cover document links, invocation metadata, entrypoint size, validator behavior, and dashboard regressions. The baseline full suite passed 140 tests. The final full run of `python3 test_all.py` passed 145 tests in 4.798 seconds; the total includes concurrent dashboard work outside this audit. The final lifecycle wording also received focused integrity/review checks and a validator-fixture exercise: clearing current integration claims before reopening leaves valid metadata, blocked consumers, and unchanged historical manifest bytes.

## Remaining tradeoffs and measurement

The prohibition on implementation-stage application startup is deliberate: reviewers/verifiers supply real-path evidence. It can delay feedback for UI-only behavior. Measure whether that separation causes extra returns before changing stage authority; focused in-process checks cannot be mislabeled as live verification.

Spec deletion at verified closure remains the collection's existing policy. Historical evidence is retained, but it is not maintained product requirements. Teams that need permanent operational or business documentation must identify it as a product deliverable; do not reconstruct a hidden replacement spec through this audit.

The optional standards catalog remains absent and honestly reported. Adding a language catalog or another orchestration skill would not resolve the observed loops. Scoped, explicitly selected guidance and host-tool authority still govern companion use.

Use the next comparable feature runs to measure ticket completion time, time waiting for dependencies/resources, implementation and check durations, review returns and causes, repeated broad checks and their reason, and work repeated after compaction. Use existing assignment timestamps and optional measured check durations; record unavailable data rather than infer it. Compare comparable scope and environments, alongside escaped defects and integration failures. Only that evidence can support a claim such as fivefold improvement.
