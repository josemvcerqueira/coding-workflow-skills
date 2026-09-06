# Check scope and evidence reuse

Use this contract when selecting implementation checks, accepting prior review evidence, or repeating feature verification. The stage owner decides which contracts need proof; the worker records the checks and the receiving reviewer or verifier independently validates reuse. A small diff is an input to impact analysis, not proof of low risk.

## Select checks

Before expensive execution, record the changed behavior or finding, affected callers and shared contracts, required project gates, and the smallest checks that establish the result. Use measured previous durations when available to sequence expensive checks; elapsed time never turns a required failure into a pass.

- **Initial implementation:** run focused TDD checks and affected regressions, then the applicable non-application suite, build, and configured static checks. Scope applicability to the ticket's modules and contracts, while retaining mandatory project gates.
- **First independent review:** inspect the actual delta and both review axes; run the required working path and checks whose independent evidence is missing. Inspect reproducible implementation logs and target identity before accepting earlier check results. An implementer's summary alone is insufficient. Duplicate execution adds value only when it tests a missing boundary, resolves uncertainty, or satisfies project policy.
- **Revision or reviewer repair:** compare the last evidenced target with the successor, close each required finding, and rerun failed and affected checks. Reuse successful unaffected evidence under the rules below. Reassess both review axes; a new round or commit alone does not require repeating every command.
- **First feature verification:** exercise the combined target against the full spec, including cross-ticket interactions. Ticket-only evidence cannot substitute for the required integrated runtime flows.
- **Repeated feature verification:** produce a current complete criterion map using new observations and validated unaffected observations from earlier feature runs. Rerun every failed scenario and every whole-feature scenario whose participating behavior or contracts changed, plus affected regressions.

Broaden checks for a changed shared interface, dependency, runtime configuration, migration, authorization rule, concurrent state, or build/test setup; an unexplained failure; uncertain impact; or a mandatory project gate. Identify the affected surface first. Run the full applicable suite when narrower coverage cannot bound it or project policy requires it. File count, line count, and severity labels alone do not establish check scope.

## Reuse proof

For each reused result, link its original report/output and record:

1. The prior exact source identity and the delta to the current target, including dirty and untracked inputs when relevant.
2. The covered criterion or contract, reproducible command/action, result, and test/build inputs.
3. Why the relevant code and dependency path, fixtures, environment, material configuration, and expected behavior remain applicable. Changed test labels can preserve behavioral evidence but still need the naming check and a focused collection/run check when selection depends on names.
4. The receiving reviewer/verifier's explicit acceptance and any limits. Group checks only when they share the same impact argument; keep their evidence discoverable.

Successful outputs need not be rerun merely because another file or commit changed. Missing logs, unknown source identity, changed relevant inputs, or an unproven impact boundary require new checks. A prior failure is never reusable as success. Preserve it and rerun the failing check after its cause is corrected; a different passing check does not erase it.

Record reused checks as carried evidence, not newly executed commands. Required unavailable checks remain blocked. Optional polish may remain open without delaying readiness. Required behavior, standards, and safety defects must be resolved before the affected ticket becomes ready.

## Failure and cost control

Classify a failure as product, harness, environment, or demonstrated unrelated pre-existing behavior before choosing a correction. Preserve the failed attempt and evidence for any changed applicability decision. A race under concurrency needs investigation under the original concurrent conditions; a serial pass alone cannot clear it.

Batch compatible known corrections within the same ticket before the next expensive run, using focused checks during edits. Stop unchanged retry loops and diagnose the cause. Defer a broad check to the combined feature stage only when no earlier project/ticket gate requires it and current scoped evidence is sufficient for readiness; record the future check and owner explicitly. Deferral is not a pass or permission to integrate known broken behavior.

## Decision examples

| Evidence and delta | Required next action |
| --- | --- |
| A one-hour suite passed; only an explicit test-naming rule failed | Eligible mechanical reviewer repair, rerun naming and any affected collection/reference check; retain unaffected suite results with reuse proof. |
| One assertion failed; the fix changes a pricing calculation | Implementer adds or tightens the behavior regression, fixes it, reruns the failure and affected callers; independent review checks the delta. Reverify affected integrated flows. |
| An authorization fix is one line | Treat its shared security contract as high impact; inspect callers and run relevant permission/tenant regressions, expanding coverage when impact is uncertain. |
| A concurrent race failed; a serial retry passed | Preserve the failure, diagnose under the original concurrent conditions, and prove the correction there before accepting the affected claim. |
| An earlier feature run passed most criteria; a local fix changes one workflow | Rerun the failed and affected integrated scenarios; carry only proven unaffected observations into a new complete feature report. |
| Earlier green logs identify only a branch, or runtime configuration changed without an identity record | Re-establish a stable target and rerun the checks whose provenance or applicability cannot be verified. |
