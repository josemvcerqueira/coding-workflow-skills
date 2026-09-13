"""Regression checks for low-overhead coordination and runtime verification guidance."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def read(relative):
    return (SKILLS / relative).read_text(encoding="utf-8").lower()


class EfficiencyGuidanceTests(unittest.TestCase):
    def test_thin_coordinator_replaces_legacy_entrypoint(self):
        self.assertTrue((SKILLS / "thin-coordinator/SKILL.md").is_file())
        self.assertFalse((SKILLS / "coordinate-work").exists())
        coordinator = read("thin-coordinator/SKILL.md")
        self.assertIn("measured release critical path", coordinator)
        self.assertIn("longest safe event wait", coordinator)
        self.assertIn("no more than three short sentences", coordinator)

    def test_small_tickets_reuse_component_and_review_lanes_safely(self):
        scheduling = read("thin-coordinator/references/scheduling.md")
        implementation = read("implement-ticket/SKILL.md")
        for required in (
            "component lane batches",
            "exactly one writer",
            "separate baseline",
            "fresh focused context",
            "same lane",
        ):
            self.assertIn(required, scheduling)
        self.assertIn("new acknowledged assignment", implementation)
        self.assertIn("does not combine ticket records", implementation)

    def test_database_snapshot_is_immutable_and_each_lane_owns_a_clone(self):
        scheduling = read("thin-coordinator/references/scheduling.md")
        for required in (
            "content-addressed database snapshots",
            "read-only cache",
            "single builder",
            "run-owned database",
            "no lane writes",
            "engine and major version",
            "migrations",
            "seed generator",
        ):
            self.assertIn(required, scheduling)

    def test_expensive_runtime_has_collect_all_and_open_circuit_gates(self):
        checks = read("setup-workflow/references/check-scope.md")
        for required in (
            "collect-all gate",
            "cannot fall through to a startup timeout",
            "terminal owner fails immediately",
            "after two",
            "the circuit is open",
            "diagnostic probes",
            "non-accepting evidence",
        ):
            self.assertIn(required, checks)

    def test_review_closure_has_one_bounded_successor(self):
        review = read("review-ticket/SKILL.md")
        closure = read("review-ticket/references/closure.md")
        self.assertIn("monotonic review closure", review)
        for required in (
            "one atomic, deduplicated finding batch",
            "regressions caused by the correction",
            "automatic_successor_rounds_remaining: 1",
            "reviewers recommend dispositions",
            "ask the user only",
        ):
            self.assertIn(required, closure)


if __name__ == "__main__":
    unittest.main()
