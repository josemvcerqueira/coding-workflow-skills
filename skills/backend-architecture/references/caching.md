# Caching

First identify the repeated work, expected reuse, and acceptable staleness. Caching can reduce origin load and read latency, but adds invalidation, memory, and failure costs. Do not introduce it solely because a backend exists.

## Select a policy

| Choice | Benefit | Cost or risk |
| --- | --- | --- |
| No cache | Simple consistency and operations | Repeated origin work |
| Local cache | Avoids a network hop | Per-instance duplication and inconsistent copies |
| Shared cache | Reuses entries across instances | Network latency and another shared dependency |
| Cache-aside | Loads useful entries on demand | Miss penalty and stale reads during update races |
| Write-through | Updates cache on the write path | More write latency; partial failures still require a policy |
| Write-behind | Can reduce foreground write delay | Durability, ordering, and recovery complexity |

See [Microsoft's cache-aside guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside) for consistency and suitability tradeoffs. No cache pattern name alone guarantees read-after-write consistency.

## Write the cache contract

Specify these fields for each important cached object or query:

- Authoritative source and exact cached value.
- Key dimensions, including tenant, user/permission scope, query parameters, and representation version as applicable.
- Maximum permitted staleness and the reason for its expiry policy. A TTL is not a substitute for required invalidation.
- Write, deletion, and permission-change invalidation, including concurrent read/refill races. Use a version or equivalent coordination when freshness requires it.
- Entry size, memory bound, eviction behavior, and negative-result caching policy.
- Miss, cache failure, stale-data, and cold-start behavior. Define when stale data is forbidden.

Protect the origin during misses and outages. Consider coalescing concurrent requests for the same key, staggered expiry, bounded refresh work, and admission limits. Do not allow cache failure to send unlimited traffic to an already saturated database. Use stale-while-revalidate only when the product permits the resulting freshness window.

Authentication and tenant isolation must remain correct on cache hits. Do not serve another user's data or retain revoked authorization because a cache entry is valid by time alone. Minimize sensitive cached content and specify access and deletion controls.

Observe hit rate by useful workload, miss latency, origin load, memory, evictions, refresh failures, and stale responses. Plan warm-cache and cold-cache measurements. [Redis eviction documentation](https://redis.io/docs/latest/develop/reference/eviction/) illustrates why memory and eviction policies are separate from expiry; use the selected cache's actual guarantees.
