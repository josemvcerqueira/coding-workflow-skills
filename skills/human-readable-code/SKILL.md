---
name: human-readable-code
description: Make existing code easy for humans to read. Use when the user asks for readable, clean, human-written, or senior-quality code, complains about cramped formatting or inline SQL, or wants clearly named query functions. Covers spacing, workflow structure, names, persistence boundaries, and checks that preserve behavior.
---

# Human Readable Code

A cleanup request includes how the code reads, not just whether a formatter accepts it. Complete the readability pass in the first attempt; do not wait for separate prompts about spacing, names, or database boundaries.

## Inspect the reading path

Read the main entry point, a representative complete workflow, its helpers, and the repository's instructions and tooling. Find callers, tests, fixtures, and exports affected by changes before editing.

Identify where a reader must decode syntax, infer a name's meaning, or switch between business decisions and implementation mechanics. Use those findings to choose the smallest coherent change within the requested scope.

## Make the workflow tell the story

Keep orchestration at one level of abstraction. Give meaningful domain operations names that explain their purpose, such as `findPublishableCommands`, `markCommandQueued`, or `savePreparedOrder`. A reader should understand the workflow before inspecting those implementations.

Place the main operation before its supporting helpers when language rules and project conventions allow. Keep related helpers together. Extract a helper when it names a meaningful step or isolates distracting mechanics; keep obvious expressions inline. Avoid scattering a simple operation across forwarding wrappers or generic factories.

Use names that reveal behavior and outcomes. A throwing precondition reads like `requireTradingEnabled`; a boolean predicate reads like `isTradingEnabled`. Replace opaque production variable names when their meaning requires reconstruction.

## Give the eye useful boundaries

Use the project's formatter. For JavaScript and TypeScript, use Prettier when requested or already adopted; use the language's normal formatter elsewhere.

Separate imports from declarations and neighboring functions from one another. Keep an import block together. Add blank lines between meaningful phases inside functions, such as validation, loading, execution, and recording the result. Keep closely related statements together. Wrapping long lines is not a substitute for grouping the steps.

Prettier does not choose all semantic spacing. Use existing lint tooling to enforce stable declaration spacing and explicit control-flow blocks where appropriate. Add scoped rules when needed and leave an executable formatting check in the project's normal workflow. Avoid unrelated repository-wide formatting churn.

## Put persistence behind named operations

Keep query syntax inside focused storage functions; expose their purpose to business workflows. A helper named `executeQuery` does not communicate the operation.

Prefer the existing ORM or typed query layer. When ORM adoption is requested, choose a compatible library and implement the affected persistence path fully, including schema mappings, callers, and fixtures. An ORM still needs well-named operations; replacing a SQL string with a long inline query chain is an incomplete readability pass.

For example, a worker should read:

```ts
const commands = await findPublishableCommands(client);

for (const command of commands) {
  const queueId = await publishCommand(client, command);

  await markCommandQueued(client, command.id, queueId);
}
```

The storage operation owns the filtering, ordering, and row-locking details. Preserve the same transaction and connection throughout atomic work.

Before changing queries, identify their contracts: row-lock targets and `SKIP LOCKED`, ordering, deduplication, null handling, retries, permissions, and exact numeric values. Preserve identifiers and money without lossy number conversion. Exercise these contracts against the actual database when they are affected.

Keep necessary database-specific SQL parameterized and encapsulated in storage or infrastructure, such as an existing restricted stored function or migration. Do not force an ORM dependency for an unrelated cleanup or rewrite working migrations merely to eliminate every SQL fragment.

## Verify the result as a reader and as a maintainer

Read the changed workflow continuously from its entry point. Finish only when:

- Names explain the steps without requiring helper bodies to understand their purpose.
- Spacing makes declarations and workflow phases easy to scan.
- Business decisions are readable without embedded query or transport mechanics.
- Each extraction earns its place by naming a concept or hiding complexity.
- Changed callers, fixtures, configuration, and exports are consistent.
- Relevant formatting, lint, type, build, and behavior checks pass, or their limits are explicitly reported.

Use existing tests for behavior-preserving edits. Add focused regression coverage for changed nontrivial behavior and database contracts; do not add tests that merely restate formatting or wrapper implementations. Distinguish mocked checks, real database checks, and live external-service verification.

Report the concrete readability improvements and verification. A subjective request for “10/10” is a quality target, not grounds to claim perfection. Publishing follows the user's authorization in the current session; this skill adds none.
