---
name: spec-to-tickets
description: Convert an engineering specification into local Markdown tickets with vertical scope, spec references, explicit dependencies, and parallel-work constraints. Use when the user invokes this skill to prepare or maintain a filesystem ticket set for one implementation agent per ticket.
license: MIT
disable-model-invocation: true
---

# Spec to tickets

Create and maintain the complete local ticket set from an engineering specification. Preserve scope and explicit dependencies. Each ticket fits one focused implementation assignment. Implementation, dispatch, web issues, and later reviews belong to other stages.

## Read the specification

Required reference: read this collection's [external workspace contract](../setup-workflow/references/workspace.md). Locate the installed setup-workflow companion if the sibling path is absent; do not install it silently. Resolve the selected project, external context, and active workflow from its registry and task identity. The user need not supply directory paths. Read the external CONTEXT.md and applicable repository instructions or user-maintained context. Keep their scopes explicit. Missing context alone does not block safe work; inaccessible required guidance needs its own blocker. Do not execute closing or completed workflows.

Read the full source specification and relevant code, interfaces, and tests. Resolve an ambiguous source path; the discovery interview is optional.

Extract requirements, acceptance criteria, exclusions, and shared contracts. Preserve source identifiers. If identifiers are absent, use exact headings and local ticket criterion IDs without silently rewriting the specification.

Preserve relevant whole-feature scenario identifiers and source links in the ticket handoffs. Keep cross-component flows visible even when they span several tickets. Carry required startup/testability work into the appropriate implementation scope; do not assume the final verifier will implement missing product behavior or infrastructure. Whole-feature verification happens after the slices are reviewed and available together, not while creating tickets.

Research facts you can find. Ask one focused question only for a material product or scope decision that the specification and available evidence do not resolve. Include a recommendation and its tradeoff. Do not ask the user to approve routine slicing choices.

## Slice by observable outcome

Each normal ticket must deliver one coherent behavior through all affected layers. Include the necessary data, service, API, UI, and implementation checks within that slice. Do not create a backend phase followed by an API phase followed by a frontend phase.

Choose slice boundaries from the feature's actual behavior and dependencies. Each normal slice must support verification of its complete path, without waiting for a later ticket to supply another required layer.

Start with the smallest useful outcome that works on the current code plus explicit prerequisites. Keep its essential validation, authorization, failure handling, and regressions together. Split additional independently useful behavior; combine fragments whose separate delivery adds no observable capability or repeats the same expensive setup and review. Optimize completed, verified outcomes rather than ticket count. For uncertain boundaries, use [the slicing examples](references/slicing.md).

A narrow prerequisite is allowed when it genuinely gates those slices. Explain why it cannot reasonably belong to the first vertical slice, what concrete capability it supplies, and how that capability can be verified. Do not create speculative infrastructure or broad cleanup tickets first.

For changes that cannot be split vertically without breaking compatibility, use an explicit exception: introduce a compatible new form, migrate bounded consumers, then remove the old form after all consumers have moved. Keep each step usable and verifiable. If that is impossible, identify the integration constraint rather than promising independent completion.

Do not defer basic correctness or essential security requirements to later review. Each ticket must describe working implementation and the checks needed to establish that it works. Separate code-quality review, review against the full specification, stylistic cleanup, and broader improvement passes are outside this skill and its sizing budget.

## Size for one agent

Include relevant reading, implementation, debugging, and necessary checks in the assignment's size. Leave meaningful context headroom. Judge scope by distinct behaviors, affected contracts, unfamiliar code, and migration risk. Broad discovery or several substantial risks warrant splitting by usable outcome. Prefer a small coherent slice to filling a context window or creating tiny file-edit tickets.

Record the main uncertainty and sizing rationale. Context is a qualitative constraint: fixed token estimates cannot predict duration. Aim to avoid sprawling, hours-long assignments without promising a runtime. A modest overrun is acceptable when preserving one behavior has a clear benefit; record that sizing exception. Runtime compaction supports continuity, not oversized scope.

## Challenge the draft

Check the draft from three perspectives; a small set needs only one compact audit, not three repeated reads:

1. **Outcome draft:** map every requirement and criterion to the smallest demonstrable vertical outcome.
2. **Verticality challenge:** trace setup, action, and result on the declared starting base. State what a tester can observe if no later ticket runs. Split independently useful outcomes; reunite fragments that need each other to work.
3. **Size and graph challenge:** inspect contracts, uncertainty, and checks. Split separable substantial risks; reject splits that multiply setup, shared edits, or handoffs without reducing risk. Remove ordering-only dependencies, then reconcile coverage and resources.

Record the conclusion in each Sizing section and the index coverage map, not a transcript of each pass. Validator count warnings are prompts for judgment: many acceptance criteria can describe one behavior, and few criteria can conceal an oversized ticket. A clean validator result does not certify scope.

## Define the graph and parallel work

Read [the ticket format](references/ticket-format.md) before creating or updating files. Use stable IDs and file names.

`blocked_by` contains only prerequisite tickets whose required implementation must be reviewed as ready and available before this ticket starts. Explain each dependency's deliverable in the body. Dependencies must be acyclic.

Derive "unblocks" from other tickets' `blocked_by` fields. Do not maintain duplicate reverse edges in every ticket. Ticket numbering and suggested order do not create dependencies.

No dependency does not automatically mean safe parallel work. Use shared exclusive-resource labels for tickets that cannot safely run at the same time because they edit the same unstable contract, migration sequence, or tightly coupled code. Inspect actual boundaries; do not label the entire backend as one exclusive resource.

Prefer existing interfaces or explicitly specified stable contracts for independent slices. If consumers require new producer behavior, keep that real prerequisite; mocks alone do not establish an independently working outcome. Distinguish permanent dependency edges from temporary shared-resource conflicts.

Tickets can run together when their prerequisites are reviewed and available, neither is already assigned, and their exclusive resources do not conflict with implementation or review work. Avoid permanent lists of "parallel with every other ticket"; record the constraints and derive candidates in the index.

For each prerequisite, specify what counts as available to the consumer, such as an implementation revision integrated into its working base. A producer finishing on an inaccessible branch is not sufficient.

## Keep implementation context focused

Include the outcome, necessary rules and contracts, local acceptance criteria, source pointers, boundaries, and a reproducible behavior check. Link directly to relevant spec IDs and prerequisite deliverables; include only necessary excerpts.

Tell the implementation agent to start with its assigned file, then read only needed source sections and prerequisite handoff evidence. Do not require reading the index, every ticket, or the full interview. A wider read is appropriate if a contradiction or missing contract makes it necessary.

For a UI feature, describe how a later testing agent can start the relevant frontend and backend, prepare test data, exercise the complete path, and observe success or failure. Reuse verified project commands when available. Mark unknown setup steps explicitly rather than inventing commands. Do not create review tickets or claim that these checks already ran.

Separate focused slice checks from combined-feature scenarios. Give each slice a reproducible check that establishes its own behavior and affected regressions. Link shared startup instructions and feature-wide checks once; identify their integration trigger instead of copying a long full-suite run into every ticket. Preserve checks required by project policy or the change's risk. If the smallest honest check is expensive, record that constraint; making more tickets may increase total cost.

## Save and maintain the local set

Use the selected external workflow's `tickets/` directory and WORKFLOW.md pointers. Create one Markdown file per ticket and a small `INDEX.md` for assignment and lookup. Specs are normally linked as `../spec.md`; source code remains in the separate assigned checkout. Do not create an in-repository tracker or regenerate a closing/completed ticket set.

Link the set to the spec and record its SHA-256 digest in the index so later runs can detect a changed source. Map each in-scope spec requirement and acceptance criterion to its owning ticket or tickets. If responsibility is shared, explain the division. Do not silently omit requirements or broaden scope.

On later runs, read existing state before changing the set. Preserve IDs, assignments, implementation evidence, and user edits. Do not regenerate completed or active tickets as pending work. If the spec changes, identify affected tickets and record the impact; do not pretend already implemented work meets new requirements.

Split only unstarted work automatically. Preserve the original ID as superseded and point to replacements. For active work, return the proposed split to the assignment coordinator: it must stop writers, preserve implementation evidence, and reconcile leases and acceptance ownership before replanning. Ask the user only when the split requires a material scope or product decision. Never delete history or renumber other tickets to make the sequence look tidy.

When implementation discovers unexpected breadth or a missing prerequisite, replan the unimplemented remainder from current evidence. Keep completed usable behavior and checks attached to its original identity; create bounded remaining outcomes, update downstream edges and coverage, and account for every original criterion. Do not create parallel replacements while an original writer remains active.

The index is a derived summary; ticket files own dependency and lifecycle state. See the format reference for update ownership. Do not mark implementation complete while generating tickets. Do not dispatch or claim tickets during this planning stage.

## Validate and hand off

Run `python3 <skill-directory>/scripts/validate_tickets.py <ticket-directory>`. The validator first rejects closing/completed workflow markers, then checks active metadata, spec-file existence, reference-text presence, graph edges and cycles, and lifecycle conflicts. It prints readiness data for the index. Fix reported errors and refresh the index from the ticket files.

Also check what the script cannot prove: review-report verdicts and freshness, exact spec-heading targets, Markdown links, index freshness and source digest, complete spec coverage, vertical scope, sufficient contracts, realistic size, and safe parallel boundaries. Every in-scope criterion needs explicit ownership; shared ownership states each slice's contribution and the combined scenario that proves the whole. Confirm that every normal ticket has an observable complete path and that every exception has a reason.

Return directory/index paths, ticket count, initial ready work, major blockers, and a sample assignment containing one ticket path. Stop before implementation.

Use short, precise sentences, active voice, and consistent terms.
