---
name: backend-architecture
description: Use when explicitly requested to design backend systems. Also serves as the conditional architecture reference for write-the-spec when work changes APIs, services, persistence, background processing, or backend operational behavior.
license: MIT
disable-model-invocation: true
---

# Backend architecture

Turn backend requirements into specific design choices, with reasons, costs, and verification criteria. Use this skill inside specification work, in the same agent and context. It does not implement code, create tickets, run the application, provision services, or start a review workflow.

## Establish the constraints

Read the supplied brief and relevant project code, schemas, architecture decisions, deployment configuration, and available measurements. Preserve accepted scope and existing contracts. Do not redesign unrelated systems.

Identify the affected request or job path, its users, data owner, and failure consequences. Establish relevant workload characteristics: request rate and bursts, read/write mix, data size and growth, concurrency, tenant distribution, and geographic constraints. Establish existing latency, availability, freshness, recovery, and cost requirements. Use evidence; label estimates and proposals. Do not invent traffic, benchmark results, or numeric targets.

For a narrow change, reuse applicable project policies. Missing measurements do not block design unless they materially affect a choice or acceptance criterion. Do not require a new capacity study for every endpoint.

Research discoverable facts first. For a missing decision that materially changes the product, consistency, cost, or acceptance criteria, ask one focused question with a recommendation and tradeoff. Do not add a routine architecture approval gate. Save independent progress and mark material unknowns.

## Read the relevant guidance

Read [design principles and patterns](references/design.md) for backend design work. Then select references by the affected behavior:

- Persistence, writes, concurrency, queues, or events: [data and messaging](references/data-and-messaging.md).
- Cached reads, expensive repeated work, or cache changes: [caching](references/caching.md).
- Request processing, workers, remote dependencies, latency, capacity, or reliability: [performance and resilience](references/performance.md).

Do not copy the reference catalogue into the spec. These are options, not mandatory infrastructure. Consult linked primary sources and project-version documentation when a choice depends on product-specific behavior. The sources were checked on 2026-09-05; verify current details when using them.

## Choose the smallest sufficient design

Start from the existing architecture. For new systems, evaluate a modular single deployment before distributed services. Recommend added boundaries or infrastructure only when they solve an identified requirement. Keep module boundaries distinct from deployment boundaries.

For each consequential choice, record the requirement served, selected approach, strongest relevant alternative, expected benefit, accepted cost or failure mode, supporting evidence, and condition for reconsideration. Explain disagreement when a proposed pattern does not justify its complexity. Do not equate familiar pattern names with proven scalability.

Define responsibilities, data ownership, contracts, and consistency rules. Locate authentication and authorization checks, including tenant/object access. Bound input sizes, query work, and resource use. Identify sensitive data and its storage, cache, logging, and retention rules. Consult the [OWASP API risks](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) for relevant threats; this is design work, not a security audit.

## Put the decisions in the specification

When called by `write-the-spec`, add findings to that specification's technical design, requirements, verification, and evidence sections. Preserve its identifiers and decision provenance. Do not produce a competing architecture document or invoke the spec skill recursively. When used alone, provide a focused recommendation; write a separate file only when requested or required by the calling task.

Include only applicable contracts: component and data boundaries; sync/async behavior; transaction and retry semantics; cache freshness; resource limits; failure responses; migrations and recovery. A narrow change may reuse established policies by exact reference.

Translate material decisions into measurable acceptance criteria and a proposed verification method. For performance, state the workload, environment, measurement boundary, target source, and relevant percentile or success ratio. Plan cold-cache, concurrent-write, dependency-failure, or overload checks when they test a real design risk. Distinguish future live/load tests from implementation-stage checks; do not execute them here.

Use short sentences, active voice, and consistent terms based on STE principles. Define unfamiliar terms. Do not claim formal ASD-STE100 compliance.
