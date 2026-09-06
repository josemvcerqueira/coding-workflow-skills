# Review record and decisions

Use `<workflow>/reviews/<ticket-id>/R-001.md`, then the next unused round number. Its path from a ticket is normally `../reviews/<ticket-id>/R-001.md`. Supporting logs or reproductions may live beside the report. Link from the ticket; do not paste long logs into its body. Preserve old rounds and finding IDs when findings recur.

Each report contains:

- Ticket and spec links; date; coordinator and reviewer identities.
- Baseline, target identity, included paths, spec digest, and relevant standards sources.
- Separate Quality and standards and Spec and behavior sections. Each has its outcome, findings, executed checks, evidence links, and limits.
- A criterion-to-evidence map for the ticket, with pass, fail, or blocked results. State why a check is not applicable when necessary.
- Coordinator dispositions for each finding: accepted-required, repaired-by-reviewer, optional, rejected-with-evidence, or unresolved. Preserve the reviewer's original concern when disagreeing.
- Reviewer repairs, when used: finding ID, eligibility evidence, granted lease, before/after source identities, changed paths, exact correction, smallest meaningful post-edit checks, explicit skips, and cleanup state. Use disposition `repaired-by-reviewer` only after the parent verifies this evidence.
- Final decision, lifecycle transition, availability evidence, remaining blockers, and handoff action.

Use IDs such as `Q-001` and `B-001`. A required finding includes location, evidence, a violated contract or demonstrated maintenance cost, requested correction, and expected verification. Complexity scores, code-smell counts, and generic thresholds are advisory inputs and cannot make a finding blocking without that contract or cost. Severity describes impact; required/optional decides whether it blocks. Do not use a severity cutoff that silently accepts a real acceptance-criterion defect.

## Decision table

| Evidence on the current target | Ticket state | Next action |
| --- | --- | --- |
| Both axes pass; required verification passes; no unresolved blocking findings | `ready` | Verify availability and refresh downstream candidates. |
| A confirmed required code or test correction remains | `revision_required` | Implementer fixes accepted findings, then submits a new review. |
| Required check, reviewer, access, or material decision is missing; no confirmed correction yet | `in_review` | Record blocked review and the concrete resumption action. |

An optional improvement does not prevent readiness. A concern can be rejected only with evidence and a recorded reason. Obtain the reviewer's reassessment of a material disagreement; unresolved disagreement is not a pass. Do not overrule a supported finding because the deadline is close.

Use [bounded reviewer repair](reviewer-repair.md) for an explicit and unambiguous mechanical correction that does not change production behavior and does not delete or weaken a test. Severity alone is not the gate. After the smallest meaningful checks pass, the parent may accept `repaired-by-reviewer` and finish the same review round. A qualifying repair needs no second reviewer solely because of the repair. Failed eligibility, an unexpected delta, or insufficient verification returns the finding to the implementer.

If a reviewer fails, times out, or returns an incomplete report, retry that role through the available agent mechanism. Save progress if it cannot finish. Do not count an absent review as a pass.

## Reopening and invalidation

Before the review parent changes a `ready` ticket to another status, or records `revision_required`, check `available` and `integration_ref`. When availability is true or an integration reference is present, synchronize with the assignment coordinator. That owner records the reason and affected consumers, preserves the former integration manifest path in the review/run history, and atomically sets `available: false` and `integration_ref: null`. Keep the manifest file and prior reports intact. An integration reference is valid only on ready, available work; clearing only availability leaves invalid metadata. Already false/null fields need no invalidation or coordinator wait; proceed under verified review ownership, resolving any competing writer first.

Within `coordinate-work`, the same parent owns any needed invalidation and the following status transition. When invalidation is needed, a standalone review parent requests and verifies the owning coordinator's update before writing status; sequence ticket/index writes so there is one writer at a time. If that owner is unavailable, retain current metadata, save the finding and blocked transition in the review handoff, and report the affected completion claim as disputed until reconciliation. Do not leave contradictory lifecycle fields or silently assume coordinator ownership. Ordinary ownership recovery can resume the transition after its prerequisites hold.

## Revision handoff

After confirming `available: false` and `integration_ref: null`, set `revision_required` and keep the concrete implementation reference as the reviewed location. Preserve prior review rounds. The assignment coordinator sets `in_progress` and confirms the implementer before work resumes. Do not auto-dispatch from this skill.

Send the implementer the exact ticket, review, and handoff-manifest paths; accepted required finding IDs; affected contracts; relevant evidence; and required rechecks. The implementer follows `implement-ticket` and its TDD companion. It records each fix or evidenced disagreement, runs implementation checks, updates `implementation_ref`, and returns `implemented`. It cannot self-certify `ready` or close findings as reviewer-approved.

For a confirmed integration or feature-verification defect, the coordinator acting as review parent may record the supported finding, invalidate availability/integration as above, and set `revision_required` directly. Link the feature report and reproduction in a new ticket review record; record the behavior-axis defect and retain the prior quality-axis evidence with its known limits. Dispatch a diagnostic reviewer before the fix only for uncertainty or dispute. This disposition accepts a correction, not a new review pass. The implementation correction still requires independent review of both axes before readiness.

For re-review, the coordinator supplies changed paths, prior finding IDs and dispositions, affected contracts, and reusable evidence candidates. Re-review both axes on the new target with the coordinator's current risk-based reviewer count. Start with that delta and apply the shared [check-scope contract](../../setup-workflow/references/check-scope.md). Record new checks separately from independently validated carried evidence, with a concrete reason for broader execution. If the same blocker remains after a fix attempt, diagnose or clarify the missing decision; do not repeat an unchanged implement/review loop.

## Completion and scheduling

`ready` means this ticket's review and verification are complete. `available` separately means its implementation is usable in the consumers' agreed base. A ready ticket may remain unavailable. In that case, report the integration handoff, not a newly unblocked dependent.

Do not remove files, dependency edges, or prior reports to close a ticket. The index keeps all ticket rows and separates open work from completed work. Derive unblocks and candidates from metadata. A dependency satisfied today remains recorded for later regression analysis.

If a completed prerequisite is reopened, identify its consumers through metadata. Notify the assignment owner about active or completed consumers that need reassessment. Do not certify affected work from an invalidated snapshot, silently downgrade other agents' tickets, or clear real blockers to satisfy the validator.

For older ticket sets, keep `implemented` as unreviewed implementation completion. Do not mass-convert old tickets to `ready`. Missing `review_ref` is allowed for legacy unreviewed tickets; add it when a review report exists. Recompute the index under the review gate. Report previously started work that now has an unreviewed prerequisite to the coordinator.

## Rationale and sources

This workflow uses independent standards and specification axes from [Matt Pocock's code-review skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md). It adds current-target verification, local lifecycle updates, and a revision handoff. It does not require his tracker setup.

The distinction between required corrections and optional polish follows [Google's code review standard](https://google.github.io/eng-practices/review/reviewer/standard.html). Aim for sound, maintainable work, not endless stylistic perfection. Sources checked on 2026-09-05.
