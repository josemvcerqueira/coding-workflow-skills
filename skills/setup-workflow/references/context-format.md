# Context document contract

Keep the established external context structure. Include the following information where it applies. Record PROJECT.md and the exact product source root. Use relative document links resolved from this context file, or verified absolute host paths when appropriate. State the project root used for scope patterns and command working directories. An installed skill outside the repository can use an exact local path, but label it machine-local and not portable. A source URL is provenance, not proof of local installation.

## Project facts and navigation

Record purpose if known, key source directories, language/framework versions with manifest evidence, architecture/decision links, and important constraints. In a monorepo, identify each relevant package's scope and link deeper context; do not load every package's skills into every task. Keep current facts separate from proposed technology choices. Do not infer business goals from a directory name.

## Commands

For each discovered useful command, record:

- Exact command and working directory.
- Purpose and source definition.
- Required tools, test resources, and service or external side effects.
- Evidence status: inspected, not run; or a pointer to actual prior execution evidence with its limits.

Separate implementation-safe checks from checks that start an application or require live services. Missing commands remain unknown. A familiar command name is not evidence of safe behavior or successful tests. Do not claim existing evidence is fresh without checking its target.

For later feature verification, include discovered startup/build sources, readiness probes, test configuration variable names, service/storage requirements, and owned-resource cleanup commands. Identify production-bound defaults or shared resources that need isolation. Inspect these sources only during setup; the verifier checks their current safety and executes them later. Put feature-specific scenarios and expected behavior in the engineering spec, not in this project map.

## Selected coding standards

Each mapping identifies the skill, its actual location, affected files or subsystem, relevant workflow stages, and whether the project requires it. Include the basis for selection, availability, version compatibility, and inspected source/revision when known. Preserve existing mappings that lack these extra fields; add only supported facts.

Illustrative shape, not a skill that this collection supplies:

```markdown
## Coding standards

Scope patterns are relative to the project root. Relative links resolve from this file. Absolute skill paths identify installed files on this host.

- Go service standards:
  - Skill: /absolute/product/path/.agents/skills/go-standards/SKILL.md
  - Applies to: services/**/*.go
  - Used by: implementation and review
  - Required: yes
  - Selected by: existing project instructions
  - Availability: present
  - Compatibility: verified against the project's declared Go version
```

The absolute skill path above is illustrative, not an installed skill. In an external context file, a repository-relative-looking path would resolve to the wrong root. Replace example values only with evidence. Never insert this example as an active mapping merely to fill a section. Use the same selected standards for implementation and review unless the project explicitly scopes an entry to one stage. A selected optional skill is guidance, not an independent mandatory acceptance gate.

## Recommendations and gaps

List unselected candidates separately, with reason, source, applicability, conflicts, and installation status. Recommendations do not become active mappings until selected by the user or established project policy. If no suitable candidate or catalog exists, state that and point to relevant project rules or verified official documentation. Missing optional guidance does not block the whole workflow. Missing required guidance needs a stated impact and resolution path, not a fabricated pass.

Record unresolved facts and decisions with the next action. Do not turn every missing tool into a question or block writing the rest of the context. A setup document can be saved while required guidance is unavailable; that does not mean the project is ready for affected implementation or review.
