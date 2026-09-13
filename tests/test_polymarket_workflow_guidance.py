"""Regression invariants learned from the Polymarket coordination run."""

import unittest
from pathlib import Path


SKILLS = Path(__file__).resolve().parents[1] / "skills"


def read(relative):
    return (SKILLS / relative).read_text(encoding="utf-8").lower()


class PolymarketWorkflowGuidanceTests(unittest.TestCase):
    def test_blocking_quality_findings_require_contract_or_maintenance_evidence(self):
        briefs = read("review-ticket/references/reviewer-briefs.md")
        record = read("review-ticket/references/review-record.md")

        self.assertIn("complexity scores are advisory", briefs)
        self.assertIn("violated contract", briefs)
        self.assertIn("demonstrated maintenance cost", briefs)
        self.assertIn("page-permit ownership", briefs)
        self.assertIn("violated contract or demonstrated maintenance cost", record)

    def test_rereview_contract_is_delta_focused_and_preserves_independence(self):
        review = read("review-ticket/SKILL.md")
        record = read("review-ticket/references/review-record.md")
        scheduling = read("thin-coordinator/references/scheduling.md")
        combined = "\n".join((review, record, scheduling))

        for required in ("changed paths", "prior finding ids", "affected contracts", "reusable evidence"):
            self.assertIn(required, combined)
        self.assertIn("concrete reason", combined)
        self.assertIn("independently validates", combined)

    def test_expensive_test_capacity_and_concurrent_failures_are_preserved(self):
        implementation = read("implement-ticket/SKILL.md")
        briefs = read("review-ticket/references/reviewer-briefs.md")
        scheduling = read("thin-coordinator/references/scheduling.md")
        combined = "\n".join((implementation, briefs, scheduling))

        self.assertIn("test-suite capacity", scheduling)
        self.assertIn("broad race", combined)
        self.assertIn("original concurrent conditions", combined)
        self.assertIn("serial pass", combined)
        self.assertIn("does not erase", combined)

    def test_all_three_stages_use_the_shared_handoff_manifest(self):
        manifest = read("setup-workflow/references/handoff-manifest.md")
        for skill in ("implement-ticket/SKILL.md", "review-ticket/SKILL.md", "thin-coordinator/SKILL.md"):
            self.assertIn("handoff manifest", read(skill))
        for field in (
            "source_identity", "report_paths", "changed_paths", "affected_contracts",
            "prior_finding_ids", "checks", "explicit_skips", "cleanup", "next_action",
        ):
            self.assertIn(field, manifest)
        self.assertIn("follow the manifest's recorded paths", read("thin-coordinator/SKILL.md"))

    def test_lifecycle_gates_and_context_measures_remain_distinct(self):
        dashboard = read("thin-coordinator/references/dashboard.md")
        run_state = read("thin-coordinator/references/run-state.md")
        combined = dashboard + "\n" + run_state

        for gate in ("implemented", "reviewed", "integrated", "whole-feature verified"):
            self.assertIn(gate, combined)
        self.assertIn("exact current context", combined)
        self.assertIn("cumulative token usage", combined)
        self.assertIn("verification and cleanup", combined)

    def test_small_review_findings_use_a_bounded_reviewer_repair_path(self):
        implementation = read("implement-ticket/SKILL.md")
        review = read("review-ticket/SKILL.md")
        record = read("review-ticket/references/review-record.md")
        briefs = read("review-ticket/references/reviewer-briefs.md")
        repair = read("review-ticket/references/reviewer-repair.md")
        coordination = read("thin-coordinator/SKILL.md")
        manifest = read("setup-workflow/references/handoff-manifest.md")
        ticket_format = read("spec-to-tickets/references/ticket-format.md")
        combined = "\n".join((review, record, briefs, repair, coordination, ticket_format))

        self.assertIn("new or changed test names", implementation)
        self.assertIn("fixture labels", implementation)
        self.assertIn("repository naming rules", implementation)
        self.assertIn("reviewer repair", combined)
        self.assertIn("explicit and unambiguous", combined)
        self.assertIn("does not change production behavior", combined)
        self.assertIn("does not delete or weaken a test", combined)
        self.assertIn("smallest meaningful", combined)
        self.assertIn("severity alone", combined)
        self.assertIn("no second reviewer", combined)
        self.assertIn("outside the bounded reviewer repair", review)
        self.assertIn("bounded reviewer repair", ticket_format)
        self.assertIn("reviewer_repairs", manifest)

    def test_dashboard_and_handoffs_use_exact_lifecycle_and_report_evidence(self):
        implementation = read("implement-ticket/SKILL.md")
        review = read("review-ticket/SKILL.md")
        coordination = read("thin-coordinator/SKILL.md")
        dashboard = read("thin-coordinator/references/dashboard.md")
        run_state = read("thin-coordinator/references/run-state.md")
        ticket_format = read("spec-to-tickets/references/ticket-format.md")
        combined = "\n".join((implementation, review, coordination, dashboard, run_state, ticket_format))

        self.assertIn("integration_ref", combined)
        self.assertIn("availability alone", combined)
        self.assertIn("handoff_path", dashboard)
        self.assertIn("executive snapshot", dashboard)
        self.assertIn("every ticket's title, phase", dashboard)
        self.assertIn("number of review returns", dashboard)
        self.assertIn("human role labels", dashboard)
        self.assertIn("terminal coordinator progress record governs", dashboard)
        self.assertIn("keep summaries, next actions", dashboard)

    def test_live_instruction_changes_require_acknowledged_delivery(self):
        coordination = read("thin-coordinator/SKILL.md")
        run_state = read("thin-coordinator/references/run-state.md")

        self.assertIn("live instruction delivery", coordination)
        for required in (
            "actual session or control channel",
            "instruction revision",
            "worker acknowledgment",
            "inbox file is not proof",
            "do not dispatch duplicate work",
        ):
            self.assertIn(required, run_state)

    def test_reviewer_setup_recovery_has_a_handoff_boundary(self):
        review = read("review-ticket/SKILL.md")
        record = read("review-ticket/references/review-record.md")
        checks = read("setup-workflow/references/check-scope.md")

        self.assertIn("setup-recovery boundary", review)
        self.assertIn("bounded setup recovery", record)
        for required in (
            "second failed setup attempt",
            "explicit coordinator checkpoint",
            "candidate identity",
            "outstanding acceptance checks",
            "verification explicitly `blocked`",
            "responsible harness owner",
            "healthy in-flight command",
        ):
            self.assertIn(required, checks)

    def test_scheduling_depends_on_concrete_needs_and_separates_adoption(self):
        coordination = read("thin-coordinator/SKILL.md")
        scheduling = read("thin-coordinator/references/scheduling.md")

        self.assertIn("dependency-based scheduling", coordination)
        for required in (
            "source, artifact, resource, or acceptance dependency",
            "active reviewer does not automatically block",
            "independent tooling development",
            "adopting that tooling",
            "acknowledged safe boundary",
            "single-writer",
            "expensive test-lane",
        ):
            self.assertIn(required, scheduling)


if __name__ == "__main__":
    unittest.main()
