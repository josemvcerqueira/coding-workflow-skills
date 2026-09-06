---
name: spec-to-tickets
description: Convert an engineering specification into local Markdown tickets with vertical scope, spec references, explicit dependencies, and parallel-work constraints. Use when the user invokes this skill to prepare or maintain a filesystem ticket set for one implementation agent per ticket.
license: MIT
disable-model-invocation: true
---

# Spec to tickets

Create the complete local ticket set from an engineering specification. Size each ticket so that one implementation agent can complete it later in roughly one 200,000-token context window. Preserve the specification's scope and make dependencies explicit.

This skill creates and maintains ticket documents. It does not implement features, dispatch implementation agents, create web issues, or perform later reviews.

## Priorities

1. Prefer a narrow, working vertical slice over a collection of layers.
2. Make each ticket sufficient for one future implementation agent to start, with precise links for more context.
3. Record real dependencies and shared-resource conflicts.
4. Size for working implementation within roughly one 200,000-token context window.
5. Save and validate the ticket set directly, without a final approval gate.

## Read the specification

Required reference: read this collection's [external workspace contract](../setup-workflow/references/workspace.md). Locate the installed setup-workflow companion if the sibling path is absent; do not install it silently. Resolve the selected project, external context, and active workflow from its registry and task identity. The user need not supply directory paths. Read the external CONTEXT.md and applicable repository instructions or user-maintained context. Keep their scopes explicit. Missing context alone does not block safe work; inaccessible required guidance needs its own blocker. Do not execute closing or completed workflows.

Read the source specification in full and inspect relevant project instructions, code, interfaces, and tests. Do not require the discovery interview. Resolve an ambiguous source path before proceeding.

Extract requirements, acceptance criteria, exclusions, and shared contracts. Preserve source identifiers. If identifiers are absent, use exact headings and local ticket criterion IDs without silently rewriting the specification.

Preserve relevant whole-feature scenario identifiers and source links in the ticket handoffs. Keep cross-component flows visible even when they span several tickets. Carry required startup/testability work into the appropriate implementation scope; do not assume the final verifier will implement missing product behavior or infrastructure. Whole-feature verification happens after the slices are reviewed and available together, not while creating tickets.

Research facts you can find. Ask one focused question only for a material product or scope decision that the specification and available evidence do not resolve. Include a recommendation and its tradeoff. Do not ask the user to approve routine slicing choices.

## Slice by observable outcome

Each normal ticket must deliver one coherent behavior through all affected layers. Include the necessary data, service, API, UI, and implementation checks within that slice. Do not create a backend phase followed by an API phase followed by a frontend phase.

Choose slice boundaries from the feature's actual behavior and dependencies. Each normal slice must support verification of its complete path, without waiting for a later ticket to supply another required layer.

A narrow prerequisite is allowed when it genuinely gates those slices. Explain why it cannot reasonably belong to the first vertical slice, what concrete capability it supplies, and how that capability can be verified. Do not create speculative infrastructure or broad cleanup tickets first.

For changes that cannot be split vertically without breaking compatibility, use an explicit exception: introduce a compatible new form, migrate bounded consumers, then remove the old form after all consumers have moved. Keep each step usable and verifiable. If that is impossible, identify the integration constraint rather than promising independent completion.

Do not defer basic correctness or essential security requirements to later review. Each ticket must describe working implementation and the checks needed to establish that it works. Separate code-quality review, review against the full specification, stylistic cleanup, and broader improvement passes are outside this skill and its sizing budget.

## Size for one agent

Use 200,000 context tokens as a soft planning envelope, not a token allowance to spend or a promise. Account for the ticket, relevant source reading, reasoning, tool outputs, code changes, debugging, and necessary implementation checks. Leave headroom for uncertainty.

Aim for bounded assignments that an agent can finish without a sprawling, hours-long implementation effort. Context tokens do not reliably predict elapsed time, so do not promise a duration. Treat many independent behaviors, broad discovery, or several major subsystem changes as reasons to reduce scope. A smaller coherent slice is preferable to filling the context window.

Judge scope by affected contracts, unfamiliar code, migration risk, and the number of distinct behaviors. Do not invent precise token estimates. Record a short sizing rationale and the main uncertainty.

Split an oversized ticket by behavior or use case while preserving a working path. Do not replace a meaningful slice with tiny file-edit tickets just to reduce context. A modest overrun is acceptable when keeping the behavior together has a clear benefit. Mark the sizing exception and explain that tradeoff; do not use the exception to justify a substantially oversized assignment.

## Define the graph and parallel work

Read [the ticket format](references/ticket-format.md) before creating or updating files. Use stable IDs and file names.

`blocked_by` contains only prerequisite tickets whose required implementation must be reviewed as ready and available before this ticket starts. Explain each dependency's deliverable in the body. Dependencies must be acyclic.

Derive "unblocks" from other tickets' `blocked_by` fields. Do not maintain duplicate reverse edges in every ticket. Ticket numbering and suggested order do not create dependencies.

No dependency does not automatically mean safe parallel work. Use shared exclusive-resource labels for tickets that cannot safely run at the same time because they edit the same unstable contract, migration sequence, or tightly coupled code. Inspect actual boundaries; do not label the entire backend as one exclusive resource.

Tickets can run together when their prerequisites are reviewed and available, neither is already assigned, and their exclusive resources do not conflict with implementation or review work. Avoid permanent lists of "parallel with every other ticket"; record the constraints and derive candidates in the index.

For each prerequisite, specify what counts as available to the consumer, such as an implementation revision integrated into its working base. A producer finishing on an inaccessible branch is not sufficient.

## Keep implementation context focused

Place the minimum task context in each ticket: outcome, relevant rules and contracts, local acceptance criteria, source pointers, boundaries, and a reproducible behavior check.

Link directly to the specification and the relevant requirement or section IDs. Include only necessary excerpts. Link prerequisite tickets with a short description of what the consumer needs from them. Other tickets and the full spec remain available for targeted reading.

Tell the implementation agent to start with its assigned file, then read only needed source sections and prerequisite handoff evidence. Do not require reading the index, every ticket, or the full interview. A wider read is appropriate if a contradiction or missing contract makes it necessary.

For a UI feature, describe how a later testing agent can start the relevant frontend and backend, prepare test data, exercise the complete path, and observe success or failure. Reuse verified project commands when available. Mark unknown setup steps explicitly rather than inventing commands. Do not create review tickets or claim that these checks already ran.

## Save and maintain the local set

Use the selected external workflow's `tickets/` directory and WORKFLOW.md pointers. Create one Markdown file per ticket and a small `INDEX.md` for assignment and lookup. Specs are normally linked as `../spec.md`; source code remains in the separate assigned checkout. Do not create an in-repository tracker or regenerate a closing/completed ticket set.

Link the set to the spec and record its SHA-256 digest in the index so later runs can detect a changed source. Map each in-scope spec requirement and acceptance criterion to its owning ticket or tickets. If responsibility is shared, explain the division. Do not silently omit requirements or broaden scope.

On later runs, read existing state before changing the set. Preserve IDs, assignments, implementation evidence, and user edits. Do not regenerate completed or active tickets as pending work. If the spec changes, identify affected tickets and record the impact; do not pretend already implemented work meets new requirements.

Split only unstarted work automatically. Preserve the original ID as superseded and point to replacements. For active work, identify the conflict and resolve it with the user before redefining the assignment. Never delete history or renumber other tickets to make the sequence look tidy.

The index is a derived summary; ticket files own dependency and lifecycle state. See the format reference for update ownership. Do not mark implementation complete while generating tickets. Do not dispatch or claim tickets during this planning stage.

## Validate and hand off

Run `python3 <skill-directory>/scripts/validate_tickets.py <ticket-directory>`. The validator first rejects closing/completed workflow markers, then checks active metadata, spec-file existence, reference-text presence, graph edges and cycles, and lifecycle conflicts. It prints readiness data for the index. Fix reported errors and refresh the index from the ticket files.

Also check what the script cannot prove: review-report verdicts and freshness, exact spec-heading targets, Markdown links, index freshness and source digest, complete spec coverage, vertical scope, sufficient contracts, realistic size, and safe parallel boundaries. Confirm that every normal ticket has an observable complete path and that every exception has a reason.

Return the directory and index paths, ticket count, and a concise summary of the initial ready work and major blockers. Give a sample assignment containing one ticket path. Do not dump every ticket into the response or begin implementation.

Use short sentences, active voice, consistent terms, and explicit conditions based on STE principles. Preserve technical precision; do not claim formal ASD-STE100 compliance.
