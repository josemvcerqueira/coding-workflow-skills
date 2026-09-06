"""Run with python3 -m unittest discover -s scripts -p 'test_*.py'."""

import json
import tempfile
import unittest
from pathlib import Path

from validate_tickets import validate


class TicketValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "INDEX.md").write_text("# Tickets\n", encoding="utf-8")
        (self.root / "spec.md").write_text("# Spec\nREQ-001\nAC-001\n", encoding="utf-8")

    def ticket(self, tid, **changes):
        data = dict(id=tid, title="Working slice", status="pending", spec="spec.md",
                    spec_refs=["REQ-001", "AC-001"], blocked_by=[],
                    exclusive_resources=[], external_blockers=[], assignee=None,
                    implementation_ref=None, available=False, superseded_by=[])
        data.update(changes)
        metadata = "\n".join(f"{key}: {json.dumps(value)}" for key, value in data.items())
        (self.root / f"{tid}.md").write_text(f"---\n{metadata}\n---\n# Outcome\n", encoding="utf-8")

    def reviewed_ticket(self, tid="T-001", **changes):
        report = self.root / "reviews" / tid / "R-001.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("# Review\nEvidence for both axes.\n", encoding="utf-8")
        values = dict(status="ready", implementation_ref="commit:abc",
                      review_ref=str(report.relative_to(self.root)), available=True)
        values.update(changes)
        self.ticket(tid, **values)

    def test_dependency_waits_for_available_implementation(self):
        self.ticket("T-001", status="implemented", implementation_ref="commit:abc")
        self.ticket("T-002", blocked_by=["T-001"])
        self.assertEqual(validate(self.root)["ready"], [])
        self.ticket("T-001", status="implemented", implementation_ref="commit:abc", available=True)
        self.assertEqual(validate(self.root)["ready"], [])
        self.reviewed_ticket()
        result = validate(self.root)
        self.assertEqual(result["ready"], ["T-002"])
        self.assertEqual(result["unblocks"]["T-001"], ["T-002"])

    def test_cycle_is_rejected(self):
        self.ticket("T-001", blocked_by=["T-002"])
        self.ticket("T-002", blocked_by=["T-001"])
        self.assertTrue(any("Cycle" in error for error in validate(self.root)["errors"]))

    def test_missing_dependency_is_rejected(self):
        self.ticket("T-001", blocked_by=["T-999"])
        self.assertTrue(validate(self.root)["errors"])

    def test_missing_spec_reference_is_rejected(self):
        self.ticket("T-001", spec_refs=["REQ-002"])
        self.assertTrue(validate(self.root)["errors"])

    def test_active_resource_prevents_assignment(self):
        self.ticket("T-001", status="in_progress", assignee="agent-1",
                    exclusive_resources=["session-contract"])
        self.ticket("T-002", exclusive_resources=["session-contract"])
        self.ticket("T-003")
        result = validate(self.root)
        self.assertEqual(result["ready"], ["T-002", "T-003"])
        self.assertEqual(result["assignable_with_current_active_work"], ["T-003"])

    def test_active_resource_collision_is_rejected(self):
        for tid in ("T-001", "T-002"):
            self.ticket(tid, status="in_progress", assignee=tid,
                        exclusive_resources=["session-contract"])
        self.assertTrue(any("conflict" in error for error in validate(self.root)["errors"]))

    def test_active_work_requires_available_prerequisites(self):
        self.ticket("T-001")
        self.ticket("T-002", status="in_progress", assignee="agent-2", blocked_by=["T-001"])
        self.assertTrue(any("unavailable prerequisite" in error for error in validate(self.root)["errors"]))
        self.reviewed_ticket()
        self.assertEqual(validate(self.root)["errors"], [])

    def test_reviewed_but_unavailable_does_not_unblock(self):
        self.reviewed_ticket(available=False)
        self.ticket("T-002", blocked_by=["T-001"])
        self.assertEqual(validate(self.root)["ready"], [])

    def test_review_and_revision_do_not_unblock(self):
        for status in ("in_review", "revision_required"):
            with self.subTest(status=status):
                self.reviewed_ticket(status=status, available=False)
                self.ticket("T-002", blocked_by=["T-001"])
                result = validate(self.root)
                self.assertEqual(result["errors"], [])
                self.assertEqual(result["ready"], [])

    def test_final_review_states_require_local_evidence(self):
        for status in ("ready", "revision_required"):
            for review_ref in (None, "missing.md", " "):
                with self.subTest(status=status, review_ref=review_ref):
                    self.ticket("T-001", status=status, implementation_ref="commit:abc",
                                review_ref=review_ref)
                    self.assertTrue(validate(self.root)["errors"])

    def test_review_reserves_resources(self):
        self.reviewed_ticket(status="in_review", available=False,
                             exclusive_resources=["shared-contract"])
        self.ticket("T-002", exclusive_resources=["shared-contract"])
        result = validate(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["assignable_with_current_active_work"], [])

    def test_revision_cannot_remain_available(self):
        self.reviewed_ticket(status="revision_required")
        self.assertTrue(validate(self.root)["errors"])

    def test_ready_with_external_blocker_is_invalid(self):
        self.reviewed_ticket(external_blockers=["Required integration check unavailable"])
        self.assertTrue(validate(self.root)["errors"])

    def test_ready_without_implementation_is_invalid(self):
        self.reviewed_ticket(implementation_ref=None)
        self.assertTrue(validate(self.root)["errors"])

    def test_active_external_blocker_is_reported(self):
        self.ticket("T-001", status="in_progress", assignee="agent-1",
                    external_blockers=["Waiting for sandbox access"])
        self.assertTrue(any("external blockers" in error for error in validate(self.root)["errors"]))

    def test_external_blocker_prevents_readiness(self):
        self.ticket("T-001", external_blockers=["Waiting for sandbox access"])
        self.assertEqual(validate(self.root)["ready"], [])

    def test_invalid_completion_is_rejected(self):
        self.ticket("T-001", status="implemented")
        self.assertTrue(validate(self.root)["errors"])

    def test_superseded_dependency_requires_reconciliation(self):
        self.ticket("T-001", status="superseded", superseded_by=["T-003"])
        self.ticket("T-002", blocked_by=["T-001"])
        self.ticket("T-003")
        self.assertTrue(any("superseded" in error for error in validate(self.root)["errors"]))

    def test_superseded_history_does_not_block_replacement_graph(self):
        self.ticket("T-001", status="superseded", superseded_by=["T-003"])
        self.ticket("T-002", status="superseded", blocked_by=["T-001"], superseded_by=["T-004"])
        self.ticket("T-003")
        self.ticket("T-004", blocked_by=["T-003"])
        result = validate(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["ready"], ["T-003"])

    def test_whitespace_evidence_and_list_values_are_rejected(self):
        for changes in (
            dict(status="implemented", implementation_ref=" ", available=True),
            dict(status="in_progress", assignee=" "),
            dict(exclusive_resources=[" "]),
        ):
            with self.subTest(changes=changes):
                self.ticket("T-001", **changes)
                self.assertTrue(validate(self.root)["errors"])


class WorkflowMarkerTests(unittest.TestCase):
    def workflow(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "workflow" / "tickets"
        root.mkdir(parents=True)
        (root / "INDEX.md").write_text("# Tickets\n", encoding="utf-8")
        (root / "spec.md").write_text("REQ-001\n", encoding="utf-8")
        data = dict(id="T-001", title="Working slice", status="pending", spec="spec.md",
                    spec_refs=["REQ-001"], blocked_by=[], exclusive_resources=[],
                    external_blockers=[], assignee=None, implementation_ref=None,
                    available=False, superseded_by=[])
        metadata = "\n".join(f"{key}: {json.dumps(value)}" for key, value in data.items())
        (root / "T-001.md").write_text(f"---\n{metadata}\n---\n", encoding="utf-8")
        return root

    def assert_marker_blocks(self, root, marker_name):
        result = validate(root)
        self.assertEqual(set(result), {"errors"})
        self.assertTrue(result["errors"])
        for error in result["errors"]:
            self.assertIn(marker_name.removesuffix(".md").lower(), error.lower())
            self.assertIn("no scheduling", error.lower())
            self.assertIn("resume cleanup or start a new workflow", error.lower())

    def test_each_local_or_parent_marker_blocks_active_validation(self):
        for name in ("CLOSING.md", "COMPLETED.md"):
            for location in ("local", "parent"):
                with self.subTest(marker=name, location=location):
                    root = self.workflow()
                    directory = root if location == "local" else root.parent
                    (directory / name).write_text("# Workflow record\n", encoding="utf-8")
                    self.assert_marker_blocks(root, name)

    def test_marker_presence_blocks_regardless_of_contents_or_file_type(self):
        for name in ("CLOSING.md", "COMPLETED.md"):
            for location in ("local", "parent"):
                for kind in ("empty", "malformed", "directory", "symlink", "broken_symlink"):
                    with self.subTest(marker=name, location=location, kind=kind):
                        root = self.workflow()
                        directory = root if location == "local" else root.parent
                        marker = directory / name
                        if kind == "directory":
                            marker.mkdir()
                        elif kind == "symlink":
                            marker.symlink_to(root / "spec.md")
                        elif kind == "broken_symlink":
                            marker.symlink_to(directory / "nonexistent-record")
                        else:
                            marker.write_bytes(b"" if kind == "empty" else b"\xff{invalid")
                        self.assert_marker_blocks(root, name)

    def test_markers_block_before_missing_spec_or_malformed_metadata(self):
        for name in ("CLOSING.md", "COMPLETED.md"):
            for location in ("local", "parent"):
                for defect in ("missing_spec", "malformed_metadata"):
                    with self.subTest(marker=name, location=location, defect=defect):
                        root = self.workflow()
                        if defect == "missing_spec":
                            (root / "spec.md").unlink()
                        else:
                            (root / "T-001.md").write_text("invalid metadata", encoding="utf-8")
                        directory = root if location == "local" else root.parent
                        (directory / name).touch()
                        self.assert_marker_blocks(root, name)

    def test_missing_spec_without_marker_still_fails(self):
        root = self.workflow()
        (root / "spec.md").unlink()
        result = validate(root)
        self.assertEqual(set(result), {"errors"})
        self.assertTrue(any("Missing spec" in error for error in result["errors"]))

    def test_unrelated_sibling_workflow_markers_do_not_block(self):
        root = self.workflow()
        sibling = root.parent.parent / "other-workflow"
        sibling.mkdir()
        for name in ("CLOSING.md", "COMPLETED.md"):
            (sibling / name).touch()
        result = validate(root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["assignable_with_current_active_work"], ["T-001"])

    def test_symlinked_ticket_directory_checks_resolved_workflow_parent(self):
        for name in ("CLOSING.md", "COMPLETED.md"):
            with self.subTest(marker=name):
                root = self.workflow()
                alias = root.parent.parent / "ticket-alias"
                alias.symlink_to(root, target_is_directory=True)
                (root.parent / name).touch()
                self.assert_marker_blocks(alias, name)

    def test_completed_reviewed_records_do_not_pass_active_validation(self):
        root = self.workflow()
        ticket = root / "T-001.md"
        text = ticket.read_text(encoding="utf-8")
        text = text.replace('status: "pending"', 'status: "ready"')
        text = text.replace('implementation_ref: null', 'implementation_ref: "commit:abc"')
        text = text.replace('available: false', 'available: true')
        text = text.replace('superseded_by: []', 'superseded_by: []\nreview_ref: "review.md"')
        ticket.write_text(text, encoding="utf-8")
        (root / "review.md").write_text("# Review evidence\n", encoding="utf-8")
        self.assertEqual(validate(root)["errors"], [])
        (root.parent / "COMPLETED.md").touch()
        self.assert_marker_blocks(root, "COMPLETED.md")


if __name__ == "__main__":
    unittest.main()
