# Monotonic review closure

Use this contract for every first review, correction, successor review, integration acceptance, or
release-gate acceptance. A task without a review stage does not gain one from this contract.

## Freeze the first review

Before dispatch, the review parent records one closure file beside the review reports. Freeze the
acceptance contract, exact source identity, evidence matrix, changed and directly affected seams,
explicit exclusions, and deferred work. Missing or stale inputs make the review non-dispatchable.

The first full review returns one atomic, deduplicated finding batch. The parent accepts, rejects with
evidence, defers, or escalates each finding, then gives the implementer one coherent correction
containing the complete accepted blocker set. The correction adds no new requirements.

## Bound successor review

A successor review checks only:

1. every accepted blocker;
2. regressions caused by the correction; and
3. unchanged-source continuity for carried evidence.

Previously accepted work remains accepted unless the reviewer demonstrates that the correction
regressed it. The successor still uses a fresh context independent of implementation. Reuse the same
frozen checkout and valid check artifacts when their exact identities remain unchanged.

Classify successor observations as:

- `BLOCK`: a named blocker remains, the correction introduced a material regression, or required
  frozen evidence is missing;
- `DEFER`: a pre-existing issue, unrelated concern, optimization, hardening idea, or new requirement
  falls outside the frozen correction;
- `ESCALATE`: credible security, financial-integrity, data-loss, or similarly critical harm needs
  owner attention even outside the correction surface.

A block cites the frozen requirement, reproducible failure, material impact, and why it belongs to
the correction surface. An observation or improvement idea cannot change lifecycle state by itself.

## Exit and loop bound

When every named blocker and required matrix entry passes with no correction-caused or critical
defect, the reviewer recommends pass and the parent advances lifecycle. After one correction and one
successor review, another newly discovered blocker does not start an automatic round. The parent
records a disposition: accept within existing scope, defer to a new ticket, re-scope, or redesign.
Ask the user only when that disposition changes the product contract, task scope, or recorded
authority. A still-unresolved named blocker or critical escalation follows the same disposition gate.

Reviewers recommend dispositions; only the parent changes task, ticket, integration, or release state.
The closure file keeps:

```yaml
acceptance_contract:
source_identity:
full_review_findings:
accepted_findings:
open_blockers:
successor_review_surface:
deferred_findings:
critical_escalations:
automatic_successor_rounds_remaining: 1
exit_condition:
owner_decision_required: false
```

`full_review_findings` never grows during successor review. Decrement the allowance after its one
review and never let a reviewer reset it. Source, contract, or closure-file drift requires the parent
to freeze a corrected, authorized record before another review.
