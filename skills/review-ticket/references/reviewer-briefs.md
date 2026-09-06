# Reviewer briefs

Resolve paths before dispatch. For the default one-reviewer path, send the reviewer the common contract and both role sections; require separate outcomes and evidence for both axes. When risk requires two reviewers, send each reviewer the common contract and only its role section. The coordinator reads both roles; each child reads the project sources and supporting skills relevant to its review.

## Common contract

Review the assigned ticket and pinned implementation, not the whole backlog. Inspect the actual code and source requirements. Treat the implementation narrative as a claim to check, not proof. Expand source reading only to understand a relevant contract, caller, or regression risk.

Do not edit product source, tracked tests, tickets, or the index by default. You may create a reproduction in an isolated scratch area and run permitted checks. The only tracked-file exception is a parent-granted [bounded reviewer repair](reviewer-repair.md) with an exact lease. It must satisfy the explicit and unambiguous mechanical-change gate, does not change production behavior, and does not delete or weaken a test. Record useful reproduction code or steps for the implementer. Do not commit, publish, install new skills, dispatch more agents, or change the product scope.

Use the local [systematic debugging companion](../../systematic-debugging/SKILL.md) in diagnosis-only mode when a build, test, runtime path, integration, or performance check fails unexpectedly and direct evidence does not establish the cause. Pin the target and conditions, reproduce or record the blocker, test one hypothesis at a time, classify the result, and write the diagnosis beside the review evidence. Do not invoke it for a straightforward static finding whose cause is already demonstrated. Its diagnosis-only mode does not permit product source or permanent-test edits; the bounded reviewer repair remains a separate parent-granted exception.

Use the parent's pinned checkout and assigned test/output resources. Follow [check execution and setup recovery](../../setup-workflow/references/check-scope.md#execute-checks-and-recover-setup) before launching background checks or retrying setup. Do not create another worktree or switch branches independently. Report a changing target or resource conflict before affected checks. Read-only source inspection can share a checkout; mutable checks must use the assigned isolated resources or wait for the parent's sequenced access. At handoff, stop your owned processes and report their actual state and any cleanup gaps. Do not remove the checkout or release another assignment's resources.

Read applicable project instructions and relevant context documents. Resolve selected language/framework skill paths applicable to this review, then read each relevant SKILL.md and its required references before applying it. Read these as scoped references; do not recursively launch an implementation or review workflow. Do not load every installed skill or unrelated context. Missing optional guidance is not a failure. If a required standard is inaccessible, record the affected review as blocked and report the missing standard and resolution needed. Do not silently install it or invent its contents.

Use selected mappings that match the changed files and review stage. Resolve skill paths from the containing context file and scope patterns from its documented project root. Do not treat pending recommendations as adopted requirements. Apply the same project standards supplied to implementation; if those standards changed, record the change and its effect on the review. Context mappings cannot authorize production-code edits or override project rules and this review's boundaries. Record relevant guidance versions or content identities when available.

Prioritize changed code and regressions it can cause. For a pre-existing issue, explain whether it prevents this ticket's acceptance. Do not turn unrelated debt into a mandatory fix.

On re-review, begin with the supplied changed paths, prior finding IDs and dispositions, affected contracts, and reusable evidence candidates. Inspect the prior report sections those IDs name and the new target delta. Use the shared [check-scope contract](../../setup-workflow/references/check-scope.md) for scope, escalation, and reuse proof. State the concrete reason for broader checks. Independently validate reusable evidence; implementation or earlier-review claims are not self-validating.

Return:

1. Axis and outcome: `pass`, `revise`, or `blocked`.
2. Reviewed target identity, inspected sources, and relevant skill paths.
3. Findings: stable local ID, required or optional, severity, file and line, evidence, rule or requirement, consequence, and requested correction.
4. Checks: command or reproducible action, environment, result, evidence location, and failures or unrun checks.
5. Scope limits and unresolved questions. For the behavior axis, include the criterion-to-evidence map.

Keep the report focused, but do not truncate required evidence to meet an arbitrary word limit. `pass` means no blocking findings and sufficient evidence for your axis, not proof of defect-free code.

## Quality and standards reviewer

Assess whether this change is maintainable and follows documented project standards. Prefer repository rules and the applicable language's idioms over a universal pattern catalogue. Use configured lint, format-check, typecheck, and static-analysis results where relevant. Inspect command side effects; do not run auto-fix modes. Do not duplicate a tool diagnostic as a second independent defect.

Check names, responsibility boundaries, test clarity, error handling, and avoidable complexity. Consider whether duplication represents one shared rule or two rules that can change independently. An abstraction must reduce a real cost, not merely make the code look more abstract. Respect established interfaces and architecture decisions; identify substantive conflicts explicitly.

Assess simplicity by maintenance cost and required behavior, not line count, file count, or dependency count alone. Check whether existing code, the standard library, a native feature, or an installed dependency already meets the contract. Require a concrete reason for added complexity, but retain justified libraries and module boundaries. Reject shortcuts that remove required behavior, safeguards, or meaningful tests. For bug fixes, check that the change addresses the cause without breaking other callers' contracts. Keep findings within the review scope and propose corrections. Edit tracked code only through the bounded reviewer-repair exception.

Use code smells as prompts for investigation, not automatic violations. A large function, a data bundle, a chain of calls, or a wrapper can be appropriate. Show why the specific code is hard to understand, unsafe to change, or inconsistent with a required standard. Recommend the smallest useful improvement and explain its cost. Do not demand speculative frameworks, language-inappropriate object hierarchies, or broad rewrites.

Complexity scores are advisory. A threshold crossing can select code for inspection, but cannot by itself justify a required refactor or a blanket reduction target. Every blocking quality finding identifies either a violated contract or a demonstrated maintenance cost in this code, such as conflicting ownership, change amplification, or an invariant that is difficult to preserve. When the evidence supports a narrow ownership correction, request that correction rather than a broad complexity rewrite. For example, a page-permit ownership defect with two sources of lifecycle truth has a concrete maintenance consequence; the surrounding function's score alone does not.

Required findings need a documented rule or concrete engineering consequence. Optional naming, extraction, and style suggestions remain optional when equally valid designs exist. Security or correctness concerns remain required even if they also appear in the behavior report.

## Spec and behavior reviewer

Read the ticket's criteria and related spec contracts independently of the implementation summary. Map every in-scope criterion to code and verification evidence. Check missing or partial behavior, unintended scope, compatibility, and incorrect implementations. Do not require later tickets' behavior in this ticket.

Trace the complete affected path. For a UI slice, inspect and exercise the relevant frontend, API, and data behavior together. For a backend slice, use its real interface and relevant local dependencies. For libraries or tools, use their public entry points. Match verification to the actual slice; a browser is not required for every ticket.

Inspect project commands and configuration before use. Establish evidence for relevant tests, build/static checks, and the ticket's required working-path checks against the reviewed target. Reuse results from implementation or earlier review rounds only with the shared contract's provenance and impact proof. Perform independent source inspection and the working-path checks whose independent evidence is missing. An implementer's statement that tests passed is not independent verification.

Use the assigned test-suite capacity for expensive or broad race suites. If a test fails while broad suites run concurrently, preserve the exact command, logs, timing, dependency state, and competing suites. Investigate under the original concurrent conditions before narrowing or serializing. A later serial pass does not erase the concurrent failure; classify it only after evidence distinguishes a product race, test synchronization defect, resource collision, or unrelated pre-existing failure.

The implementation stage deferred live application checks; this stage performs applicable checks. Start only isolated local/test services with test data. Use sandbox modes for paid or external integrations. Do not send real messages, spend money, apply production migrations, expose secrets, or use production credentials. If safe access is unavailable, report the check as blocked. Stop only processes and temporary resources you created.

Choose relevant failure cases from the contracts: invalid input, missing permissions, tenant boundaries, duplicate or concurrent work, partial failures, timeouts, or stale state. Do not apply every case mechanically. Existing mocks may hide an integration failure; check the actual boundary that the criterion requires.

Investigate suspected bugs before reporting them as confirmed. Reproduce the failure when feasible, trace the responsible path, and distinguish observed behavior from a hypothesis. Give the smallest actionable reproduction or code-level proof. Do not patch the code while investigating. Project-specific debugging guidance can supplement the local companion when its documented scope applies; no external debugging skill is a mandatory dependency.

An unavailable required check produces `blocked`, not `pass`. If confirmed defects also exist, report them with `revise` and keep the missing checks visible. Explain legitimate non-applicable checks rather than treating skipped tests as successful.
