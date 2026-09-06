# Verification report and lifecycle

## Location and target

Use the active WORKFLOW.md verification pointer, normally `<workflow>/verification/V-001/REPORT.md`, followed by V-002 and later rounds. Keep it outside the product checkout. Allocate a unique run directory without overwriting another run. Keep its evidence, harnesses, fixture configuration, and resource ledger together. Resolve artifact links from the report, and use exact checkout and canonical spec/ticket paths in handoffs.

Record code revision plus dirty/untracked content identity, spec path and SHA-256, context/configuration sources and identities, selected guidance, and start/end times. Pin what the running application actually loaded: image/build ID or source identity and startup command. Exclude only known run outputs and disposable data from source identity; identify those exclusions. Include runtime configuration identities without exposing secrets.

Recheck the product, spec, and material configuration before the verdict. A target change invalidates affected evidence. Preserve the old run, re-establish a stable target, and rerun affected checks. Do not silently carry an old green result to a new checkout. An interrupted run with incomplete evidence cannot pass.

Reuse an unaffected observation only with recorded impact analysis: its original report, target and evidence links; unchanged criterion, code/dependency path, test setup and material configuration; and why the observation still establishes the result on the new target. If that chain cannot be established, rerun the check. Rerun whole-feature scenarios whose participating components or contracts changed; successful isolated checks cannot replace them.

## Required content

1. **Outcome and scope:** pass, fail, or blocked; target identities; prerequisite readiness; counts of passed, failed, blocked, and justified non-applicable criteria.
2. **Environment:** exact commands and working directories, services, test data, safe provider substitutions, readiness evidence, configuration differences, and resource ledger.
3. **Coverage:** each in-scope REQ and AC, scenario/check, expected result, observed result, outcome, and evidence link. Explain how multiple observations establish a criterion. A non-applicable designation needs a spec-grounded reason; it cannot remove an inconvenient requirement.
4. **Findings:** stable VF-001-style IDs, affected criteria, observed failure, smallest reproduction, evidence, likely affected tickets/code, and requested correction. Distinguish confirmed defects from hypotheses and harness/environment errors. Keep unknown ownership explicit.
5. **Checks and limitations:** existing regressions run, failed attempts, skipped or blocked work, uncovered behavior, and required decisions. Do not copy full unrelated logs into the report.
6. **Cleanup and next action:** resources stopped/removed, resources remaining, cleanup evidence, revision routing, and conditions for another run.

Coverage row example (illustrative, not a required feature):

| Criterion | Scenario | Expected | Observed | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| AC-003 | Write, restart with the same test database, read | Saved value remains | Value missing after restart | fail | Relative trace and response paths |

## Verdict

- **Pass:** all required in-scope criteria have sufficient successful evidence on the stable combined target; prerequisite review/integration gates hold; no unresolved required checks or findings remain. Required runtime flows actually ran. Cleanup is confirmed or resources are deliberately retained under explicit user instruction and documented.
- **Fail:** at least one confirmed product/spec violation. Preserve every additional blocked or unrun check; fail does not imply coverage is complete.
- **Blocked:** no confirmed product violation establishes fail, but an entry gate, required check, decision, target identity, tool, or safe environment is unresolved. Merely finding a suspicious line is not a confirmed runtime failure.

A report may therefore say "fail, with two checks blocked." Optional polish does not block feature verification. A pass is bounded evidence for the stated spec and target, not proof of perfect code, a merge, or a release.

## State ownership and revisions

Do not introduce a ticket status named verified or repurpose available. Preserve ticket files and graph edges. Verification reports own whole-feature outcomes; the assignment coordinator owns `<workflow>/RUN.md`, ticket transitions, and the index. A pass is followed by the coordinator's closure contract, which deletes registered specs only after checking completion gates. The verifier does not delete specs. After closure, report spec digests and former paths are historical provenance, not instructions or live document requirements.

On failure, notify that owner with the report and findings. Affected ready tickets need their completion claims reconciled. The coordinator uses review-ticket's existing re-review entry to assess and record accepted revisions, then returns them through implement-ticket and review-ticket. Do not put a feature report directly into review_ref as if it supplied both ticket-review axes. If a defect has no suitable ticket, report the uncovered spec requirement; the coordinator must arrange a bounded ticket through spec-to-tickets rather than assign untracked implementation or broaden an active ticket.

Keep past ready/review evidence as history even when reopened. After fixes and renewed ticket reviews, establish the new combined target and run feature verification again, including the failed scenario and affected regressions. A spec change needs explicit scope reconciliation; do not cure a failed check by editing expected behavior.
