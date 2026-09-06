# Performance, scale, and resilience

## Make latency measurable

Define the user-visible operation and where timing starts and ends. State workload, data volume, payload sizes, concurrency, geography, and environment. Use an agreed latency percentile or proportion below a threshold, plus error rate. Do not substitute an average for tail behavior or invent a universal millisecond target. [Google's SLO guidance](https://sre.google/workbook/implementing-slos/) links measurable objectives to user experience.

Map the critical path: queue wait, application work, database work, and remote calls. Allocate budgets with headroom. Address repeated queries, N+1 access, unbounded results, unnecessary serialization, and network round trips before adding services. Use connection pools with explicit limits. Parallelize independent work only within dependency capacity. Moving work to a queue changes completion semantics; it does not make the work disappear.

Use representative query plans and data distributions when evaluating database performance. Indexes improve selected reads but consume storage and write effort. [PostgreSQL's EXPLAIN documentation](https://www.postgresql.org/docs/current/using-explain.html) provides a concrete method; use the actual database/version documentation. `EXPLAIN ANALYZE` executes the statement, so do not run it against live mutations as a supposedly read-only check.

## Design for bounded capacity

Keep request handlers free of required instance-local session state when replicas must be interchangeable. State where durable state lives. Bound concurrency, queues, payloads, page sizes, connections, and expensive per-request work. Protect tenant fairness.

Identify the first likely shared bottleneck and how it will be measured. More API replicas can overload the database through more connections. Separate worker and request capacity where workloads interfere. Define scaling signals, startup delay, maximum scale, and downstream limits. Consider vertical scaling and query improvements before sharding. Sharding requires a key strategy, hot-key handling, rebalancing, and cross-partition behavior.

Use load shedding or backpressure before unlimited queuing causes failure. Specify client-visible rejection and retry behavior. [Google's overload guidance](https://sre.google/sre-book/handling-overload/) explains why protecting useful work is necessary under saturation.

## Contain failures

Set request and connection deadlines from the end-to-end budget and measured dependency behavior. Propagate cancellation where supported. Specify retryable failures, bounded attempts, backoff, jitter, and one responsible retry layer. Retrying mutations requires safe duplicate handling. See [AWS's timeouts and retries guidance](https://d1.awsstatic.com/builderslibrary/pdfs/timeouts-retries-and-backoff-with-jitter.pdf).

Use bulkheads (separate resource pools) when one dependency can consume capacity needed by others. A circuit breaker can stop futile calls but adds recovery states and tuning; use it for a concrete failure mode, not by default. Define degraded behavior explicitly. Never turn a dependency error into a false success.

Specify relevant metrics, structured logs, trace propagation, and alerts without secret payloads or uncontrolled label cardinality. Include readiness, graceful shutdown, backup/restore, and recovery objectives when affected. Plan load, burst, slow-dependency, and recovery tests. Record expected outcomes; this design skill does not run them or certify performance.
