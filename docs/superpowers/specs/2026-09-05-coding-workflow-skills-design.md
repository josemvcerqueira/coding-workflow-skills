# Coding Workflow Skills repository design

## Purpose

Create a personal, public-ready collection of reusable coding workflow skills. The repository will support the Agent Skills specification, installation through the skills.sh CLI, and use by both Claude Code and Codex/GPT coding agents.

## Repository

- Name: `coding-workflow-skills`
- VPS location: `/home/ubuntu/coding-workflow-skills`
- Default branch: `main`
- License: MIT
- Git author: reuse the existing VPS identity `josemvcerqueira <41003724+josemvcerqueira@users.noreply.github.com>` as repository-local configuration

The VPS repository is the working copy. A GitHub remote can be added later under the same repository name so skills.sh can install and index the collection.

## Initial structure

```text
coding-workflow-skills/
|-- README.md
|-- LICENSE
|-- skills/
|   `-- .gitkeep
|-- docs/
|   `-- superpowers/
|       `-- specs/
|           `-- 2026-09-05-coding-workflow-skills-design.md
`-- .gitignore
```

No placeholder `SKILL.md` files will be created. Each skill will be added only after its behavior and activation conditions have been defined.

## Skill structure

Each finished skill will live at `skills/<skill-name>/SKILL.md`. Its folder name and frontmatter `name` will match and use lowercase letters, numbers, and hyphens. The `description` will state the capability and concrete activation conditions.

Optional resources will be added only when they serve the skill:

```text
skills/<skill-name>/
|-- SKILL.md
|-- scripts/       # deterministic reusable helpers
|-- references/    # detailed guidance loaded on demand
`-- assets/        # templates or files used in outputs
```

The main `SKILL.md` will stay concise and route to supporting resources through relative links.

## Planned workflow family

The likely first skills are:

- `shaping-tickets`: turn an approved ticket or request into an implementation-ready specification.
- `implementing-tickets`: execute an approved implementation plan with appropriate tests and verification.
- `reviewing-code`: review completed changes for requirements, correctness, maintainability, and risk.
- A possible orchestration skill will connect the stages only after the individual skills have been tested in real use.

These names and boundaries remain proposals; creating the repository does not commit us to them.

## Distribution

Once the repository is mirrored to GitHub, users will be able to inspect and install skills with commands such as:

```bash
npx skills add josemvcerqueira/coding-workflow-skills --list
npx skills add josemvcerqueira/coding-workflow-skills -g -a claude-code -a codex
```

A root `skills.sh.json` will be added when the first real skills exist. It will group related skills for skills.sh without introducing empty or misleading entries.

## Validation

Every skill will be checked against the Agent Skills naming and frontmatter requirements. Before publication, the repository will also be tested with the skills.sh CLI by listing the available skills and installing them into isolated Claude Code and Codex test locations.

## Failure handling

- A missing or malformed skill stops publication until validation passes.
- Tool-specific instructions belong in conditional references instead of making the core workflow depend on one agent.
- Commands that change external systems require the authorization appropriate to that action; installing a workflow skill does not grant deployment, merge, or messaging authority.
- The GitHub remote and skills.sh listing are intentionally deferred until the repository owner chooses to publish.

## Success criteria

- The repository exists on the OVH VPS on branch `main`.
- Its structure makes the portable `skills/<name>/SKILL.md` convention explicit.
- It contains no fake or incomplete skills.
- Documentation explains how Claude Code and Codex users will install the future collection.
- The initial commit is clean and reproducible before skill authoring begins.
