"""Mechanical integrity and context-budget checks for the skill suite."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class SkillSuiteIntegrityTests(unittest.TestCase):
    def test_skill_entrypoints_have_explicit_invocation_policy(self):
        for skill_path in sorted(SKILLS.glob("*/SKILL.md")):
            with self.subTest(skill=skill_path.parent.name):
                text = skill_path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                self.assertIn(f'\nname: {skill_path.parent.name}\n', text)
                frontmatter = text.split("---", 2)[1]
                self.assertRegex(frontmatter, r"(?m)^disable-model-invocation:\s*true\s*$")

                policy_path = skill_path.parent / "agents/openai.yaml"
                self.assertTrue(policy_path.is_file(), policy_path)
                policy = policy_path.read_text(encoding="utf-8")
                self.assertRegex(policy, r"(?m)^\s*allow_implicit_invocation:\s*false\s*$")

    def test_all_skill_document_links_resolve(self):
        for document in sorted(SKILLS.glob("**/*.md")):
            with self.subTest(document=document.relative_to(ROOT)):
                text = document.read_text(encoding="utf-8")
                for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                    if "://" in target or target.startswith("#"):
                        continue
                    resolved = (document.parent / target.split("#", 1)[0]).resolve()
                    self.assertTrue(resolved.exists(), f"{document}: broken link {target}")

    def test_execution_and_closure_reach_the_same_check_scope_contract(self):
        contract = (SKILLS / "setup-workflow/references/check-scope.md").resolve()
        for relative in (
            "implement-ticket/SKILL.md",
            "review-ticket/SKILL.md",
            "verify-feature/SKILL.md",
            "setup-workflow/references/close-workflow.md",
            "setup-workflow/references/handoff-manifest.md",
        ):
            with self.subTest(document=relative):
                document = SKILLS / relative
                targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8"))
                local_targets = {
                    (document.parent / target.split("#", 1)[0]).resolve()
                    for target in targets if "://" not in target and not target.startswith("#")
                }
                self.assertIn(contract, local_targets)

    def test_no_skill_entrypoint_exceeds_the_suite_ceiling(self):
        for skill_path in sorted(SKILLS.glob("*/SKILL.md")):
            with self.subTest(skill=skill_path.parent.name):
                words = len(re.findall(r"\S+", skill_path.read_text(encoding="utf-8")))
                self.assertLessEqual(words, 1800, f"{skill_path.parent.name} loads {words} words")

    def test_orchestration_entrypoints_preserve_context_headroom(self):
        budgets = {
            "coordinate-work": 1600,
            "implement-ticket": 1600,
            "review-ticket": 1600,
        }

        for skill, budget in budgets.items():
            with self.subTest(skill=skill):
                text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
                words = len(re.findall(r"\S+", text))
                self.assertLessEqual(words, budget, f"{skill} loads {words} words before task evidence")


if __name__ == "__main__":
    unittest.main()
