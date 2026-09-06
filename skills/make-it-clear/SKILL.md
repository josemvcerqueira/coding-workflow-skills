---
name: make-it-clear
disable-model-invocation: true
license: MIT
description: Clarify a confusing explanation, concept, decision, or task state. Use when the user explicitly invokes make-it-clear to understand the current conversation or regain context.
---

# Make it clear

Help the user understand the relevant idea or situation without requiring them to reconstruct the conversation. Treat confusion as a signal to change the explanation.

## Identify the need

Use the user's wording and nearby conversation to choose the smallest useful response:

- **Concept or statement:** Explain what it means, give a concrete example, and connect it to the user's task when relevant.
- **Reasoning or decision:** Explain the problem, why the approach helps, and the material tradeoff. Mention alternatives only when they clarify the choice.
- **Task orientation:** State the goal, current problem, approach, verified progress, and next step. Say whether the user needs to decide or do anything.
- **Mixed or unspecified confusion:** Start with a brief orientation and explain the likely point of confusion. Ask one focused question only if the ambiguity still prevents a useful explanation.

Do not force every response into a progress report. A question about one term usually needs only that term explained in context.

## Explain differently

Lead with the practical meaning or purpose. Add only the background needed to understand it.

Use plain English inspired by Simplified Technical English: direct sentences, concrete verbs, and consistent terminology. Do not claim formal ASD-STE100 compliance.

Define an unfamiliar term before relying on it. Preserve exact identifiers when needed to locate something, but explain what they do. Use established project terminology when available and relevant; do not require a particular context file or assume the user understands its vocabulary.

If the earlier explanation failed, change the approach: use a specific example, break down a missing prerequisite, or trace cause and effect. Avoid repeating the same jargon with minor wording changes. Use an analogy only when it clarifies the idea, and explain a significant limitation if it could mislead.

Use a small table or diagram when relationships are easier to see than describe. Prefer prose for a simple explanation.

Aim for a first response that takes about thirty seconds to read, unless the user asks for depth or the concept requires more. Give enough detail to resolve the confusion; brevity must not remove the essential explanation. Avoid obligatory headings, recaps, and "does that make sense?" endings.

## Ground the explanation

Base task status on available evidence. Distinguish planned, attempted, completed, and verified work. Separate confirmed causes from hypotheses. If a missing fact matters, inspect the relevant available source or say what is unknown; do not invent progress, reasons, completion percentages, or time estimates.

## Preserve the ongoing task

Address the confusion before continuing dependent work. A request for explanation does not cancel the original task or authorize a new implementation. Continue previously authorized work after explaining, unless the user asks to pause or a necessary decision remains unresolved. Do not require confirmation merely because this skill was invoked.

## Examples of scope

- "What is a refresh token?" → Explain the token and its role in keeping someone signed in; omit unrelated task history.
- "Why change the database?" → Explain the limitation the change addresses and the relevant tradeoff.
- "I've been away. Where are we?" → Give the goal, evidence-backed status, remaining work, and next step.
- "Wait, what?" after a dense explanation → Re-explain the central claim with a concrete example and the minimum context needed.
