# Choosing a useful slice

Use these examples when a draft's boundaries are uncertain. Adapt them to the actual specification and existing code; the examples do not add requirements.

## Separate useful behavior

Suppose saved filters require creating, listing, and deleting filters. Existing authentication, persistence, and navigation already work.

- **Create a saved filter:** submit through the real entry point, persist it, and observe confirmation. Include invalid input and ownership checks required by the spec. Verify persistence through the existing public read boundary or an appropriate integration check; a new filter-list screen is not required unless the specified creation journey needs it.
- **List saved filters:** open the list and see the current user's stored filters, including the required empty state. Its test can seed valid stored data. If creation introduced the required schema or read interface, record that real prerequisite; otherwise the existing contract may permit parallel work.
- **Delete a saved filter:** remove a selected filter and verify it stays removed. Include the required unauthorized and missing-filter behavior. If the only specified entry point is a list action, depend on the usable list slice.

Each outcome includes its necessary layers. Separate schema, API, UI, validation, and test tickets would leave these paths incomplete. Conversely, combining all three useful outcomes solely because they share a feature name makes the assignment needlessly broad.

## Keep an atomic outcome together

A payment submission may need idempotency, authorization, persistence, failure handling, and several assertions. Those criteria can describe one inseparable correctness boundary. Their count is not evidence that validation and failure handling should ship separately. Split additional payment methods or independent user journeys when the specification permits it.

Use a narrow prerequisite only when a reusable capability genuinely cannot belong to the first usable slice. Name the consumers, its own executable check, and why the extra handoff earns its cost. A stable interface removes coordination uncertainty; a mocked future producer does not make a missing production path work.

## Avoid multiplying an expensive test

If a focused check proves each slice and one combined journey takes an hour, link that journey to the combined-feature stage. Repeat it earlier only when required policy, a changed shared contract, or regression risk makes it necessary. If every proposed fragment still needs that hour-long check and none is useful alone, combine them. If the expensive check is the only evidence for a slice, keep it required and state the cost honestly.

## Replan from evidence

When a worker discovers an unexpected migration, preserve its code and check evidence, report the affected criteria, and propose a bounded remainder. The assignment coordinator first stops active writers and reconciles their ownership. The planner then updates only that remainder, consumers, and the coverage map. Already working behavior stays traceable; replacement tickets cannot overlap an active original assignment.

Record an old-to-new criterion map before changing lifecycle state. Preserve the original ticket's criteria, identity, and implementation evidence. Either retain that ticket until its full acceptance is satisfied, or mark the stopped original `superseded` and name replacement IDs in `superseded_by`. Replacements must collectively cover every original criterion, including already implemented behavior with linked evidence and current review; partial implementation is not readiness. Never narrow the original acceptance and mark the partial result `ready`.

Reconcile every live consumer's `blocked_by` edges to the replacements that provide its required capabilities. Superseded records may retain historical edges, but live tickets cannot depend on a superseded ticket. A consumer waits until each required replacement is reviewed `ready` and `available`; splitting does not silently remove dependencies or inherit the original ticket's completion claim. Validate the reconciled graph before resuming assignment.
