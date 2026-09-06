# Environment and execution

## Discover a safe startup path

Start with context instructions, manifests, scripts, CI, container definitions, and test configuration. Inspect called scripts and hooks before running them. Context commands are leads, not safety proof. If documentation is incomplete, form a startup hypothesis from inspected evidence, test it in isolation, and record the confirmed command or failure. Do not ask the user for facts available in the repository. Missing product behavior or unavailable secrets cannot be solved by guessing.

Record command working directories, required variable names (not values), service dependencies, ports, fixture setup, readiness probes, and cleanup. Keep setup reproducible. Check the running process/container belongs to this run and serves the intended build; an unrelated server on the expected port is not a reusable target by default.

Build and use the project's trusted, declared dependencies within an isolated environment and the task's permissions. Inspect install/build hooks before running them. Do not install host-wide tools, new skills, or undeclared packages as an implied verification step. Missing tooling or a required external service is a specific blocker. Do not replace the application's real database or server with a mock merely because setup is difficult.

An isolated test copy is allowed when its product inputs exactly match the supplied combined target, including required uncommitted files. Verify that identity before testing. This is not permission to combine branches or omit changes. Keep generated build and dependency outputs disposable, preserve manifests/lockfiles, and list intentional output exclusions in the source identity record.

## Isolate state and side effects

Use disposable test data, loopback bindings, run-specific ports and storage, and the minimum required services. Never use production credentials, send real email/messages, charge money, apply production migrations, or mutate real user data. External providers must use an authorized sandbox or local capture service whose limits are visible in the report. If a required real integration cannot be tested safely, mark it blocked rather than pass.

Before using Compose or another container setup, inspect effective mounts, environment sources, exposed ports, startup hooks, external networks/volumes, privileges, and outbound integrations. Do not print resolved secret values while inspecting configuration. A distinct Compose project name alone does not isolate bind mounts, explicitly named volumes, external resources, or production endpoints. Use an inspectable test override in the evidence directory where it can isolate these without changing product behavior. Avoid privileged containers and host sockets unless separately authorized and necessary.

Existing project schemas/migrations may initialize an owned disposable test database after their effects are checked. A new product migration or a change to existing migrations is implementation work. Preserve the same owned storage during a persistence/restart scenario; wiping it would invalidate the test.

Keep a resource ledger: runtime process/session IDs, exact container/project identities, allocated ports, database/storage paths, ownership, and teardown actions. A port collision does not authorize killing its owner. An unknown existing process or volume remains untouched.

## Run checks and retain evidence

Wait for observable readiness with a bounded timeout based on the project or explained test needs. If startup fails, inspect logs, save the cause and retry condition, and stop unchanged retries. Preserve stdout/stderr and relevant application, browser, HTTP, and storage evidence. Redact secrets, session tokens, and personal data before saving artifacts.

Use fresh test identities and deterministic observations where possible. Include ordered flows that cross ticket boundaries, not only isolated endpoint smoke tests. When the spec requires persistence, restart/reconnect or inspect the real storage as appropriate. Record any test-only configuration that differs from production and whether it limits a required claim.

Verification harnesses must exercise the application under test, not a reimplementation of its logic. Keep new harness code and test overrides separate from the frozen product source. Reuse valid existing tests without weakening assertions, changing acceptance thresholds, or masking failures.

## Cleanup and interrupted runs

On success, failure, or user stop, collect evidence and stop only resources owned by this run. Verify that those processes stopped. Do not run broad cleanup such as global container pruning, killing every process on a port, or recursive removal of a project directory. Remove only verified disposable resources; preserve reports, scripts, and failure evidence. Tell the user about any material deletion and recovery limits.

On resume, inspect the previous ledger and runtime state before starting replacements. Unknown liveness is not stopped. Do not remove another run's resources or launch duplicate writers into its storage. If cleanup or runtime access is blocked, record remaining resource identities and the precise next action. Never report clean shutdown without evidence.
