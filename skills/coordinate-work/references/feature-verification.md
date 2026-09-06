# Final feature verification

Record whether the user requested final feature verification. Preserve that choice on resume. Do not add the stage to an older ticket-only run without a request. The verifier remains explicit-only; directly reading its instructions in an authorized child assignment does not enable implicit invocation.

When requested, locate this collection's verify-feature skill and read its entrypoint and required references before dispatch. Resolve its inputs from WORKFLOW.md and the agreed combined target; do not ask the user to remember paths. It uses the already required spec-to-tickets companion. Report a missing verifier instead of installing or substituting it. When verification was not requested, return a suggested invocation with the actual spec, ticket directory, and combined checkout paths; do not dispatch.

## Entry and dispatch

All non-superseded tickets for the spec must be ready. Check that their reviewed implementations are present together in the agreed verification checkout. Do not infer integration from an available flag, branch existence, or independent review passes. Missing integration requires the existing explicit authority rules; verification does not grant merge permission.

For parallel ticket work, complete the authorized integration and any required re-review before this handoff. Select the combined target yourself and record the contributing implementation identities. Do not ask the verifier to combine ticket worktrees or treat separate branch checks as whole-feature evidence. The verifier uses the coordinator's assigned target and resources; it does not choose a different product checkout.

Freeze the combined target and reserve its mutable test resources. Wait for conflicting writers and review runs to stop; unknown liveness is a blocker. Count the verifier against runtime capacity. Give it a fresh focused context, not the implementation transcript. Supply the exact skill path, full spec path, canonical ticket directory, checkout/build identity, context path, evidence directory, and user limits.

Use the run's dispatch-intent and unknown-outcome recovery rules. Record a verification assignment separately from ticket assignees. The verifier owns its new report directory; the coordinator remains the sole writer of RUN.md and lifecycle/index state. No second coordinator lock is needed for that child. A slow or unreachable verifier still reserves its target and resources until reconciled.

## Outcomes and correction loop

Inspect the report, target identity, criterion coverage, check evidence, and cleanup status before accepting an outcome. A final message alone is not proof. Link the report and record its target and pass/fail/blocked result in RUN.md, separately from ticket counts.

- **Pass:** report feature verified only for that exact spec and combined target. Do not claim deployment, release, or perfect code.
- **Fail:** reconcile confirmed findings with affected tickets. Reopen the relevant ready tickets through review-ticket's existing re-review procedure, supplying the feature report. The ticket review parent records accepted revisions with its two-axis review contract; never replace review_ref with a feature report. Then use the normal implement-ticket and review-ticket loop. Pause affected consumers and invalidate stale availability/evidence as needed. Do not reopen unrelated tickets automatically.
- **Blocked:** save the missing condition and retry action. Do not invent a code revision for an unavailable service. Wait only for a known active event; otherwise checkpoint and return the blocker.

If a confirmed defect has no suitable ticket, identify the uncovered existing spec requirement. Arrange a bounded ticket through spec-to-tickets within the run's authorized scope; do not invent new product scope or silently enlarge an active assignment. Ask one focused question for a material spec conflict or new authority.

After corrections pass ticket review and the combined target is restored, dispatch a new verification round. Include prior finding IDs, affected criteria, and report paths. Require the failed scenarios and affected regressions to run again. Stop unchanged retry loops and obtain a concrete diagnosis or missing decision.

## Pause and completion

Status-only requests remain read-only. Draining starts no new feature-verification run; an already active verifier may finish and clean up. Save its findings for resume rather than launching new fixes. Pause-now requests stop dispatch and ask the verifier to checkpoint and clean up owned resources; record any unconfirmed process stops.

A ticket-only run can finish with verification not requested. A run that includes final verification is complete only after a current pass, confirmed cleanup or explicitly authorized retained resources, and the coordinator's successful registered-spec deletion and completion receipt under setup-workflow's closure contract. Changed product/spec/configuration inputs invalidate the affected verification claim; preserve the old report as history. No outcome grants commit, merge, push, or deployment authority.
