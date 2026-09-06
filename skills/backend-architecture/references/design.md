# Design principles and patterns

Use principles to explain decisions, not to require a class hierarchy or folder structure.

## Coding principles

- **Single responsibility:** keep policies that change for different reasons separate. This reduces change impact; excessive splitting adds navigation and coordination cost.
- **Open/closed:** use an extension point for a demonstrated family of variations. This protects stable behavior; speculative extension frameworks add complexity.
- **Liskov substitution:** replacement implementations must preserve the caller's contract, including errors and invariants. Shared method names alone are not enough.
- **Interface segregation:** expose the capabilities a caller needs. This reduces coupling; an interface per trivial function can add noise.
- **Dependency inversion:** business rules depend on stable contracts rather than transport or vendor details. This improves isolation and testing; use indirection where it has a concrete benefit.

These are the SOLID principles. They apply to module contracts as well as object-oriented code. See [Robert C. Martin's explanation](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html).

Prefer cohesive domain modules, explicit side effects, and simple control flow. Keep one authoritative definition of a business rule. Do not merge unrelated rules only because their code looks similar. Apply KISS (keep the design simple), DRY (avoid duplicated knowledge), and YAGNI (do not build speculative capabilities) as decision heuristics, not absolute bans on duplication or future planning.

## Select a structural pattern

| Pattern | Benefit and suitable use | Cost and design obligation |
| --- | --- | --- |
| Modular monolith | One deployment with explicit business modules; simple local calls and transactions | Shared release and resource limits; prevent arbitrary cross-module writes |
| Layered design | Separates transport, use cases, and persistence | Avoid pass-through layers that add no policy; organize features coherently |
| Hexagonal / ports and adapters | Keeps domain behavior separate from database, network, and framework adapters | Define small ports for actual use cases; do not wrap every library call |
| Microservices | Independent deployment, ownership, or scaling where required | Network failures, distributed data, and operational cost; define service ownership and contracts |
| Queue and worker | Moves suitable long-running work out of request handling | Completion becomes asynchronous; define status, failure, and queue limits |
| Event-driven design | Lets independent consumers react to facts | Delivery, ordering, schema evolution, and tracing need explicit rules |

Do not choose microservices only because future growth is possible. [Fowler's monolith-first argument](https://martinfowler.com/bliki/MonolithFirst.html) is a useful starting heuristic, not proof that every system should begin as a monolith. [Microsoft's style comparison](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/) explains the operational tradeoffs. [Cockburn's original ports-and-adapters article](https://alistair.cockburn.us/hexagonal-architecture) explains separation from external technology.

Use domain-driven design boundaries when business rules and terminology justify them. Do not require aggregates and repositories for simple CRUD. A repository can protect a domain persistence boundary; a generic wrapper that only repeats an ORM may add no value. A strategy can isolate interchangeable policies; a factory can centralize nontrivial construction. Choose these for a real variation or invariant, not as a checklist.
