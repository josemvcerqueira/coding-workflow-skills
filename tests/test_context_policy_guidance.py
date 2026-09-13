"""Keep coordinator context-pressure guidance aligned across its documents."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CoordinatorContextPolicyGuidanceTests(unittest.TestCase):
    def test_context_telemetry_never_creates_a_workflow_stop(self):
        dashboard = (ROOT / "skills/thin-coordinator/references/dashboard.md").read_text(encoding="utf-8")
        run_state = (ROOT / "skills/thin-coordinator/references/run-state.md").read_text(encoding="utf-8")
        entrypoint = (ROOT / "skills/thin-coordinator/SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        design = (ROOT / "docs/superpowers/specs/2026-09-05-workflow-dashboard-design.md").read_text(encoding="utf-8")
        plan = (ROOT / "docs/superpowers/plans/2026-09-05-workflow-dashboard.md").read_text(encoding="utf-8")

        for document in (dashboard, run_state, entrypoint, readme, design, plan):
            normalized = document.lower().replace("-", " ")
            self.assertNotIn("200,000", normalized)
            self.assertNotIn("200k", normalized)
            self.assertIn("runtime", normalized)

        combined = "\n".join((dashboard, run_state, entrypoint)).lower().replace("-", " ")
        self.assertIn("same coordinator", combined)
        self.assertIn("never stop", combined)
        self.assertIn("solely", combined)

    def test_run_request_grants_standing_local_execution_authority(self):
        entrypoint = (ROOT / "skills/thin-coordinator/SKILL.md").read_text(encoding="utf-8").lower()
        run_state = (ROOT / "skills/thin-coordinator/references/run-state.md").read_text(encoding="utf-8").lower()
        scheduling = (ROOT / "skills/thin-coordinator/references/scheduling.md").read_text(encoding="utf-8").lower()
        agent_prompt = (ROOT / "skills/thin-coordinator/agents/openai.yaml").read_text(encoding="utf-8").lower()

        combined = "\n".join((entrypoint, run_state, scheduling, agent_prompt))
        self.assertIn("standing local execution authority", combined)
        self.assertIn("do not ask", combined)
        self.assertIn("local commits", combined)
        self.assertIn("selected local consumer", combined)
        self.assertNotIn("default: no such authority", combined)
        self.assertNotIn("without committing, merging, or deploying", combined)

    def test_ticket_workers_use_adaptive_context_handoffs(self):
        implementer = (ROOT / "skills/implement-ticket/SKILL.md").read_text(encoding="utf-8").lower()
        delegation = (ROOT / "skills/implement-ticket/references/delegation.md").read_text(encoding="utf-8").lower()

        combined = "\n".join((implementer, delegation))
        self.assertNotIn("at 200k or above, stop broad work", combined)
        self.assertNotIn("at 200,000 or above, stop broad work", combined)
        self.assertIn("finish the bounded step", combined)
        self.assertIn("runtime manage compaction", combined)
        self.assertIn("fresh context", combined)
        self.assertIn("coordinator-authorized local commit", combined)
        self.assertIn("no additional user approval", combined)
        self.assertIn("targeted searches and bounded sections", combined)
        self.assertIn("do not paste raw command output", combined)

    def test_idle_coordination_waits_do_not_churn_context_or_status(self):
        entrypoint = (ROOT / "skills/thin-coordinator/SKILL.md").read_text(encoding="utf-8").lower()
        scheduling = (ROOT / "skills/thin-coordinator/references/scheduling.md").read_text(encoding="utf-8").lower()
        combined = "\n".join((entrypoint, scheduling))

        self.assertIn("longest safe event wait", combined)
        self.assertIn("do not re-read", combined)
        self.assertIn("do not emit", combined)

    def test_execution_run_has_one_goal_and_a_final_response_gate(self):
        entrypoint = (ROOT / "skills/thin-coordinator/SKILL.md").read_text(encoding="utf-8").lower()
        run_state = (ROOT / "skills/thin-coordinator/references/run-state.md").read_text(encoding="utf-8").lower()
        combined = "\n".join((entrypoint, run_state))

        self.assertIn("create_goal", combined)
        self.assertIn("get_goal", combined)
        self.assertIn("update_goal", combined)
        self.assertIn("exactly one", combined)
        self.assertIn("status-only", combined)
        self.assertIn("final response gate", combined)
        self.assertIn("commentary", combined)
        self.assertIn("wait timeout", combined)

    def test_coordinator_pulses_liveness_without_rewriting_progress(self):
        dashboard = (ROOT / "skills/thin-coordinator/references/dashboard.md").read_text(encoding="utf-8").lower()

        self.assertIn("workflow-dashboard pulse", dashboard)
        self.assertIn("heartbeat_at", dashboard)
        self.assertIn("preserves", dashboard)
        self.assertIn("updated_at", dashboard)
        self.assertIn("before the stale threshold", dashboard)

    def test_live_dashboard_migration_never_installs_during_coordination(self):
        dashboard = (ROOT / "skills/thin-coordinator/references/dashboard.md").read_text(encoding="utf-8").lower()

        self.assertNotIn("then install the standalone application", dashboard)
        self.assertIn("explicit maintenance", dashboard)
        self.assertIn("paused or complete", dashboard)

    def test_context_pressure_does_not_imply_a_new_coordinator(self):
        scheduling = (ROOT / "skills/thin-coordinator/references/scheduling.md").read_text(encoding="utf-8").lower()

        self.assertNotIn("a new coordinator resumes", scheduling)
        self.assertIn("same coordinator resumes", scheduling)
        self.assertIn("truly cannot continue", scheduling)

    def test_assignment_contract_has_one_complete_owner(self):
        scheduling = (ROOT / "skills/thin-coordinator/references/scheduling.md").read_text(encoding="utf-8").lower()

        for required in (
            "canonical agent path",
            "canonical parent agent path",
            "handoff path",
            "pause-checkpoint path",
            "dashboard availability",
            "progress path",
            "child_capacity",
        ):
            self.assertIn(required, scheduling)

    def test_reviewer_children_do_not_write_the_review_manifest(self):
        review = (ROOT / "skills/review-ticket/SKILL.md").read_text(encoding="utf-8").lower()

        self.assertIn("reviewer children return", review)
        self.assertIn("only the parent writes", review)
        self.assertIn("review manifest", review)

        repair = (ROOT / "skills/review-ticket/references/reviewer-repair.md").read_text(encoding="utf-8").lower()
        self.assertIn("return the repair evidence", repair)
        self.assertIn("parent records", repair)

    def test_dashboard_is_loaded_only_when_required_or_already_recorded(self):
        entrypoint = (ROOT / "skills/thin-coordinator/SKILL.md").read_text(encoding="utf-8").lower()

        self.assertIn("user or workflow requires it", entrypoint)
        self.assertIn("run.md` already records one", entrypoint)
        self.assertIn("do not start a dashboard solely for coordination", entrypoint)

    def test_coordinated_workers_reuse_supplied_workspace_identity(self):
        implementer = (ROOT / "skills/implement-ticket/SKILL.md").read_text(encoding="utf-8").lower()
        reviewer = (ROOT / "skills/review-ticket/SKILL.md").read_text(encoding="utf-8").lower()

        for entrypoint in (implementer, reviewer):
            self.assertIn("coordinator supplies canonical paths", entrypoint)
            self.assertIn("do not repeat registry discovery", entrypoint)


if __name__ == "__main__":
    unittest.main()
