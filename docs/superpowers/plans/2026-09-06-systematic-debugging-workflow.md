# Systematic Debugging Workflow Implementation Plan

> **For agentic workers:** Implement this plan task-by-task with test-first evidence. Do not expand stage authority while adding the debugging companion.

**Goal:** Add a self-contained systematic debugging skill that review, implementation, verification, and coordination can use at unexplained failure boundaries.

**Architecture:** `systematic-debugging` is the collection's sole model-invoked companion. Its canonical reference defines the diagnostic loop, classifications, stage modes, record shape, and escalation rule. Existing explicit stage skills link to that contract and preserve their current write permissions and lifecycle ownership.

**Tech Stack:** Agent Skills Markdown, Codex `agents/openai.yaml`, Python `unittest` contract tests.

**Spec:** `docs/superpowers/specs/2026-09-06-systematic-debugging-workflow-design.md`

## Global constraints

- Keep every user-facing stage skill explicit-only.
- Debugging invocation does not expand the calling stage's authority.
- Reviewers and verifiers diagnose without editing product source or permanent tests.
- Implementers use the existing `tdd` companion for confirmed product corrections.
- Three unsuccessful root-cause corrections route to the coordinator for architectural reconsideration.
- Preserve the user's existing untracked `docs/observations/` files.
- Do not commit, push, publish, or install skills as part of this change.

---

### Task 1: Define the debugging contract with failing tests

**Files:**

- Create: `tests/test_systematic_debugging_guidance.py`
- Modify: `tests/test_skill_suite_integrity.py`

**Interfaces:**

- Consumes: existing skill layout and explicit-only metadata policy.
- Produces: executable invariants for the one implicit companion, consumer-stage links, read-only diagnosis, classification routing, and repeated-correction escalation.

- [x] Add an integrity exception map whose only member is `systematic-debugging`, with expected `disable-model-invocation` and `allow_implicit_invocation` values.
- [x] Add focused tests that resolve the canonical diagnostic reference from each consumer and assert reviewer/verifier write boundaries remain intact.
- [x] Add tests for all six classifications, explicit next-owner routing, and the three-unsuccessful-corrections escalation.
- [x] Run `python3 -m unittest tests.test_systematic_debugging_guidance tests.test_skill_suite_integrity -v` and confirm it fails because the skill and links do not exist.

### Task 2: Add the local systematic debugging companion

**Files:**

- Create: `skills/systematic-debugging/SKILL.md`
- Create: `skills/systematic-debugging/agents/openai.yaml`
- Create: `skills/systematic-debugging/references/diagnostic-method.md`

**Interfaces:**

- Consumes: a symptom, target identity, calling stage, permitted evidence paths, and existing caller authority.
- Produces: a diagnosis record with reproduction, evidence, tested hypothesis, classification, affected contract, cleanup state, and routed next action.

- [x] Write the compact trigger-only entrypoint and keep detailed techniques in `diagnostic-method.md`.
- [x] Define diagnosis-only and implementation modes without granting authority.
- [x] Define the evidence loop, six classifications, record fields, next-owner table, and three-correction escalation.
- [x] Add MIT attribution to Superpowers v6.3.0 while keeping the installed plugin optional.
- [x] Add Codex metadata with `allow_implicit_invocation: true` and no explicit-only frontmatter flag.
- [x] Run the focused tests and correct only failures attributable to this task.

### Task 3: Connect failure paths without creating a reviewer repair loop

**Files:**

- Modify: `skills/review-ticket/SKILL.md`
- Modify: `skills/review-ticket/references/reviewer-briefs.md`
- Modify: `skills/review-ticket/references/review-record.md`
- Modify: `skills/implement-ticket/SKILL.md`
- Modify: `skills/verify-feature/SKILL.md`
- Modify: `skills/coordinate-work/SKILL.md`
- Modify: `skills/coordinate-work/references/run-state.md`

**Interfaces:**

- Consumes: the canonical debugging companion and existing stage authority.
- Produces: conditional invocation at unexplained failures, structured diagnosis handoffs, TDD corrections, and coordinator-owned routing.

- [x] Require reviewers to invoke the debugging companion for unexplained failing checks or unexpected behavior, while letting demonstrated static findings remain direct findings.
- [x] Keep diagnosis-only writes in external review evidence or scratch; preserve the separate parent-leased mechanical reviewer-repair exception.
- [x] Require implementation-mode diagnosis before speculative correction and route the third unsuccessful correction to architecture review.
- [x] Let verifiers correct only their owned disposable harness and return confirmed product defects to coordination.
- [x] Make the coordinator classify and route diagnosis outcomes instead of repeating an unchanged implementation/review loop.
- [x] Run the focused tests and then the complete deterministic suite.

### Task 4: Document and pressure-test discovery behavior

**Files:**

- Create: `evals/systematic-debugging/reviewer-ambiguous-failure.md`
- Create: `evals/systematic-debugging/reviewer-static-finding-control.md`
- Create: `evals/systematic-debugging/README.md`
- Create: `evals/systematic-debugging/fixtures/retry-budget/retry_budget.py`
- Create: `evals/systematic-debugging/fixtures/retry-budget/test_retry_budget.py`
- Modify: `README.md`

**Interfaces:**

- Consumes: a fresh review agent and the isolated retry-budget fixture copied by the evaluator.
- Produces: recorded RED/GREEN outcomes scored for invocation, evidence, classification, read-only behavior, routing, and unnecessary invocation.

- [x] Add one ambiguous-failure pressure scenario and one static-finding control with observable pass/fail criteria.
- [x] Document required result metadata: model, prompt, fixture revision, repetitions, raw result location, and scorer decision.
- [x] State that these are model-behavior evaluations, not deterministic unit tests, and that no GREEN claim is allowed until they are run with a permitted fresh agent.
- [x] Update the root README inventory, installation command, implicit-companion exception, stage integration, and attribution.
- [x] Run the skill validator, link checks, focused tests, and full suite; inspect `git diff --check` and final status.
