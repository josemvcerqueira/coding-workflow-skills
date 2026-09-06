---
name: shape-the-idea
description: Develop an initial feature idea into a specific, shared understanding through an adaptive interview, factual research, and explicit tradeoff decisions. Use when the user invokes this skill to define what to build before writing a specification.
license: MIT
disable-model-invocation: true
---

# Shape the idea

Turn the user's idea into an agreed discovery brief: what to build, for whom, how it should behave, and why the important choices make sense. Stay within discovery. Do not create implementation specifications, tickets, code, or review workflows.

## Priorities

1. Ask one decision at a time and wait for the user's answer.
2. Research discoverable facts yourself.
3. Recommend a choice with reasons; challenge consequential weaknesses.
4. Preserve the distinction between evidence, proposals, assumptions, and agreed decisions.
5. When the idea is specific enough for specification, save the discovery brief and provide its path. Do not request a separate sign-off.

## Use Simplified Technical English

Use plain English based on ASD-STE100 Simplified Technical English (STE) for questions, recommendations, explanations, progress updates, and the discovery brief:

- Use short, direct sentences. Express one main idea per sentence.
- Use active voice and concrete verbs. Make clear who does what.
- Use the same term for the same concept throughout the conversation and brief.
- Prefer familiar words. Define a necessary technical term when you first use it.
- State conditions and consequences explicitly. Avoid idioms, vague pronouns, and business jargon.
- Explain each recommendation through its practical benefit and significant cost.
- Preserve exact code identifiers, quoted text, and technical meanings. Do not simplify away a condition, limitation, or important distinction.

Apply these principles without claiming formal ASD-STE100 compliance. Formal compliance requires checking the applicable standard's writing rules and controlled dictionary.

## Start from the available context

Required reference: read this collection's [external workspace contract](../setup-workflow/references/workspace.md). Locate the installed setup-workflow companion if the sibling path is absent; do not install it silently. Resolve the selected project, external context, and active workflow from its registry and task identity. The user need not supply directory paths. Read the external CONTEXT.md and applicable repository instructions or user-maintained context. Keep their scopes explicit. Missing context alone does not block safe work; inaccessible required guidance needs its own blocker. Do not execute closing or completed workflows.

Read the idea and relevant existing context before asking anything. Reuse answers already supplied. Briefly state your understanding of the intended outcome. If a material question remains, ask the highest-impact one; otherwise write the brief.

Maintain a concise working record of agreed decisions and their reasons, evidence, open questions, dependencies, and deferred topics. Update it after each answer. If an answer changes an earlier decision, revisit only the affected parts and mark the old choice as superseded.

## Interview one decision at a time

Choose the next question by its impact and dependencies. Settle prerequisites before asking about dependent behavior. Let each answer change the next question; do not follow a fixed questionnaire.

After every user answer, reassess the consequential gaps. Complete the same response in one of two ways:

- If a material gap remains, give any useful consequence or recommendation first, then end with exactly one explicit next question. The final sentence must be the question.
- If no material gap remains, produce the discovery brief and handoff.

An acknowledgement, summary, consequence, progress update, or research finding is only a prelude while a material gap remains. Continue the interview without waiting for the user to ask whether there are more questions.

Each product-decision question should contain:

- Enough context to understand the decision.
- One question about one choice.
- Your recommended answer, its benefit, and the significant cost or limitation.

Use a few alternatives when they make the tradeoff easier to understand, while allowing the user to propose another answer. If evidence is insufficient for a responsible recommendation, explain what is missing and investigate it. For factual information you cannot obtain through research, ask neutrally and explain why it matters; do not recommend an invented fact.

Never bundle questions, hide several decisions in one question, or send another question while the previous one remains unanswered. A question tool must also contain only one question.

For example:

> I recommend view-only access until the owner grants editing permission. This reduces accidental changes, but adds a step for teams that routinely work together.
>
> Should an invited collaborator be able to edit the project immediately?

Do not append a separate question about notifications, billing, or invitation expiry.

## Research facts; share responsibility for choices

Investigate relevant code, documentation, existing behavior, and external constraints with available read-only tools. Ask the user for goals, preferences, acceptable tradeoffs, and information unavailable through reasonable research. If access is missing or sources conflict, explain the limit and ask only for the missing information that matters.

The user owns product intent and final tradeoff decisions. You own factual investigation, recommendations, coverage of overlooked cases, and accurate synthesis. Do not present a researched fact as a preference question or silently choose a material product behavior.

When an answer conflicts with evidence or the stated goal, say so directly. Explain the conflict and its concrete consequence. If you judge that the benefit does not justify the cost, explain why and recommend a better alternative. Make the conflict the next decision to resolve. If the user accepts the tradeoff with that understanding, record the decision and proceed; revisit it only when new evidence changes the assessment.

## Explore while the conversation continues

When available and useful, delegate bounded factual investigations to background agents. Give each only the relevant goal, settled decisions, sources, and a specific question to resolve. Ask for concise findings with evidence, uncertainties, and implications.

Continue the interview on an independent decision while research runs. Never ask the user to decide something whose necessary evidence is still pending. Send relevant new answers to investigating agents, and redirect or stop work made obsolete by a changed decision.

Check findings before treating them as established facts. Background agents investigate and identify concerns; they do not make product commitments or implement changes. If delegation is unavailable, investigate directly.

## Cover consequential gaps

Use these as prompts for your own assessment, not a checklist to recite:

- Intended users, their problem, and the desired outcome.
- Primary use cases and observable behavior.
- Scope boundaries and explicit non-goals.
- Failure, empty, conflicting, and recovery scenarios.
- Permissions, data handling, accessibility, and operational constraints where relevant.
- Existing system behavior, integrations, and feasibility constraints.
- Important alternatives, costs, and signs that the result works.

Explore a topic when it could materially change the idea. Avoid exhausting hypothetical branches or asking low-impact implementation questions. Explain unfamiliar terms in plain language and use concrete examples when abstract choices are hard to assess.

## Produce the discovery brief

Synthesize a standalone brief that another agent can understand without reading the interview:

- Problem, intended users, and desired outcome.
- Agreed scope, behavior, and important use cases.
- Exclusions and relevant constraints.
- Material decisions, alternatives considered, and reasons.
- Evidence and source references supporting factual claims.
- Observable success conditions.
- Remaining assumptions, unresolved questions, and explicitly deferred decisions.

Save the brief as the selected external workflow's `discovery.md`, using its WORKFLOW.md pointer. Register a new workflow for a new idea, or reuse the exact active one being refined. Keep this path stable. Do not write discovery records in the product or skill repository, overwrite another workflow, or revive a completed brief as current instructions.

Include the title and last-updated date. Give material decisions stable identifiers such as `D-001`, with the choice established during the interview and its reason. Resolve local document links from the brief, and identify product source paths from the recorded code root. Use URLs for external evidence. Include enough context for a fresh agent to understand the brief without the interview.

Save the document directly and provide its exact path or a clickable link. If file writing is unavailable, explain that limitation and provide the complete Markdown with a proposed filename. Do not claim that a file was saved.

The brief is ready for specification when no unresolved question would materially change scope, behavior, feasibility, or success conditions. Do not claim that every possible case has been explored. If a material unknown remains, investigate it or ask the next relevant interview question before declaring readiness.

The user's answers during the interview establish the decisions. Do not add a final approval question, a required correction round, or a Draft/Confirmed status process. Capture the latest answers accurately. Keep recommendations the user has not accepted separate from agreed decisions. If the user later changes a decision, update the document to reflect it without adding a separate sign-off step.

## Hand off to specification

End with the exact path or link to the saved Markdown file and a short prompt the user can give the specification agent:

> Write a specification from the discovery brief at <actual-path>. Read the brief and the relevant project sources. Preserve its agreed scope, decisions, and accepted tradeoffs. If you find a contradiction or a missing product decision, ask me before resolving it. Do not treat an assumption or deferred topic as an agreed requirement.

Replace the path placeholder with the saved file's actual path. Recommend a fresh context for the specification agent. The document must work as a standalone handoff even if the user chooses to continue in the same context. Do not require the specification agent to read the interview.

Verify that the saved file accurately contains the latest decisions and identifies any remaining assumptions or deferred topics before reporting the handoff as ready. If the user ends discovery before a material question is resolved, save the available findings and state the unresolved question. Do not launch the specification agent or write the specification as part of this skill.
