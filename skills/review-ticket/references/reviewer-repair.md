# Bounded reviewer repair

Use reviewer repair to close a small, mechanical review finding without an implementation and re-review round. It is an exception to the reviewer's read-only default. The parent must grant it within existing edit authorization and record an exact file lease before the reviewer writes. A standalone review remains read-only unless the user explicitly authorized fixes. During an authorized `coordinate-work` run, the coordinator may grant the lease because that run already authorizes implementation edits, unless the user or repository requires review-only operation.

## Eligibility

A repair qualifies only when all of these are true:

- The repository rule is explicit and unambiguous, and the finding already identifies that rule and an exact location.
- The correction is local and mechanical: a test name, fixture label, comment, documentation spelling, configured formatting, or an equivalent local symbol rename performed safely by repository-supported tooling.
- The correction does not change production behavior, a public interface, data or wire format, control flow, permissions, migrations, test inputs, assertions, expected outputs, or acceptance criteria.
- It does not delete or weaken a test, reduce coverage, suppress a diagnostic, or alter configuration to make a check pass.
- Its affected paths fit one small recorded lease and do not overlap another active writer.
- The reviewer can verify it with the smallest meaningful configured check plus any focused test or build needed to catch broken references.

Severity alone neither permits nor forbids reviewer repair. A low-severity change returns to the implementer when its semantics or blast radius are uncertain. A required naming correction can qualify when the rule and edit are mechanical. File moves normally return to the implementer because module resolution, imports, build inputs, ownership, and public paths can change. Allow a move only when repository-supported tooling proves all references and the path is not a public or persisted contract.

## Procedure

1. Record the finding before editing, with its stable ID, explicit rule, exact location, and requested correction.
2. Ask the parent to grant reviewer repair and register the exact lease. Do not write while another reviewer or writer is using the target. With two reviewers, finish their independent first inspection before any repair changes the frozen source identity.
3. Make only the recorded mechanical correction. Do not fix adjacent polish or expand the lease.
4. Inspect the resulting delta. If it contains a semantic or unexpected change, stop and return the finding to the implementer.
5. Run the smallest meaningful naming, lint, typecheck, build, or focused test checks after the edit. Apply the shared [check-scope contract](../../setup-workflow/references/check-scope.md) to retain proven unaffected broader evidence and expand checks when needed.
6. Stop owned processes and return the repair evidence to the parent: before/after source identities, changed paths, check results, explicit skips, cleanup, and proposed disposition. The parent records those facts in the review report and handoff manifest after inspecting them.

A qualifying repair requires no second reviewer solely because the reviewer made it. The implementation still received independent review before the repair, and configured checks prove the bounded mechanical delta. Existing risk rules can still require two reviewers for the ticket itself. If the repair touches evidence owned by another required review axis, that axis must validate only the affected delta before readiness.

The parent remains the only writer of the ticket, review record, and index. It marks the finding `repaired-by-reviewer` only after inspecting the delta and check evidence. A failed, blocked, or incomplete repair becomes `revision_required` and returns through the normal implementer path; do not keep editing until it passes.
