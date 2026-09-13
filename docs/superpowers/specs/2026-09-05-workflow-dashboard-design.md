# Workflow dashboard and context-aware delegation design

## Purpose

Give the user a live, read-only view of a coordinated ticket run without using another model to summarize it. Show ticket progress, agent activity, exact available token telemetry, context pressure, blockers, and next actions. Permit one ticket owner to use focused child agents when independent work can safely proceed in parallel.

## Chosen approach

Add a standalone application under `apps/workflow-dashboard`, outside every skill package. A stable `workflow-dashboard` command exposes progress, snapshot, and serve operations. Its long-lived Bun TypeScript server listens on `127.0.0.1`, serves the colocated HTML asset, and returns the last completed snapshot immediately. It schedules a persistent Python telemetry worker every 30 seconds; refreshes never overlap, and the worker retains an incremental JSONL cache. `thin-coordinator` contains only the discovery and usage contract. This separates skill installation, coordinator logic, HTTP service, and potentially slow telemetry scan without adding a database, external service, or monitoring agent.

The page is a projection. Ticket files remain authoritative for ticket lifecycle, and `RUN.md` remains authoritative for coordination policy and history. Per-agent progress records provide a small machine-readable join between those artifacts and runtime telemetry. The page cannot mutate workflow state or stop an agent.

## Dashboard contents

The first viewport shows:

- Run mode, last refresh, active agents, runtime capacity, tickets ready, tickets active, and tickets blocked.
- Pipeline completion, calculated from recorded lifecycle gates and labeled as pipeline progress rather than remaining-effort prediction.
- One compact row per ticket with its phase, completion state, review-return count, and current owner's context.
- A compact agent section immediately below the tickets with human role names and current context. Runtime paths and historical agents remain outside the page.
- An agent tree showing the coordinator, ticket owners, delegated children, and reviewers.
- Exact cumulative token use and latest model-call input for every mapped Codex session.

The page uses plain labels and restrained status colors. It includes no controls, decorative imagery, animation, invented ETA, or generated prose.

## Context telemetry

Codex session JSONL files contain `session_meta` and `event_msg` records. The dashboard reads only identifiers, agent ancestry, timestamps, model identity when available, and `token_count` values. It never reads or serves prompts, messages, tool arguments, tool output, or authentication data.

For each session, show these separate values:

- Cumulative input, output, reasoning-output, and total tokens. Cached input remains internal for counter validation.
- Latest-call input tokens.
- Model context window.
- Latest-call context occupancy: latest input divided by the model context window.

The smart-context indicator applies to latest-call input, not cumulative use, and scales with the runtime-reported model context window:

- Below 80% occupancy: normal.
- At or above 80% occupancy: warning; save a compact checkpoint at the next meaningful boundary.
- At or above 95% occupancy: critical advisory; let the runtime compact and finish a nearly complete bounded step when that is safer.

Context pressure is telemetry, not a workflow stop. The coordinator does not ask for approval, stop, or replace an agent solely because of a token number. Cumulative usage remains visible as a cost/churn signal. When exact telemetry or the context window cannot be joined, show `Not reported`; never estimate tokens.

## Progress records

Each runtime owns one JSON record under `<workflow>/progress/`. A deterministic helper writes records atomically. Required fields are schema version, agent path, parent agent path, ticket ID when applicable, role, stage, state, summary, started time, updated time, and next action. Optional fields include runtime session ID, blockers, file leases, and reserved test resources.

Workers update the record only at meaningful milestones: assignment accepted, code located, failing test observed, implementation underway, checks running, blocked, checkpointed, or handoff complete. Repeated unchanged heartbeats are unnecessary. The records do not replace the ticket implementation record or `RUN.md` event history.

Health is evidence-based:

- `Blocked` only when a blocker is recorded.
- `Context critical` or `Context warning` only from exact telemetry.
- `Check recommended` when the configured inactivity interval passes without a progress update; this does not claim that the worker failed or stopped.
- `On track` when no warning condition exists.

## Intra-ticket delegation

One implementer remains the ticket owner and the only writer of ticket lifecycle fields and the final implementation record. The coordinator records a child-agent allowance based on runtime capacity and resource isolation. A child cannot spawn another child.

The owner may delegate when work packages are independent at an observable behavior or contract boundary. Different filenames alone do not prove independence. Before dispatch, the owner records:

- Child ID, goal, and expected handoff.
- Exact file lease with no overlap.
- Interface or contract the child must preserve.
- Isolated mutable test and output resources.
- Parent/child relationship and runtime slot reservation.

Children may share the owner's checkout only as a registered delegation group. Each writer edits only leased paths. Children do not change Git state, ticket files, `RUN.md`, dependencies, shared schemas, or repository-wide generated output. The parent does not edit a child's leased paths until that child stops. Checks that share mutable resources run sequentially. Any discovered overlap stops affected writes until the owner reschedules the work.

Each child applies TDD within its assigned behavior boundary and returns its red/green evidence. After all children stop, the owner inspects and integrates their work, runs cross-boundary and full required checks, and writes the single ticket handoff. Review starts only after every member of the delegation group and its mutating processes has stopped.

Delegation should happen early. Under rising context pressure, checkpoint at a meaningful boundary and let the runtime manage compaction. Finish a nearly complete bounded step when safer. Use a coordinator-managed fresh-context continuation only when the runtime cannot continue reliably; preserve ownership and evidence without treating a token number as a lifecycle event.

## Server lifecycle and portability

The coordinator resolves the separately installed `workflow-dashboard` executable from `PATH` and starts it only for an active local run when local process retention is available. It never installs or copies the application during coordination. It binds to `127.0.0.1`, chooses an available port by default, records the executable, URL, and Bun process identity in `RUN.md`, and gives the user the URL. The Bun process owns and stops its Python worker. The browser polls a read-only JSON endpoint that performs no telemetry I/O. Pause and completion leave a final static snapshot; the coordinator stops only the server process it owns. If the executable is unavailable, coordination continues without the optional projection. A live legacy server retains its old installed files until its verified owner stops both processes; only then may the skill installation be replaced and an active run restarted through the standalone command.

Non-Codex runtimes still receive ticket and progress views. Their token fields state that telemetry is unavailable. Codex log locations are configurable, and missing or malformed files degrade one agent's telemetry instead of breaking the page.

## Verification

Use standard-library unit tests with temporary workflow and session directories plus Bun server process tests. Cover ticket parsing, progress-record validation and atomic replacement, incremental session discovery, latest token selection, agent ancestry, token rollups, pipeline progress, warning boundaries, precise malformed/missing states, non-overlapping refreshes, current asset reloads, and immediate HTTP responses. Verify the HTML contains the required accessible labels and renders useful empty, unavailable-telemetry, integration-pending, active, blocked, warning, and completed states.

Run the existing ticket-validator tests, the new dashboard tests, skill validation, and a localhost smoke test. Do not require network access or install dependencies.

## Success criteria

- One command starts a readable local dashboard for an active workflow.
- Installing `thin-coordinator` copies no server, HTML, telemetry worker, or dashboard tests.
- Refreshing the page consumes no model tokens.
- Exact available telemetry is shown without reading conversation content.
- Latest-call context and cumulative usage are visually and semantically distinct.
- Context signals are deterministic percentages of the runtime-reported window and never force a workflow stop.
- Ticket ownership remains singular when child agents are used.
- Child writes, resources, liveness, and usage are visible and recoverable.
- The coordinator can checkpoint, compact in place, and continue with the same ownership and active workers.
- The implementation adds no third-party runtime or frontend dependency.
