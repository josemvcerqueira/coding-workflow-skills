# Workflow dashboard and context-aware delegation design

## Purpose

Give the user a live, read-only view of a coordinated ticket run without using another model to summarize it. Show ticket progress, agent activity, exact available token telemetry, context pressure, blockers, and next actions. Permit one ticket owner to use focused child agents when independent work can safely proceed in parallel.

## Chosen approach

Add a small local dashboard to `coordinate-work`. A Python standard-library process reads workflow records and Codex session telemetry, then serves a single HTML/CSS/JavaScript page on `127.0.0.1`. Python is the data and HTTP layer only; the browser interface is JavaScript. This reuses the repository's existing Python requirement and adds no package manager, build step, database, external service, or monitoring agent.

The page is a projection. Ticket files remain authoritative for ticket lifecycle, and `RUN.md` remains authoritative for coordination policy and history. Per-agent progress records provide a small machine-readable join between those artifacts and runtime telemetry. The page cannot mutate workflow state or stop an agent.

## Dashboard contents

The first viewport shows:

- Run mode, last refresh, active agents, runtime capacity, tickets ready, tickets active, and tickets blocked.
- Pipeline completion, calculated from recorded lifecycle gates and labeled as pipeline progress rather than remaining-effort prediction.
- One card per active ticket with its owner, stage, current milestone, elapsed time, last progress time, blocker summary, next action, and health.
- An agent tree showing the coordinator, ticket owners, delegated children, and reviewers.
- Exact cumulative token use and latest model-call input for every mapped Codex session.

The page uses plain labels and restrained status colors. It includes no controls, decorative imagery, animation, invented ETA, or generated prose.

## Context telemetry

Codex session JSONL files contain `session_meta` and `event_msg` records. The dashboard reads only identifiers, agent ancestry, timestamps, model identity when available, and `token_count` values. It never reads or serves prompts, messages, tool arguments, tool output, or authentication data.

For each session, show these separate values:

- Cumulative input, cached-input, output, reasoning-output, and total tokens.
- Latest-call input tokens.
- Model context window.
- Latest-call context occupancy: latest input divided by the model context window.

The smart-context guardrail applies to latest-call input, not cumulative use:

- Below 160,000: normal.
- 160,000 through 199,999: warning; prepare a checkpoint or split.
- 200,000 or above: critical; checkpoint and hand off to a fresh context before more broad work.

The 200,000 boundary is a workflow policy, not a claim about a model's technical maximum. Cumulative usage may exceed 200,000 without context pressure and remains visible as a cost/churn signal. When exact telemetry cannot be joined, show `Not reported`; never estimate tokens.

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

Delegation should happen early. At the 160,000 warning, the owner checkpoints and asks the coordinator to preserve or adjust its child allowance. At 200,000, the coordinator requests a checkpoint and fresh-context continuation. Spawning children after the owner is already context-critical is not a substitute for that handoff.

## Server lifecycle and portability

The coordinator starts the dashboard only for an active local run when Python and local process retention are available. It binds to `127.0.0.1`, chooses an available port by default, records the URL and process identity in `RUN.md`, and gives the user the URL. The browser polls a read-only JSON endpoint. Pause and completion leave a final static snapshot; the coordinator stops only the server process it owns.

Non-Codex runtimes still receive ticket and progress views. Their token fields state that telemetry is unavailable. Codex log locations are configurable, and missing or malformed files degrade one agent's telemetry instead of breaking the page.

## Verification

Use standard-library unit tests with temporary workflow and session directories. Cover ticket parsing, progress-record validation and atomic replacement, session discovery, latest token selection, agent ancestry, token rollups, pipeline progress, warning boundaries, malformed/missing data, and HTTP responses. Verify the HTML contains the required accessible labels and renders useful empty, unavailable-telemetry, active, blocked, warning, and completed states.

Run the existing ticket-validator tests, the new dashboard tests, skill validation, and a localhost smoke test. Do not require network access or install dependencies.

## Success criteria

- One command starts a readable local dashboard for an active workflow.
- Refreshing the page consumes no model tokens.
- Exact available telemetry is shown without reading conversation content.
- Latest-call context and cumulative usage are visually and semantically distinct.
- The 160,000 and 200,000 smart-context signals are deterministic.
- Ticket ownership remains singular when child agents are used.
- Child writes, resources, liveness, and usage are visible and recoverable.
- The coordinator can checkpoint and continue oversized work in a fresh context.
- The implementation adds no third-party runtime or frontend dependency.
