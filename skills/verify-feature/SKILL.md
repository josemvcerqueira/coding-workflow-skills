---
name: verify-feature
description: Use when the user explicitly requests final whole-feature verification against an engineering spec after ticket review, or re-verification after integration defects are corrected.
license: MIT
disable-model-invocation: true
---

# Verify feature

Test the combined feature against the full engineering spec. Exercise real application paths and save criterion-level evidence. This stage is not another code-quality review, a production fix, or a deployment. Ticket review completion and feature verification are separate outcomes.

## Establish the target

When the coordinator supplies canonical paths, verify the project, active workflow, full spec, tickets, context, combined checkout, and handoff identities against the assignment; avoid repeating registry discovery. For standalone invocation or absent/inconsistent paths, use the required [external workspace contract](../setup-workflow/references/workspace.md), locating the installed companion if needed without installing it. Resolve paths from project identity and saved pointers. Read applicable repository instructions, ticket index/metadata, and relevant implementation/review handoffs. Read source as needed; do not audit unrelated code or load all prior transcripts. Missing context alone does not block safe discovery. Closing/completed workflows are not verification targets; later changes need a new workflow.

Read this collection's [ticket format](../spec-to-tickets/references/ticket-format.md) and use its validator. Locate the installed spec-to-tickets companion if the sibling path is absent. If unavailable, report the missing dependency; do not install or invent it. Companion reads are part of this explicit invocation, not implicit skill selection.

Run `python3 <spec-to-tickets-directory>/scripts/validate_tickets.py <ticket-directory>`. Check that all non-superseded tickets for this spec are reviewed as ready, and their required implementations are present together in the supplied checkout. Validate handoff identities and spec coverage; metadata and report existence alone do not prove this. Missing code, stale review targets, or unresolved integration are blockers. Do not merge, cherry-pick, commit, or silently construct a different product target to unblock verification.

Confirm the checkout and mutable test resources have no competing writers. Coordinate a reservation with the assignment owner when one exists. Unknown worker liveness is not proof of a stable target. Do not take over its lock or change its assignments. Record the exact code target, spec digest, context/configuration identities, and test plan before execution as described in [the report contract](references/report.md). For uncommitted code, include a content manifest of relevant tracked and untracked sources; a branch name or HEAD alone is insufficient.

In a coordinated run, use the assigned combined target and reserved resources after integration. Do not switch branches, create another product worktree, or test separate ticket branches as a substitute. An exact-content isolated test copy permitted by the environment rules preserves the assigned target; report its identity and resource use to the coordinator.

## Plan the whole-feature checks

Map every in-scope requirement and acceptance criterion to evidence. Start from the spec's scenarios, then check for omitted cross-ticket interactions, failure cases, and regression risks. Do not assume the listed scenarios exhaust the spec. Derive missing test mechanics from code and project conventions; ask one focused question only when expected behavior or a material constraint cannot be established. Do not invent requirements or rewrite the spec to match the code.

Apply the shared [check-scope contract](../setup-workflow/references/check-scope.md) for first and repeated verification. On a correction round, begin with prior finding IDs, affected criteria/contracts, target delta, and candidate reusable evidence. Keep complete spec coverage while rerunning failed and affected integrated scenarios and validating carried unaffected observations.

Use relevant selected project skill mappings for verification, including guidance shared with review. Read only applicable skills and required references as scoped guidance. Recommendations are not selected requirements. Missing optional guidance is not a blocker; missing required guidance blocks the affected conclusion. Stage boundaries and project rules still apply.

Read [environment and execution rules](references/environment.md) before building, starting services, or sending requests. Reuse project test tools. You may add bounded verification harnesses, fixtures, and local test overrides in the run's evidence directory. Do not edit production code, weaken existing tests, change dependency manifests or lockfiles, or introduce product migrations as a shortcut.

## Execute and observe

Start the actual application and required local/test dependencies when the feature requires them. Use Docker when the project calls for it; do not require Docker or a browser for every backend, library, or CLI. Verify readiness and the identity of the running build before exercising the feature.

For UI features, drive the real user journey through the frontend and backend. For backend work, use the public API, worker trigger, or other real entry point. Observe durable state and downstream effects required by the spec, not just successful response codes. Use separate environments or reset only owned test data between scenarios. Run relevant existing regression checks as well as whole-feature scenarios.

Mocks and stubs can support diagnosis, but cannot prove a real boundary they replace. Document permitted external sandbox substitutes and their limits. Code inspection can support structural properties, but cannot replace required runtime behavior. A successful build, health endpoint, or collection of ticket reports is not an end-to-end pass.

When a check fails and direct evidence does not establish the cause, use the [systematic debugging companion](../systematic-debugging/SKILL.md) in diagnosis-only mode. Preserve the output, reproduce or record the blocker, test one hypothesis at a time, and classify product, harness, environment, pre-existing, specification, or inconclusive outcomes. This mode does not permit product source or permanent-test edits. Correct only your own disposable harness mistakes without changing the expected contract, then rerun and retain the history. Return confirmed product defects and affected criteria to the coordinator. Do not retry an unchanged failure until it happens to pass or conceal failed or unrun criteria.

## Report and hand off

Follow [the report contract](references/report.md) for pass, fail, and blocked outcomes, artifact layout, target freshness, cleanup evidence, and revision routing. Save a new numbered report for each run. Preserve previous reports and reproduction harnesses. After cleanup, write the shared [handoff manifest](../setup-workflow/references/handoff-manifest.md) atomically at the exact assigned path; for standalone verification, place it in this run's evidence directory. Record the current combined target, report paths, new and reused evidence, skips, findings/blockers, and resource state. Claim `whole_feature_verified` only for a report-backed pass.

The verifier writes verification artifacts and owned disposable build/test outputs, not product source or lifecycle state. It does not modify ticket lifecycle, review_ref, INDEX.md, or RUN.md. Send confirmed product findings and affected ticket/spec pointers to the coordinator. That owner routes corrections through implementation and review before another feature verification. A standalone invocation returns the same handoff without dispatching fix agents. After a pass, the coordinator performs registered-spec deletion through setup-workflow's closure contract. The verifier keeps specs intact until that handoff; it does not close the workflow itself.

Finish by stopping only the services and temporary resources you created. Save unresolved cleanup or access issues explicitly. Return the outcome, report path, tested target, coverage, failures or blockers, and next action. No final user approval is needed for an evidence-backed result. Use short sentences and consistent terms based on STE principles; do not claim formal ASD-STE100 compliance or defect-free software.
