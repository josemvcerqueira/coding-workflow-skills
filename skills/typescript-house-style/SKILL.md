---
name: typescript-house-style
description: >-
  Write and refactor TypeScript with the user's preferred stack and consistent
  composition conventions using Prettier, ESLint, Drizzle ORM, Remeda, and
  ts-pattern. Use for TypeScript features, readability cleanups, or establishing
  a familiar project style. Prefer this over generic readability guidance for
  TypeScript.
---

# TypeScript House Style

Use a recognizable stack and composition style so readers encounter the same shapes across TypeScript projects. A formatting-only pass is incomplete when workflows still mix business steps with implementation details.

## Preferred stack

| Concern | Default | Convention |
| --- | --- | --- |
| Formatting | Prettier | 100-column print width, two spaces, double quotes, semicolons, trailing commas. |
| Linting | ESLint with TypeScript support | Type-only imports, braces around control-flow bodies, and declaration spacing. |
| Types | TypeScript | `strict` and `noUncheckedIndexedAccess`; infer local and ORM types. |
| Relational persistence | Drizzle ORM | PostgreSQL uses `pg`; named storage operations own queries. |
| Data transformations | Remeda | Reuse its collection helpers and use `pipe` for meaningful multistep transformations. |
| Structured branching | ts-pattern | Match command shapes and discriminated unions; handle all domain variants. |
| Runtime and tests | Bun for new standalone backend projects | Keep an existing project's runtime, package manager, and test runner. |

These are the user's defaults when choosing tooling. Apply libraries where the task needs them: a database-free feature needs no ORM. Reuse installed versions and the lockfile; select compatible versions for new dependencies rather than copying versions from an old example. Explicit user choices take precedence.

In an existing codebase, identify its conventions before editing. Match established configuration for a narrow feature or fix. When adopting this style or cleaning a module, apply it throughout the agreed scope, including callers, tests, fixtures, and exports. A small change in a Prisma project does not authorize a whole database migration; a requested ORM/style migration does require a complete affected path.

## Familiar composition

Use named functions for module-level operations and arrow functions for short callbacks. Put the public workflow first, followed by its private helpers. Group related types near the operations they describe. Prefer named exports and direct imports; preserve framework-required default exports.

Compose a workflow from domain operations at the same level of abstraction:

1. Validate input and permissions.
2. Load the state needed for the decision.
3. Perform the domain action.
4. Record the result and return it.

Use early returns for guard conditions. Add a blank line between meaningful phases. Extract a function when it names a domain step or isolates substantial mechanics; keep obvious expressions inline. Keep external calls and query construction out of the orchestration when they obscure the story.

For backend persistence, use this small boundary, adapted to existing directories:

```text
src/
  db.ts                 connection and transaction ownership
  storage/
    schema.ts           Drizzle table definitions and inferred row types
    orders.ts           named order queries and writes
  orders/
    submit-order.ts     domain workflow
```

Add only the modules needed by the feature. Use focused functions, such as `findPendingOrder`, `saveOrderSignature`, and `markOrderSubmitted`, rather than a generic repository class or a function called `executeQuery`. Integrations own provider-specific mechanics; domain workflows call operations named for their purpose.

## Names and TypeScript shapes

Use camelCase for application values and functions, PascalCase for types, and the project's filename convention. Keep existing database column mappings during a refactor; a style change should not rename persisted fields implicitly.

Use `findOrder` for an optional result and `requireOrder` for an operation that throws when absent. Boolean predicates read as `is…`, `has…`, or `can…`. Commands and writes read as verbs. Name variables for their role rather than their type.

Represent domain alternatives as discriminated unions. Use `ts-pattern` for structured matching where it makes the variants easier to read, with exhaustive handling for closed domain unions. Use ordinary `if` guards for simple conditions. Keep callbacks short; delegate substantial branch bodies to named operations.

Use Remeda for collection operations it expresses clearly, particularly deduplication, grouping, and multistep transformations. Prefer named intermediate results when a pipeline becomes hard to scan. Use simple native expressions when they are already the clearest form.

Infer types from Drizzle schemas and established boundary validators rather than maintaining duplicate row interfaces. Annotate public contracts when this clarifies the API. Treat external input and caught errors as `unknown` and narrow or validate them before use. Type assertions, non-null assertions, and ORM JSON annotations do not perform runtime validation.

## Storage operations with Drizzle

Application workflows call named storage operations. Keep Drizzle query chains inside those operations, including filtering, ordering, and locking. A query should select the fields its caller needs and return a useful domain result rather than exposing driver metadata.

For atomic work, pass the active database transaction or client into every participating storage operation. Prefer the ORM's transaction API for new code; retain an existing client-based transaction boundary when integrations require that exact connection. Never silently query through the global pool during a transaction.

Preserve the existing query contracts when adopting Drizzle: lock targets, `SKIP LOCKED`, ordering, unique constraints, ownership filters, retries, null semantics, restricted database roles, and atomic publication. Keep 64-bit identifiers and exact financial values as strings or bigint according to the existing boundary contract, without conversion to unsafe JavaScript numbers.

Keep necessary SQL fragments parameterized and encapsulated in storage or infrastructure. Database-specific expressions, stored functions, and existing migrations are valid exceptions; ordinary application queries use the ORM. Keep the project's existing migration authority rather than introducing competing migration systems.

## Spacing that stays consistent

Keep imports together, with a blank line before declarations. Separate neighboring functions and exported declarations. Use blank lines to mark phases inside a function, without separating statements that belong to one step. Every `if`, loop, and similar control-flow body uses braces.

Prettier normalizes syntax; ESLint enforces declaration spacing and braces. Use the repo's ESLint rule namespace; where supported, configure `padding-line-between-statements` for a blank line after imports, allow adjacent imports, and require separation around functions and exports. Scope rules to the adopted module when the rest of a repository has another style. Avoid competing formatter rules or adding another formatting tool.

Provide a normal fix command that runs ESLint fixes followed by Prettier, and a check command that runs ESLint with zero warnings and Prettier in check mode. Reuse existing script names rather than creating duplicates.

## Completion

Read a changed entry point continuously before finishing. Its domain steps should be understandable without opening storage or provider implementations. Check that names, imports, spacing, and module boundaries follow the same conventions throughout the affected path.

Run the relevant formatting, lint, type, build, and existing behavior checks. Add focused tests for changed nontrivial logic. Exercise affected database contracts against a real database when changing persistence or transaction behavior; mocked query tests alone cannot establish locking or permissions.

Report what became easier to read, what checks passed, and any checks that remain unavailable. Keep dependency changes and ORM migrations within the requested scope. Publishing and deployment follow the current session's authorization, not this skill.
