#!/usr/bin/env python3
"""Validate local ticket metadata and print derived scheduling facts.

Usage: python3 validate_tickets.py PATH_TO_TICKET_DIRECTORY
Uses only the Python standard library. Does not edit files or claim work.
"""

import json
import re
import sys
from pathlib import Path


def validate(root):
    root = Path(root)
    errors = []
    # Marker presence closes active validation; never read or follow the marker.
    marker_root = root.resolve()
    for directory in (marker_root, marker_root.parent):
        for name, state in (("CLOSING.md", "closing"), ("COMPLETED.md", "completed")):
            marker = directory / name
            try:
                marker.lstat()
            except FileNotFoundError:
                continue
            except OSError as exc:
                errors.append(f"Cannot inspect {state} marker {marker}: {exc}; "
                              "no scheduling; resume cleanup or start a new workflow")
            else:
                errors.append(f"Workflow is {state} ({marker}); "
                              "no scheduling; resume cleanup or start a new workflow")
    if errors:
        return {"errors": errors}

    tickets = {}
    fields = {
        "id": str, "title": str, "status": str, "spec": str,
        "spec_refs": list, "blocked_by": list, "exclusive_resources": list,
        "external_blockers": list, "available": bool, "superseded_by": list,
    }
    if not (root / "INDEX.md").is_file():
        errors.append("Missing INDEX.md")
    paths = sorted(root.glob("T-*.md"))
    if not paths:
        errors.append("No ticket files found")
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            if not lines or lines[0] != "---":
                raise ValueError("Missing frontmatter")
            end = lines.index("---", 1)
            data = {}
            for line in lines[1:end]:
                if not line.strip():
                    continue
                key, sep, value = line.partition(":")
                if not sep or key in data:
                    raise ValueError("Invalid or duplicate metadata key")
                data[key] = json.loads(value.strip())
            for key, kind in fields.items():
                if type(data.get(key)) is not kind:
                    raise ValueError(f"{key} must be {kind.__name__}")
                if kind is list:
                    values = data[key]
                    if any(not isinstance(v, str) or not v.strip() for v in values):
                        raise ValueError(f"{key} must contain nonempty strings")
                    if len(values) != len(set(values)):
                        raise ValueError(f"{key} contains duplicates")
            for key in ("assignee", "implementation_ref"):
                if key not in data or not (
                    data[key] is None or isinstance(data[key], str) and data[key].strip()
                ):
                    raise ValueError(f"{key} must be null or a nonempty string")
            tid = data["id"]
            if not re.fullmatch(r"T-[0-9]{3,}", tid) or path.stem != tid:
                raise ValueError("ID must match filename, such as T-001.md")
            if tid in tickets:
                raise ValueError("Duplicate ticket ID")
            if not data["title"].strip() or not data["spec_refs"]:
                raise ValueError("Title and spec_refs must not be empty")
            status = data["status"]
            if status not in {"pending", "in_progress", "implemented", "in_review",
                              "revision_required", "ready", "superseded"}:
                raise ValueError("Invalid status")
            if status == "in_progress" and not data["assignee"]:
                raise ValueError("In-progress work needs an assignee")
            if status in {"implemented", "in_review", "revision_required", "ready"} and not data["implementation_ref"]:
                raise ValueError("Implemented or reviewed work needs an implementation_ref")
            if data["available"] and status not in {"implemented", "in_review", "ready"}:
                raise ValueError("Only implemented, in-review, or ready work can be available")
            review_ref = data.get("review_ref")
            if review_ref is not None:
                if not isinstance(review_ref, str) or not review_ref.strip() or Path(review_ref).is_absolute():
                    raise ValueError("review_ref must be null or a relative report path")
                if not (root / review_ref).is_file():
                    raise ValueError("Missing review report")
            if status in {"ready", "revision_required"} and not review_ref:
                raise ValueError("Ready or revision-required work needs a review_ref")
            if status == "ready" and data["external_blockers"]:
                raise ValueError("Ready work cannot have unresolved external blockers")
            if bool(data["superseded_by"]) != (status == "superseded"):
                raise ValueError("Only superseded work must name replacements")
            if not data["spec"] or Path(data["spec"]).is_absolute():
                raise ValueError("spec must be a relative file path")
            spec = (root / data["spec"]).resolve()
            if not spec.is_file():
                raise ValueError(f"Missing spec: {data['spec']}")
            source = spec.read_text(encoding="utf-8")
            for ref in data["spec_refs"]:
                if not re.search(r"(?<![\w-])" + re.escape(ref) + r"(?![\w-])", source):
                    raise ValueError(f"Spec reference not found: {ref}")
            tickets[tid] = data
        except (ValueError, OSError) as exc:
            errors.append(f"{path.name}: {exc}")

    for tid, data in tickets.items():
        for edge in ("blocked_by", "superseded_by"):
            for target in data[edge]:
                if target == tid or target not in tickets:
                    errors.append(f"{tid}: invalid {edge} target {target}")
                elif (edge == "blocked_by" and data["status"] != "superseded"
                      and tickets[target]["status"] == "superseded"):
                    errors.append(f"{tid}: dependency {target} is superseded; reconcile it")

    def check_cycles(edge):
        visiting, visited = set(), set()

        def visit(tid):
            if tid in visiting:
                errors.append(f"Cycle in {edge} at {tid}")
                return
            if tid in visited:
                return
            visiting.add(tid)
            for target in tickets[tid][edge]:
                if target in tickets:
                    visit(target)
            visiting.remove(tid)
            visited.add(tid)
        for tid in tickets:
            visit(tid)

    check_cycles("blocked_by")
    check_cycles("superseded_by")
    active = [tid for tid, d in tickets.items() if d["status"] in {"in_progress", "in_review"}]
    for tid in active:
        data = tickets[tid]
        if data["external_blockers"] and data["status"] == "in_progress":
            errors.append(f"{tid}: active work has unresolved external blockers")
        for target in data["blocked_by"]:
            prerequisite = tickets.get(target)
            if prerequisite and (
                prerequisite["status"] != "ready" or not prerequisite["available"]
            ):
                errors.append(f"{tid}: active work has unavailable prerequisite {target}")
    for i, left in enumerate(active):
        for right in active[i + 1:]:
            overlap = set(tickets[left]["exclusive_resources"]) & set(tickets[right]["exclusive_resources"])
            if overlap:
                errors.append(f"Active resource conflict: {left}, {right}: {sorted(overlap)}")
    if errors:
        return {"errors": errors}

    ready = [
        tid for tid, d in tickets.items()
        if d["status"] == "pending" and not d["external_blockers"]
        and all(tickets[b]["status"] == "ready" and tickets[b]["available"]
                for b in d["blocked_by"])
    ]
    active_resources = {r for tid in active for r in tickets[tid]["exclusive_resources"]}
    assignable = [
        tid for tid in ready if tickets[tid]["assignee"] is None
        and not active_resources.intersection(tickets[tid]["exclusive_resources"])
    ]
    return {
        "errors": [],
        "ticket_count": len(tickets),
        "ready": ready,
        "assignable_with_current_active_work": assignable,
        "unblocks": {tid: [other for other, d in tickets.items() if tid in d["blocked_by"]]
                     for tid in tickets},
        "exclusive_resources": {tid: d["exclusive_resources"] for tid, d in tickets.items()},
        "note": "Ready lists pending candidates, not reviewed-complete tickets. Candidates are not claims. Check review evidence, resource conflicts, and availability before dispatch; report existence does not prove review results.",
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: validate_tickets.py TICKET_DIRECTORY")
    result = validate(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(1 if result["errors"] else 0)
