---
name: write-the-spec
description: Turn a discovery brief into an engineering specification grounded in the project code and documentation. Use when the user invokes this skill with an idea brief or document path to define requirements, technical contracts, and acceptance criteria before ticket creation.
license: MIT
disable-model-invocation: true
---

# Write the spec

Read the discovery brief and produce a standalone engineering specification. Define the intended behavior and the technical decisions needed to implement it. Save the specification as Markdown in the selected project's external workflow workspace.

This stage ends with the specification. Do not create tickets, implement code, publish to an issue tracker, or run a separate code-review workflow.

## Priorities

1. Preserve the product decisions and scope established in the discovery brief.
2. Research technical facts instead of asking the user to find them.
3. Make behavior, contracts, and acceptance criteria precise enough to verify.
4. Distinguish established intent, researched facts, engineering choices, and unresolved assumptions.
5. Write the document directly. Do not add a final approval gate.

## Read the handoff

Read the full discovery brief supplied by the user. Do not require the interview transcript or a Confirmed status. The brief from `shape-the-idea` records decisions made during the interview without a separate sign-off.

If no path was supplied, resolve the active workflow through the shared workspace contract and read its discovery pointer. If several candidates remain plausible, ask which one to use. Do not substitute an unrelated or merely recent file.

Extract the goal, scope, decisions and their identifiers, constraints, success conditions, and open topics. Preserve exclusions and accepted tradeoffs. Treat explicit user corrections in the current task as amendments to the brief, and record them in the specification. Do not silently rewrite the source brief.

## Establish the engineering context

Required reference: read this collection's [external workspace contract](../setup-workflow/references/workspace.md). Locate the installed setup-workflow companion if the sibling path is absent; do not install it silently. Resolve the selected project, external context, and active workflow from its registry and task identity. The user need not supply directory paths. Read the external CONTEXT.md and applicable repository instructions or user-maintained context. Keep their scopes explicit. Missing context alone does not block safe work; inaccessible required guidance needs its own blocker. Do not execute closing or completed workflows.

Inspect applicable project instructions, relevant code, architecture decisions, domain terminology, schemas, interfaces, and tests. Read only what is needed to understand the affected behavior and dependencies. For external technical research, use authoritative sources relevant to the project's versions. For a new project, state that there is no existing implementation and propose a coherent design.

Separate current behavior from proposed behavior. Reference actual project paths, symbols, or documents when they help another agent find supporting evidence. Include the inspected revision when available. Do not invent paths or treat current file placement as a permanent architectural requirement.

Choose technical details that follow from the agreed scope and project conventions. Explain the reason and material tradeoff for consequential choices. Clearly identify these as engineering choices made in this specification, not decisions the user already made.

If a discoverable fact is missing, investigate it. If a missing product decision or conflict materially affects scope, behavior, feasibility, or acceptance criteria, ask one focused question, give your recommendation and its tradeoff, and wait for the answer before specifying dependent behavior. Continue independent research if useful. Do not repeat the discovery interview or ask the user to choose routine implementation details.

Do not turn assumptions, proposals, or deferred features into requirements. If an essential fact cannot be established, record the gap. Save useful work, but state that the specification is incomplete while a material gap remains.

## Write a precise specification

For backend-related work, first read the companion [backend-architecture skill](../backend-architecture/SKILL.md). This includes changes to APIs, services, database behavior, background jobs, external integrations, caching, or backend performance and reliability. Use it in this same agent and context, before finalizing technical choices. Skip it for presentation-only work that does not change backend contracts or behavior.

Read the companion as a required reference within this explicit invocation; do not rely on automatic skill selection or a model-invoked slash command. If the sibling path is absent, locate this collection's installed companion. If backend work needs it and it is unavailable, report the missing dependency before finalizing the backend design. Do not silently substitute an unrelated skill.

Read only its applicable supporting references. Record the resulting choices and tradeoffs inside this specification. Do not create a separate architecture stage, approval gate, or competing document.

Use the relevant sections in [the specification template](references/spec-template.md). Omit sections that do not apply; do not invent complexity to fill the template.

Assign stable requirement identifiers such as `REQ-001` and acceptance identifiers such as `AC-001`. Preserve identifiers during revisions. Connect each requirement to its source: a discovery decision or brief section, a recorded current-task amendment, or an identified engineering choice within the agreed scope with its supporting evidence. Connect acceptance criteria to requirements. Do not attribute a new choice to the user or source brief. Every in-scope obligation must be covered, without producing repetitive user stories for a target length.

Specify the rules that determine observable behavior. Where relevant, define inputs, outputs, validation, errors, permissions, state transitions, data ownership, persistence, and effects on existing users or data. Address concurrency, retries, partial failure, compatibility, and recovery when the feature depends on them.

Prefer precise prose, tables, and small schemas or examples over implementation code. Include a short type, payload, or state definition when it removes ambiguity. Clearly label illustrative examples; they must not contradict normative rules.

Define component responsibilities and boundaries when needed to make the design coherent. Leave incidental choices to implementation when they do not affect correctness or coordination. Do not prescribe line-by-line edits, ticket boundaries, task sequencing, or context budgets.

Use measurable acceptance criteria. Replace vague requirements such as "fast" or "secure" with the applicable observable condition. Research existing targets; if a new material target requires a user decision, ask rather than inventing a number.

## Specify verification

Describe how to verify the requirements through observable outcomes, including relevant failure cases and regressions. Use existing test boundaries and conventions where suitable. Choose unit, integration, or end-to-end coverage according to the behavior and risk; do not force all verification through one boundary.

Identify necessary test setup, data, and expected results. Define verification intent rather than assertions tied to private implementation details. Do not claim that tests have run, that code passes, or that a future implementation is correct.

Include a whole-feature verification plan for the later verify-feature stage. Give important end-to-end scenarios stable SC identifiers and map them to REQ and AC identifiers. Cover complete public-interface journeys, state changes, consequential failures, and interactions between planned components. The ticket boundaries are not known yet; do not limit scenarios to isolated components. State preconditions, test data, ordered actions, observable results, required real boundaries, permitted external sandboxes, and relevant regression checks. Include persistence, restart, concurrency, or performance checks when required by the feature, not mechanically for every spec.

Link project startup, readiness, configuration, and cleanup instructions from context or their actual source files instead of duplicating them. Describe feature-specific environment needs here. If commands or the application do not yet exist, label the setup as planned and identify what implementation must supply. Do not invent tested commands. The verifier may derive execution mechanics, but material gaps in expected behavior must be resolved in the spec. Require a stable combined implementation for final verification; passing individual ticket checks is not a whole-feature pass.

## Use Simplified Technical English

Use English based on ASD-STE100 principles throughout the specification and user messages:

- Write short, direct sentences with one main idea each.
- Use active voice, concrete verbs, and consistent terms.
- Define unfamiliar technical terms.
- Make actors, conditions, and consequences explicit.
- Avoid idioms, business jargon, and ambiguous references.
- Preserve exact identifiers, contracts, conditions, and technical meaning.

Do not claim formal ASD-STE100 compliance without checking its controlled dictionary and writing rules.

## Save and hand off

When revising a specification, read and update the active workflow's identified spec in place, preserving requirement identifiers and unrelated edits. Save a new spec as `<workflow>/spec.md` and register its exact path under WORKFLOW.md `spec_files`. Register any owned spec drafts too. Do not duplicate the spec in the product checkout, context, or another workflow. These owned spec files will be deleted after verified closure; do not delete them during authoring or hide a backup elsewhere.

Include the source brief path, last-updated date, and relevant evidence references. State unresolved material gaps explicitly if any remain. Do not use an approval status or request a final sign-off.

Before finishing, check the document for missing source decisions, scope expansion, contradictory contracts, unsupported claims, and requirements without acceptance criteria. Correct defects in the document as part of authoring; this is not a separate review workflow.

Read the saved file to verify it contains the completed specification. Return its exact path or link, a short description of what it covers, and any remaining material gap. A fresh agent must be able to use it with the referenced project sources without the interview transcript. The next stage may break it into tickets, but do not start that stage.

If file writing is unavailable, provide the complete Markdown and proposed filename. State that no file was saved.
