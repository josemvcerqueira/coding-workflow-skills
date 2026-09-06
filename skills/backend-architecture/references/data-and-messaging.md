# Data and messaging

## Define correctness before distribution

Identify the authoritative store and owner for each entity. State uniqueness, permitted state transitions, and invariants that must hold under concurrent requests. Select a transaction boundary and concurrency strategy that actually protect those invariants. Do not assume an application-level check followed by a write is atomic.

Choose storage from access patterns, consistency, operations, and project constraints. A relational database is a strong candidate for related transactional data, not a universal mandate. Specify expected queries, pagination, useful indexes, and write costs. Explain read-replica lag when read-after-write behavior matters. Plan compatible schema changes, backfill, and recovery; do not assume every destructive migration can be rolled back.

## Select advanced patterns only for a demonstrated need

| Pattern | Advantage | Cost and required contract |
| --- | --- | --- |
| CQRS | Different read/write models can serve different workloads | Projection lag and extra models; separate databases are optional |
| Event sourcing | Preserves domain events for reconstruction and historical interpretation | Event evolution, replay, retention, and projections; not just an audit log |
| Transactional outbox | Commits a state change and outgoing event record in one local transaction | Relay and cleanup required; delivery can repeat, so consumers need deduplication |
| Saga | Coordinates a workflow across independent local transactions | Compensation is business behavior, not an atomic rollback; intermediate state is visible |

Use [Microsoft's CQRS guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs) to distinguish read/write separation from event sourcing. [AWS's outbox guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) addresses the database/message dual-write failure. [Microsoft's saga guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga) explains compensation and isolation costs.

## Specify delivery and duplicate handling

For each asynchronous path, define acknowledgment meaning, delivery semantics, ordering scope, retry owner, maximum attempts or age, poison-message handling, and a controlled replay procedure. An accepted job is not a completed job. State how users discover success or failure.

For an idempotent mutation, define key scope, payload mismatch handling, concurrent duplicate behavior, result retention, and what happens after a timeout. Coordinate duplicate detection with the side effect. A key stored after the effect can still permit duplicates. Do not promise exactly-once business effects solely because a broker offers an exactly-once mode.

Bound worker concurrency and backlog. Record retention, cancellation, and overload behavior. Use compatible event schemas and identify which component owns each event. Avoid shared mutable tables between independently owned services unless that coupling is a deliberate, documented constraint.
