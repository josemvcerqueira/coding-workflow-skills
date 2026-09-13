# Check scope and evidence reuse

Use this contract when selecting implementation checks, accepting prior review evidence, or repeating feature verification. The stage owner decides which contracts need proof; the worker records the checks and the receiving reviewer or verifier independently validates reuse. A small diff is an input to impact analysis, not proof of low risk.

## Select checks

Before expensive execution, record the changed behavior or finding, affected callers and shared contracts, required project gates, and the smallest checks that establish the result. Run applicable cheap preflight and generated-contract checks before expensive suites when dependencies permit. Use measured durations to sequence checks; elapsed time never turns a required failure into a pass.

- **Initial implementation:** run focused TDD checks and affected regressions, then the applicable non-application suite, build, and configured static checks. Scope applicability to the ticket's modules and contracts, while retaining mandatory project gates.
- **First independent review:** inspect the actual delta and both review axes; run the required working path and checks whose independent evidence is missing. Inspect reproducible implementation logs and target identity before accepting earlier check results. An implementer's summary alone is insufficient. Duplicate execution adds value only when it tests a missing boundary, resolves uncertainty, or satisfies project policy.
- **Revision or reviewer repair:** compare the last evidenced target with the successor, close each required finding, and rerun failed and affected checks. Reuse successful unaffected evidence under the rules below. Reassess both review axes; a new round or commit alone does not require repeating every command.
- **First feature verification:** exercise the combined target against the full spec, including cross-ticket interactions. Ticket-only evidence cannot substitute for the required integrated runtime flows.
- **Repeated feature verification:** produce a current complete criterion map using new observations and validated unaffected observations from earlier feature runs. Rerun every failed scenario and every whole-feature scenario whose participating behavior or contracts changed, plus affected regressions.

Broaden checks for a changed shared interface, dependency, runtime configuration, migration, authorization rule, concurrent state, or build/test setup; an unexplained failure; uncertain impact; or a mandatory project gate. Identify the affected surface first. Run the full applicable suite when narrower coverage cannot bound it or project policy requires it. File count, line count, and severity labels alone do not establish check scope.

## Execute checks and recover setup

Use assigned absolute workflow/output paths, separate from the code checkout. Before a harness starts, verify each pin against its named input: spec digest against the spec, source-manifest digest against that manifest, and candidate identity against the code. Report the mismatched input; do not weaken a pin to make startup pass.

Before an expensive application or service run allocates resources, close readiness for the exact
target and harness identity with one collect-all gate. Continue every independently safe readiness
check after another fails and retain one report containing all discovered failures; dependency-blocked
checks remain unrun. A failed gate proves that it created no process, container, network, volume,
mutable data path, or browser profile and cannot fall through to a startup timeout.

For a reusable runtime harness, readiness closes four boundaries:

- every required runtime artifact, image, executable, and dependency is present by exact identity or
  has one explicit acquisition/build owner;
- every build context, configuration path, working directory, and required input resolves from
  explicit permitted roots rather than the caller's current directory;
- the code and configuration under test are protected by exclusive writer ownership or an immutable
  content-addressed snapshot, with identity checked again before publishing acceptance;
- the real failure-publication and cleanup path has deterministic fault-injection proof that status,
  logs, exit code, timings, and cleanup evidence survive a failed run.

Run host-dependent artifact and path checks for each resolved run. Run deterministic failure-path
tests when the harness or publication path changes and bind their result to that harness identity;
do not inject a deliberate failure into every product run. A harness correction is not ready for
another expensive attempt until focused regressions force each defect, a combined regression proves
the collect-all result, and any required independent review passes.

Every readiness wait observes both the ready condition and the exact process, task, or container that
can satisfy it. A terminal owner fails immediately and preserves its output; it never consumes the
remaining timeout after success has become impossible. Prove required runtime packages and production
commands before startup so a missing executable cannot become a long readiness wait.

The first deterministic harness-caused failure leaves product acceptance and enters bounded harness
diagnosis against the same focused target. Preserve the failure, collect all independently
discoverable setup defects, correct one frozen batch, and review the affected harness seams. After two
harness-caused failures for the same candidate, the circuit is open: no further expensive acceptance
attempt is eligible until the correction and any required independent review pass. Diagnostic probes
remain non-accepting evidence.

For background execution, retain the tool's task/session handle and consume its terminal result. If no handle exists, track the launched child PID plus start identity and capture its exit status. Never infer liveness from `pgrep -f` or script-name matches: the polling shell can match itself. Logging wrappers must propagate the check's exit code. Await terminal results before handoff; compaction or a worker turn ending is not command completion.

Give each setup/check attempt a distinct evidence path with its command, input identities and result. Preserve failed logs before correcting a harness. After a setup failure, reconcile owned resources and unchanged source, apply only coordinator changes acknowledged under [live instruction delivery](../../thin-coordinator/references/run-state.md#live-instruction-delivery), and retry only the affected setup/check after a diagnosed condition changes. Keep the current assignment and valid evidence.

For review, the second failed setup attempt after that recovery, or an explicit coordinator checkpoint, reaches the setup-recovery boundary. Start no further setup attempt. Let a healthy in-flight command reach its terminal result unless a safety or explicit stop instruction requires otherwise; a time checkpoint alone does not interrupt it. Preserve findings, command results and evidence paths, candidate identity, outstanding acceptance checks, and owned resource and cleanup state. Produce the current review handoff with every unavailable requirement and verification explicitly `blocked`, and route further repair to the responsible harness owner under [systematic debugging](../../systematic-debugging/SKILL.md). Keep completed review work and acceptance criteria intact; do not restart the whole review, retry by replacing the reviewer, or weaken a required check.

## Reuse proof

For each reused result, link its original report/output and record:

1. The prior exact source identity and the delta to the current target, including dirty and untracked inputs when relevant.
2. The covered criterion or contract, reproducible command/action, result, and test/build inputs.
3. Why the relevant code and dependency path, fixtures, environment, material configuration, and expected behavior remain applicable. Changed test labels can preserve behavioral evidence but still need the naming check and a focused collection/run check when selection depends on names.
4. The receiving reviewer/verifier's explicit acceptance and any limits. Tools can validate identities and coverage mappings; the independent reviewer/verifier judges semantic impact. Group checks only when they share the same impact argument; keep their evidence discoverable.

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
