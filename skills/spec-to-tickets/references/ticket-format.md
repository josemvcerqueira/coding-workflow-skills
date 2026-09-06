# Local ticket format

## Directory

```text
<external-workspace>/workflows/<workflow-id>/
  WORKFLOW.md
  spec.md
  RUN.md
  tickets/INDEX.md
  tickets/T-001.md
  tickets/T-002.md
  reviews/T-001/R-001.md
  verification/V-001/REPORT.md
```

Paths in metadata and Markdown links are relative to the file containing them. IDs are unique within a feature directory. Use the directory path with the ID when assigning work across features.

## Ticket metadata

Use this single-line YAML subset so the standard-library validator needs no dependencies. Values use JSON syntax, which is valid YAML: quoted strings, arrays, booleans, or null. No inline comments or multiline values.

```yaml
---
id: "T-001"
title: "Deliver the selected user outcome"
status: "pending"
spec: "../spec.md"
spec_refs: ["REQ-001", "AC-001", "AC-002"]
blocked_by: []
exclusive_resources: []
external_blockers: []
assignee: null
implementation_ref: null
review_ref: null
available: false
superseded_by: []
---
```

- `status`: pending, in_progress, implemented, in_review, revision_required, ready, or superseded.
- `spec_refs`: exact spec identifiers or headings. Verify them against the source.
- `blocked_by`: prerequisite IDs in this directory. Cross-feature prerequisites use explicit paths and required evidence in `external_blockers`, not invented local IDs.
- `exclusive_resources`: stable labels for work that must not overlap. An empty list is allowed.
- `external_blockers`: unresolved constraints outside this graph. Remove a blocker only when evidence resolves it.
- `assignee`: assigned implementation agent or task identifier; null before assignment.
- `implementation_ref`: usable commit, branch with revision, or other concrete implementation location. Required for implemented, in_review, revision_required, and ready.
- `review_ref`: relative path to the current review report. Required for ready and revision_required. Null before review; older unreviewed tickets may omit it. Reports retain both reviewer outcomes, the reviewed target, and check evidence.
- `available`: true only when the implementation is accessible in the consumers' agreed working base. It does not mean reviewed.
- `superseded_by`: replacement IDs for a superseded ticket, otherwise empty.

Assignment readiness is derived: a pending ticket is an assignment candidate when external blockers are empty and all prerequisites have `status: "ready"` and `available: true`. Running implementation or review may prevent assignment through exclusive-resource conflicts. The validator's `ready` list contains pending candidates; ticket `status: "ready"` means reviewed completion, not waiting to start.

`implemented` completes coding only. `in_review` reserves the review target and may record unavailable required checks. `revision_required` means accepted corrections must return to implementation. `ready` means both review axes and required verification passed on the current target. Ready tickets have no unresolved external blockers. A revision-required ticket must have `available: false`.

## Ticket body

Use these sections, keeping each focused:

### Outcome

State the complete behavior this ticket delivers and why it matters.

### Source and essential context

Link the spec and relevant sections. State the rules and contract details needed to start. Include researched code pointers when useful, without making stale file locations part of the requirement.

### Scope and exclusions

Describe the vertical path and its boundary. For a prerequisite or migration exception, explain the exception and its concrete deliverable.

### Acceptance criteria

Use checkable outcomes mapped to spec AC or REQ identifiers. Include relevant error paths and regression constraints. Do not create invented product behavior.

### Dependencies and handoff

Link each prerequisite file, state the exact capability required, and explain how its implementation becomes available. State any external blocker and exclusive-resource rationale. Future consumers are discoverable through the index; read them only when needed.

### Working-path verification

Give relevant setup, action, and expected result for demonstrating the slice. Include frontend/backend startup or environment references for UI flows. Distinguish the implementing agent's necessary checks from later independent testing and review.

### Sizing

Explain why the slice should fit roughly one 200k context window for implementation, including debugging and necessary checks. Name uncertainty or justify an exception. Exclude later review and style-improvement budgets.

### Implementation record

Initially state "Not started." The implementing agent later records implementation location, behavior checks and results, remaining limitations, and required handoff information. Failed or unrun checks must remain visible.

### Review record

Initially state "Not reviewed." The review coordinator records ownership, the current target, linked review rounds, separate quality and behavior outcomes, required revisions or blocked checks, and the final decision. Keep detailed evidence under `<workflow>/reviews/<ticket-id>/`, linked from tickets as `../reviews/<ticket-id>/R-001.md`. Preserve execution evidence after completion or revision.

## Index

The assignment agent reads the index; an implementing agent starts with its ticket.

Include:

- Source spec link, its SHA-256 digest, and last-updated date.
- One compact row per ticket: linked ID, title, status, blocked by, derived unblocks, and exclusive resources.
- A requirement/acceptance coverage map.
- Initially ready tickets and conditional parallel candidates, derived from current state. Label these as a snapshot that must be recomputed before assignment.
- Any exceptions or unresolved material gaps.

Keep completed ticket rows for history. Exclude ready and superseded tickets from open-work lists without removing their files or dependency edges.

Do not copy ticket bodies into the index. A suggested sequence is guidance only; dependency fields control gating.

## State ownership and updates

Use a single assignment coordinator to claim tickets and update the index. Markdown files are not atomic locks. Do not let several agents independently claim from the same readiness snapshot.

The optional `coordinate-work` skill supplies the execution loop and owns `<workflow>/RUN.md`, runtime mappings, and coordinator ownership. Keep this ticket directory canonical across code worktrees. Its stable assignment IDs are valid assignee values; runtime agent IDs are mapped separately in RUN.md. Planning does not acquire an execution lock or dispatch work.

The coordinator sets the assignee and in_progress status before dispatch, including revision work. The assigned implementer updates only its ticket and implementation record. It records implemented only when the slice works and reports the checks and implementation reference. The coordinator records availability after checking that downstream work can access the implementation, then refreshes the index. Availability alone never bypasses review.

Implemented means the working implementation stage is complete. It does not mean code-quality review, spec review, or publication has occurred. Those stages remain separate.

The `review-ticket` parent coordinates with the assignment owner and is the only writer during review. Two independent reviewers return evidence; they do not edit code or ticket state. The parent transitions implemented to in_review, then ready or revision_required. Missing required verification leaves in_review with a blocked review record, not a pass. Revisions return through assigned in_progress, implemented, and another review. Review never implies permission to merge, deploy, or implement the next ticket.

Bind review evidence to the exact code target and relevant spec version. Code changes require renewed review evidence. A reopened prerequisite can invalidate downstream readiness. Notify the assignment owner, preserve the graph, and pause affected work through that owner.

The separate verify-feature stage records whole-feature pass/fail/blocked outcomes in numbered verification reports, not a new ticket status. A pass requires the combined code, not just ready tickets. Its findings go to the assignment coordinator for affected-ticket re-review, accepted revisions, implementation, and renewed review. Do not place a feature report in review_ref as if it contained both ticket-review axes. Keep feature report pointers and target freshness in RUN.md when a coordinator is used.

Legacy implemented tickets remain unreviewed; never mass-promote them to ready. Add review_ref when a report exists and refresh readiness under the current gate. The validator checks report existence, not its verdict, freshness, or truth. The review coordinator verifies those before recording ready.

Do not edit other agents' assignments or inferred completion state. If a later finding invalidates completion, preserve the evidence and explain the state change rather than erasing history.

Superseded tickets may retain their original dependency edges as history. Live tickets must reference the appropriate replacement prerequisites. If an active ticket gains a blocker, report it to the coordinator and pause the affected work; do not remove the blocker just to pass validation.

## Closed workflows

The setup-workflow workspace and closure contracts are required. CLOSING.md or COMPLETED.md in this ticket directory or its immediate parent prevents active validation and scheduling, regardless of stale ticket state. Marker presence is a stop signal, not proof of successful completion. All active workflows still require an existing spec and valid spec references.

After verified closure, registered specs are deleted. Preserve ticket statuses, IDs, graph edges, and historical evidence. The closed index explains that former spec paths and IDs are historical identifiers, not live inputs. Do not regenerate specs, bypass validation, or reopen these tickets to repair deliberately retired references. New changes get a new workflow based on current code and user intent. Verify closure through its receipt and deletion journal, not through the active validator.

## Assignment prompt

> Implement the ticket at <exact-ticket-path>. Start with that file and follow its source pointers only as needed. Complete its working vertical slice and record implementation evidence there. Do not load or implement the full ticket set. Report a material scope or contract conflict instead of silently changing the spec.
