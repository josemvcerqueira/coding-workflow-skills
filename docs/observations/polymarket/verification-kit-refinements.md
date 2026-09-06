# Refinements for the owning Rollify coordinator

The reusable Zappx verification kit design and wrapper-level location are approved. Incorporate these refinements into its design specification and implementation plan. Keep ownership in this task and preserve the active Polymarket objective.

1. **Make profile selection evidence-based.** Map each ticket's changed contracts and acceptance criteria to named scenarios. `smoke` must prove the real list/event/market path; `affected` adds relevant regression scenarios. Each assignment records its profile, scenarios, why they are sufficient, and any deferred checks with a named later owner. A smaller profile cannot silently omit a mandatory project or ticket gate.

2. **Use full verification at the final combined source, with earlier escalation when needed.** The default is one full integrated run at the end, not one per ticket. Publication/follower changes, migrations, concurrency, limits, or uncertain cross-service impact can justify an earlier full run. Record the reason. Fixing a failure still requires rerunning failed and affected scenarios; “once” is not a cap that waives revalidation or the pre-push gate.

3. **Make reuse reproducible.** A backend image must match the exact candidate commit plus relevant build arguments/configuration, dependency locks, toolchain and immutable base-image identities. Key prepared database snapshots by dataset/schema digests, preparation logic and compatible database version/extensions. Keep snapshots immutable and give every run fresh writable PostgreSQL and Redis state. Retain only explicitly owned immutable caches/artifacts; automatically clean mutable processes, data and networks. Record the identities actually tested.

4. **Deliver the smallest usable kit first.** After the active T-002 behavior review's completed handoff and cleanup, extract and parameterize its completed harness. Keep scenarios reusable and add a simple Compose/command entry point; do not build another orchestration framework or rewrite working probes without a concrete need. Establish repeatable startup, smoke evidence and cleanup first, then connect affected/full scenario selection. Reuse the supported application topology rather than dropping services the application needs.

Keep executable tooling outside the product repository in the wrapper. Update the project-local zappx-joined-local-stack skill and external Zappx CONTEXT.md with exact commands. Pin the tested kit path/version/digest in workflow RUN.md and future assignments. No project-specific edits to generic skills under /home/ubuntu/coding-workflow-skills.

Do not interrupt, restart, or alter the current T-002 reviewer or its evidence. Before adopting the kit for correction review or a later ticket, finish the current handoff, validate the kit, reconcile resource ownership, and record the effective assignment. If the kit is not ready, do not report an unexecuted required check as passed.

Record setup, build, time-to-first-acceptance-check, scenario and cleanup durations separately. Compare subsequent runs with the one-off T-002 setup, accounting for different scope and warm caches. Success means reviewers use established commands and evaluate behavior, while independent review, complete criterion coverage and verified cleanup remain intact.
