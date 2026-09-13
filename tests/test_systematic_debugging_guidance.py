"""Contract tests for the systematic-debugging workflow integration."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
DEBUGGER = SKILLS / "systematic-debugging"
METHOD = DEBUGGER / "references/diagnostic-method.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").lower()


def local_links(relative: str) -> set[Path]:
    document = ROOT / relative
    targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8"))
    return {
        (document.parent / target.split("#", 1)[0]).resolve()
        for target in targets
        if "://" not in target and not target.startswith("#")
    }


class SystematicDebuggingGuidanceTests(unittest.TestCase):
    def test_model_facing_skill_documents_do_not_name_superpowers(self):
        documents = sorted(SKILLS.rglob("*.md")) + sorted(SKILLS.rglob("*.yaml"))
        offenders = [
            str(document.relative_to(ROOT))
            for document in documents
            if "superpowers" in document.read_text(encoding="utf-8").lower()
        ]

        self.assertEqual([], offenders)

    def test_model_invoked_companion_exists_with_canonical_method(self):
        entrypoint = DEBUGGER / "SKILL.md"
        policy = DEBUGGER / "agents/openai.yaml"

        self.assertTrue(entrypoint.is_file(), entrypoint)
        self.assertTrue(METHOD.is_file(), METHOD)
        self.assertTrue(policy.is_file(), policy)

        frontmatter = entrypoint.read_text(encoding="utf-8").split("---", 2)[1]
        self.assertNotRegex(frontmatter, r"(?m)^disable-model-invocation:\s*true\s*$")
        self.assertRegex(policy.read_text(encoding="utf-8"), r"(?m)^\s*allow_implicit_invocation:\s*true\s*$")
        self.assertIn(METHOD.resolve(), local_links("skills/systematic-debugging/SKILL.md"))

    def test_failure_stages_reach_the_debugging_companion(self):
        entrypoint = (DEBUGGER / "SKILL.md").resolve()
        consumers = (
            "skills/review-ticket/SKILL.md",
            "skills/review-ticket/references/reviewer-briefs.md",
            "skills/implement-ticket/SKILL.md",
            "skills/verify-feature/SKILL.md",
            "skills/thin-coordinator/SKILL.md",
            "skills/thin-coordinator/references/run-state.md",
        )

        for relative in consumers:
            with self.subTest(document=relative):
                self.assertIn(entrypoint, local_links(relative))

    def test_diagnosis_only_stages_keep_product_source_read_only(self):
        reviewer = read("skills/review-ticket/references/reviewer-briefs.md")
        verifier = read("skills/verify-feature/SKILL.md")
        self.assertTrue(METHOD.is_file(), METHOD)
        method = METHOD.read_text(encoding="utf-8").lower()

        for name, text in (("reviewer", reviewer), ("verifier", verifier)):
            with self.subTest(stage=name):
                self.assertIn("diagnosis-only", text)
                self.assertIn("product source", text)
                self.assertIn("systematic debugging", text)

        self.assertIn("does not grant", method)
        self.assertIn("bounded reviewer repair", reviewer)
        self.assertIn("parent", reviewer)

    def test_canonical_method_defines_classification_and_routing(self):
        self.assertTrue(METHOD.is_file(), METHOD)
        method = METHOD.read_text(encoding="utf-8").lower()
        expected_routes = {
            "product_defect": "implementer",
            "test_or_harness_defect": "test or harness owner",
            "environment_blocker": "coordinator or user",
            "pre_existing_failure": "coordinator",
            "expected_behavior_or_spec_gap": "user or specification owner",
            "inconclusive": "coordinator",
        }

        for classification, owner in expected_routes.items():
            with self.subTest(classification=classification):
                row = re.search(rf"(?m)^\|\s*`{classification}`\s*\|([^\n]+)$", method)
                self.assertIsNotNone(row, classification)
                self.assertIn(owner, row.group(1))

    def test_third_unsuccessful_correction_escalates_architecture(self):
        implementer = read("skills/implement-ticket/SKILL.md")
        coordinator = read("skills/thin-coordinator/references/run-state.md")

        for name, text in (("implementer", implementer), ("coordinator", coordinator)):
            with self.subTest(stage=name):
                self.assertRegex(text, r"three|third")
                self.assertRegex(text, r"architect")
                self.assertIn("systematic debugging", text)


if __name__ == "__main__":
    unittest.main()
