# Engineering specification structure

Use this structure as a guide. Keep required content complete and omit conditional sections when irrelevant. Scale detail to the feature.

## Document identity

Include the feature name, source discovery brief path, last-updated date, and inspected project revision if available. Identify any current-task amendments to the source brief.

## Problem, outcome, and scope

State the user problem, intended outcome, included behavior, and explicit exclusions. Preserve the discovery brief's scope.

## Existing system and constraints

Explain relevant current behavior, components, interfaces, conventions, and constraints. Link to inspected evidence. Clearly distinguish observations from the proposed design.

## Requirements and acceptance criteria

For each requirement, record:

- Stable REQ identifier.
- Source decision identifier or brief section, recorded current-task amendment, or identified engineering choice within the agreed scope with supporting evidence.
- Required behavior, actor, and applicable conditions.
- Linked AC identifiers with observable expected results.

Use a compact table or individual entries as appropriate. Cover significant errors and boundary cases as well as normal use.

Illustrative entry:

> REQ-001 — Source: D-002, "View-only invitations."
> A collaborator with view-only access can read the project but cannot change its content.
> AC-001 — An authenticated view-only collaborator can open the project.
> AC-002 — A write request from that collaborator is rejected and leaves stored project content unchanged.

These examples show the level of specificity. They do not add requirements to the feature being specified.

## Technical design

Define component responsibilities, interactions, and consequential engineering choices. Explain reasons and accepted costs. Link choices to the requirements they serve.

Use the following subsections only where relevant:

- Data model, ownership, validation, and invariants.
- API or event contracts: inputs, outputs, errors, and access rules.
- State transitions and user-visible interactions.
- Concurrency, ordering, retry, and idempotency behavior.
- Dependencies, compatibility, migrations, and recovery.
- Security, privacy, accessibility, performance, and operational behavior.

For affected backend behavior, incorporate the companion architecture guidance here. Record consequential choices with their requirement, alternative, benefit, cost, evidence, and condition for reconsideration. Include applicable cache freshness/invalidation, resource limits, failure contracts, workload assumptions, and measurement targets. Reference established policies for unchanged behavior; do not fill every category mechanically.

For a material interface, specify enough detail for two implementers to agree on its behavior. Do not use "handle errors appropriately" or similar phrases in place of concrete rules.

## Verification approach

Map acceptance criteria to suitable verification methods. Identify existing test conventions, required fixtures or setup, expected outcomes, and relevant regression coverage. Describe what needs verification, without claiming it has already passed.

For each distinct verification boundary, distinguish focused acceptance checks, combined-feature scenarios, and repository-required gates. Link reusable setup; note real-service needs and known execution costs or mark them unknown. Define which contracts must be stable for separate implementations to proceed. These are inputs to ticket decomposition, not predetermined tickets or a requirement to repeat all checks per ticket.

### Whole-feature scenarios

Give each important scenario a stable SC identifier and linked REQ/AC identifiers. Include:

- Preconditions, roles, and test data.
- Ordered actions through the actual public interface and participating components.
- Observable outcomes, including durable state and external effects when required.
- Important failure paths and affected regression checks.
- Required real services/boundaries and any explicitly permitted sandbox substitute.
- Links to startup, configuration, readiness, and cleanup sources; mark missing setup as planned, not tested.

These scenarios guide verify-feature on the combined code after ticket review. They complement unit and component tests. Do not prescribe a browser for a backend-only feature or Docker when no container setup is needed. The verifier still checks every in-scope criterion, including requirements not covered by a listed scenario.

## Open issues and deferred topics

Distinguish unresolved material questions from minor implementation choices and deliberately excluded future work. Explain the impact of any material gap. State when none remain; do not manufacture questions to fill this section.

## Evidence

List useful project-relative source paths and external source URLs. Keep references specific enough for a fresh agent to check the factual basis of the design.
