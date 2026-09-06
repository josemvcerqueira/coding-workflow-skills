---
name: systematic-debugging
description: Use when a test, build, runtime path, integration, or performance check fails unexpectedly, behaves inconsistently, or remains broken after a correction and the root cause is not established.
license: MIT
---

# Systematic debugging

Find the root cause before proposing or applying a correction. A plausible explanation is a hypothesis, not evidence.

## Preserve the caller's authority

Read the [diagnostic method](references/diagnostic-method.md). The calling stage selects the mode and supplies the target, evidence location, permitted checks, and resource limits. This skill does not create a workflow, change lifecycle state, or expand those permissions.

- **Diagnosis-only mode:** Reviewers and feature verifiers investigate and report. They do not edit product source or permanent tests. They may write only assigned evidence, scratch reproductions, and owned disposable harness artifacts.
- **Implementation mode:** An assigned implementer may correct a confirmed product cause inside the existing lease. Follow the caller's TDD companion: observe a failing regression test before the correction, then run focused and affected checks.

## Use the evidence loop

1. Pin the failing target, command or action, environment, and exact symptom.
2. Reproduce it, or record why reproduction is unsafe or unavailable.
3. Inspect relevant changes and trace the bad value, state, or control flow backward across boundaries.
4. Compare the failing path with a working path when one exists.
5. State one falsifiable root-cause hypothesis.
6. Run the smallest permitted experiment that distinguishes it from alternatives.
7. Record the result before forming another hypothesis or proposing a correction.

Do not retry unchanged conditions, bundle several speculative fixes, or report a suspected bug as confirmed. Skip this workflow when direct evidence already proves a straightforward static finding.

## Return a diagnosis

Record the reproduction, observations, tested hypotheses, root cause or remaining uncertainty, classification, affected contract, recommended next owner, and cleanup state. Keep the calling stage's verdict separate from the diagnosis.

In implementation mode, record materially different correction attempts. After three unsuccessful root-cause corrections for the same symptom, stop editing and return the evidence to coordination for architectural reconsideration or contract clarification.
