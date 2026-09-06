"""Keep risk-based reviewer-count guidance aligned across workflow skills."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class ReviewScalingGuidanceTests(unittest.TestCase):
    def test_one_reviewer_is_default_and_coordinator_owns_escalation(self):
        review = (ROOT / "skills/review-ticket/SKILL.md").read_text(encoding="utf-8").lower()
        coordinate = (ROOT / "skills/coordinate-work/SKILL.md").read_text(encoding="utf-8").lower()
        scheduling = (ROOT / "skills/coordinate-work/references/scheduling.md").read_text(encoding="utf-8").lower()
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        launcher = (ROOT / "skills/review-ticket/agents/openai.yaml").read_text(encoding="utf-8").lower()
        ticket_format = (ROOT / "skills/spec-to-tickets/references/ticket-format.md").read_text(encoding="utf-8").lower()

        for document in (review, coordinate, scheduling, readme, launcher, ticket_format):
            self.assertIn("one reviewer", document)
            self.assertIn("both axes", document)

        self.assertIn("coordinator decides", review)
        self.assertIn("implementer does not choose", review)
        for risk in ("security", "concurrency", "migration", "financial", "public contract", "large"):
            self.assertIn(risk, review)


if __name__ == "__main__":
    unittest.main()
