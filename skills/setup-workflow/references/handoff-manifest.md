# Compact handoff manifest

Use one `handoff.json` at the exact path allocated by the coordinator for each implementation, review, integration, or whole-feature-verification assignment. The manifest is an index to canonical evidence, not a replacement for reports or logs. Write it atomically after cleanup. Keep paths resolved and exact so the next stage can follow them without guessing conventional filenames.

Use this shape and omit no applicable field:

```json
{
  "schema_version": 1,
  "assignment_id": "run-id:ticket-id:attempt",
  "ticket_id": "T-001",
  "stage": "implementation | review | integration | whole_feature_verification",
  "outcome": "implemented | reviewed | integrated | whole_feature_verified | revision_required | failed | blocked",
  "source_identity": {
    "repository": "/absolute/repository",
    "checkout": "/absolute/checkout",
    "base_revision": "full revision",
    "target_revision": "full revision or null",
    "dirty_content_manifest": "/absolute/path or null"
  },
  "changed_paths": ["repository-relative/path"],
  "affected_contracts": ["ticket criterion, interface, invariant, or rule ID"],
  "prior_finding_ids": ["Q-001"],
  "report_paths": ["/absolute/canonical/report-or-evidence-path"],
  "reusable_evidence": [
    {
      "path": "/absolute/evidence-path",
      "contracts": ["AC-1"],
      "source_identity": "exact target covered",
      "environment": "relevant fixture/dependency identity",
      "validity": "why this evidence can remain applicable"
    }
  ],
  "checks": [
    {
      "command": "exact command or reproducible action",
      "result": "pass | fail | blocked | not_run",
      "evidence_path": "/absolute/path or null",
      "explicit_skips": [{"item": "skipped case or suite", "reason": "why"}]
    }
  ],
  "reviewer_repairs": [
    {
      "finding_id": "Q-001",
      "rule": "explicit repository rule",
      "lease": ["repository-relative/path"],
      "before_source_identity": "exact source before repair",
      "after_source_identity": "exact source after repair",
      "changed_paths": ["repository-relative/path"],
      "correction": "bounded mechanical change",
      "verification": ["check entry or evidence path"]
    }
  ],
  "cleanup": {
    "processes": "stopped | retained | unknown",
    "resources": "released | retained | unknown",
    "details": ["identity, owner, state, and release condition"]
  },
  "blockers": [],
  "next_action": "one exact next action"
}
```

`source_identity` identifies the exact content handed off. A commit target uses its full revision. Dirty work links a content manifest containing the base, included path hashes, deletions, and modes. `report_paths` and evidence paths point to files that exist at handoff. `checks` retains failures, blocked checks, and explicit skips as well as passes. `reviewer_repairs` is empty outside review or when no bounded repair occurred; it never hides the finding that caused the change.

Lifecycle outcomes are cumulative evidence gates, not synonyms. Implementation records `implemented`; independent review records `reviewed`; authorized placement in the agreed consumer base records `integrated`; verification against the combined target records `whole_feature_verified`. Each assignment records only the gate it established. A later gate follows earlier manifest and report paths and rechecks freshness; it never rewrites an earlier outcome.

Non-success outcomes claim no new completion gate: a review requiring fixes records `revision_required`; a confirmed verification or integration failure records `failed`; an unresolved prerequisite or unavailable required check records `blocked`. Link the report that distinguishes defects from blockers. Verification reports map pass to `whole_feature_verified`, fail to `failed`, and blocked to `blocked`; retain additional blocked checks even when the overall result is failed.

After an integration manifest is durable, the coordinator records its path relative to the ticket as `integration_ref`. The dashboard and verifier follow that exact path. `available: true` without an `integration_ref` can still preserve legacy dependency scheduling, but it cannot support an integration claim.

For a revision or re-review, populate `changed_paths`, `affected_contracts`, `prior_finding_ids`, and candidate `reusable_evidence`. Apply the [check-scope policy](check-scope.md). The receiving reviewer independently confirms the recorded evidence identity and explains why the intervening delta leaves its covered contracts valid; a matching filename or an old green result is insufficient.

Each check may include numeric `duration_seconds` when measured by the runner or tool. Omit it when unknown; do not estimate it from token counts or repeat a check just to obtain timing. Existing assignment timestamps and check durations can identify waiting, review returns, and repeated expensive checks without adding a separate tracker.

Keep the manifest compact. Put detailed findings in review reports and verbose output in evidence files. Record no secrets, credentials, raw conversation content, or invented cleanup claims. `unknown` remains unknown until independent process or resource evidence resolves it.
