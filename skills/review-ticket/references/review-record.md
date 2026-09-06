# Review record and decisions

Use `<workflow>/reviews/<ticket-id>/R-001.md`, then the next unused round number. Its path from a ticket is normally `../reviews/<ticket-id>/R-001.md`. Supporting logs or reproductions may live beside the report. Link from the ticket; do not paste long logs into its body. Preserve old rounds and finding IDs when findings recur.

Each report contains:

- Ticket and spec links; date; coordinator and reviewer identities.
- Baseline, target identity, included paths, spec digest, and relevant standards sources.
- Separate Quality and standards and Spec and behavior sections. Each has its outcome, findings, executed checks, evidence links, and limits.
- A criterion-to-evidence map for the ticket, with pass, fail, or blocked results. State why a check is not applicable when necessary.
- Coordinator dispositions for each finding: accepted-required, optional, rejected-with-evidence, or unresolved. Preserve the reviewer's original concern when disagreeing.
- Final decision, lifecycle transition, availability evidence, remaining blockers, and handoff action.

Use IDs such as `Q-001` and `B-001`. A required finding includes location, violated requirement or standard, demonstrated effect, requested correction, and expected verification. Severity describes impact; required/optional decides whether it blocks. Do not use a severity cutoff that silently accepts a real acceptance-criterion defect.

## Decision table

| Evidence on the current target | Ticket state | Next action |
| --- | --- | --- |
| Both axes pass; required verification passes; no unresolved blocking findings | `ready` | Verify availability and refresh downstream candidates. |
| A confirmed required code or test correction remains | `revision_required` | Implementer fixes accepted findings, then submits a new review. |
| Required check, reviewer, access, or material decision is missing; no confirmed correction yet | `in_review` | Record blocked review and the concrete resumption action. |

An optional improvement does not prevent readiness. A concern can be rejected only with evidence and a recorded reason. Obtain the reviewer's reassessment of a material disagreement; unresolved disagreement is not a pass. Do not overrule a supported finding because the deadline is close.

If a reviewer fails, times out, or returns an incomplete report, retry that role through the available agent mechanism. Save progress if it cannot finish. Do not count an absent review as a pass.

## Revision handoff

Set `revision_required`, clear `available`, and keep the concrete implementation reference as the reviewed location. Preserve prior review rounds. The assignment coordinator sets `in_progress` and confirms the implementer before work resumes. Do not auto-dispatch from this skill.

Send the implementer the exact ticket and review paths, accepted required finding IDs, relevant evidence, and required rechecks. The implementer follows `implement-ticket` and its TDD companion. It records each fix or evidenced disagreement, runs implementation checks, updates `implementation_ref`, and returns `implemented`. It cannot self-certify `ready` or close findings as reviewer-approved.

Re-review both axes on the new target. Focus on changed code, earlier findings, and affected contracts without ignoring regressions. Preserve useful earlier evidence only when reviewers explicitly establish that it still applies. If the same blocker remains after a fix attempt, diagnose or clarify the missing decision; do not repeat an unchanged implement/review loop.

## Completion and scheduling

`ready` means this ticket's review and verification are complete. `available` separately means its implementation is usable in the consumers' agreed base. A ready ticket may remain unavailable. In that case, report the integration handoff, not a newly unblocked dependent.

Do not remove files, dependency edges, or prior reports to close a ticket. The index keeps all ticket rows and separates open work from completed work. Derive unblocks and candidates from metadata. A dependency satisfied today remains recorded for later regression analysis.

If a completed prerequisite is reopened, identify its consumers through metadata. Notify the assignment owner about active or completed consumers that need reassessment. Do not certify affected work from an invalidated snapshot, silently downgrade other agents' tickets, or clear real blockers to satisfy the validator.

For older ticket sets, keep `implemented` as unreviewed implementation completion. Do not mass-convert old tickets to `ready`. Missing `review_ref` is allowed for legacy unreviewed tickets; add it when a review report exists. Recompute the index under the review gate. Report previously started work that now has an unreviewed prerequisite to the coordinator.

## Rationale and sources

This workflow uses independent standards and specification axes from [Matt Pocock's code-review skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md). It adds current-target verification, local lifecycle updates, and a revision handoff. It does not require his tracker setup.

The distinction between required corrections and optional polish follows [Google's code review standard](https://google.github.io/eng-practices/review/reviewer/standard.html). Aim for sound, maintainable work, not endless stylistic perfection. Sources checked on 2026-09-05.
