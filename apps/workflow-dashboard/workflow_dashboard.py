#!/usr/bin/env python3
"""Safe progress and telemetry data layer for the local workflow dashboard."""

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

SCHEMA_VERSION = 1
WARNING_CONTEXT_OCCUPANCY = 0.80
CRITICAL_CONTEXT_OCCUPANCY = 0.95
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")
TERMINAL_STATES = {"complete", "completed", "paused", "stopped", "whole_feature_verified"}
REQUIRED_PROGRESS = ("agent_path", "parent_agent_path", "role", "stage", "state", "summary", "next_action")
OPTIONAL_PROGRESS = (
    "ticket_id", "session_id", "blocker", "file_lease", "handoff_path",
    "reserved_test_resources", "stage_started_at", "expected_duration_seconds",
    "estimate_set_at", "estimate_note", "runtime_provider", "requested_model",
    "heartbeat_at",
)
PROGRESS_KEYS = set(REQUIRED_PROGRESS) | set(OPTIONAL_PROGRESS) | {"schema_version", "started_at", "updated_at"}
TICKET_STATUSES = {"pending", "in_progress", "implemented", "in_review", "revision_required", "ready", "superseded"}
GATE_SCORE = {"pending": 0, "in_progress": 25, "implemented": 50, "revision_required": 50, "in_review": 75, "ready": 75}
UUID_SUFFIX = re.compile(r"(?:^|[-_])([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", re.I)
JSON_NUMBER = re.compile(rb"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$")
FAST_EVENT_TYPE = re.compile(rb'"payload"\s*:\s*\{\s*"type"\s*:\s*"([A-Za-z0-9_]+)"')
MAX_SAFE_RECORD_BYTES = 1_048_576


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _canonical_path(value):
    if not isinstance(value, str) or not value.startswith("/") or "//" in value:
        return False
    parsed = PurePosixPath(value)
    return all(part not in {".", ".."} for part in parsed.parts) and str(parsed) == value


def _agent_filename(agent_path):
    prefix = re.sub(r"[^A-Za-z0-9._-]+", "_", agent_path.strip("/")) or "root"
    digest = hashlib.sha256(agent_path.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}.json"


def _parse_time(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def _valid_progress(record, expected_filename=None):
    if not isinstance(record, dict) or set(record) - PROGRESS_KEYS:
        return False
    if record.get("schema_version") != SCHEMA_VERSION:
        return False
    if any(not isinstance(record.get(key), str) or not record[key].strip() for key in REQUIRED_PROGRESS):
        return False
    if not _canonical_path(record["agent_path"]) or not _canonical_path(record["parent_agent_path"]):
        return False
    if _parse_time(record.get("started_at")) is None or _parse_time(record.get("updated_at")) is None:
        return False
    for key in ("ticket_id", "session_id", "blocker", "file_lease", "handoff_path"):
        if key in record and record[key] is not None and (not isinstance(record[key], str) or not record[key].strip()):
            return False
    for key in ("stage_started_at", "estimate_set_at", "heartbeat_at"):
        if key in record and record[key] is not None and _parse_time(record[key]) is None:
            return False
    duration = record.get("expected_duration_seconds")
    if duration is not None and (
        not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0
    ):
        return False
    for key in ("estimate_note", "runtime_provider", "requested_model"):
        if key in record and record[key] is not None and (
            not isinstance(record[key], str) or not record[key].strip()
        ):
            return False
    resources = record.get("reserved_test_resources")
    if resources is not None and (not isinstance(resources, list) or any(not isinstance(item, str) or not item.strip() for item in resources)):
        return False
    return expected_filename is None or expected_filename == _agent_filename(record["agent_path"])


def write_progress(workflow: Path, record: dict) -> Path:
    """Atomically replace one agent's schema-limited progress record."""
    if not isinstance(record, dict):
        raise ValueError("progress record must be an object")
    missing = set(REQUIRED_PROGRESS) - set(record)
    if missing:
        raise ValueError(f"missing progress fields: {', '.join(sorted(missing))}")
    workflow = Path(workflow)
    directory = workflow / "progress"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / _agent_filename(record["agent_path"])
    existing_started = None
    if target.is_file() and not target.is_symlink():
        try:
            previous = json.loads(target.read_text(encoding="utf-8"))
            if isinstance(previous, dict):
                existing_started = previous.get("started_at")
        except (OSError, json.JSONDecodeError):
            pass
    saved = {key: record[key] for key in PROGRESS_KEYS if key in record}
    saved.update({"schema_version": SCHEMA_VERSION, "started_at": record.get("started_at") or existing_started or _now_iso(), "updated_at": record.get("updated_at") or _now_iso()})
    if not _valid_progress(saved, target.name):
        raise ValueError("invalid progress record")
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=directory, prefix=".progress-", suffix=".tmp", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(saved, temporary, sort_keys=True)
            temporary.write("\n")
        os.replace(temporary_path, target)
    except BaseException:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    return target


def pulse_progress(workflow: Path, agent_path: str) -> Path:
    """Refresh runtime liveness without changing the last progress milestone."""
    workflow = Path(workflow)
    target = workflow / "progress" / _agent_filename(agent_path)
    if not target.is_file() or target.is_symlink():
        raise ValueError("progress record not found")
    try:
        saved = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("invalid progress record") from exc
    if not _valid_progress(saved, target.name) or saved["agent_path"] != agent_path:
        raise ValueError("invalid progress record")
    saved["heartbeat_at"] = _now_iso()
    if not _valid_progress(saved, target.name):
        raise ValueError("invalid progress record")
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=target.parent,
            prefix=".progress-", suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(saved, temporary, sort_keys=True)
            temporary.write("\n")
        os.replace(temporary_path, target)
    except BaseException:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    return target


def _existing_absolute_file(value):
    return isinstance(value, str) and _canonical_path(value) and Path(value).is_file()


def _valid_handoff_manifest(manifest, *, stage, outcome, ticket_id=None):
    """Accept a lifecycle gate only when its compact manifest links real evidence."""
    required_types = {
        "schema_version": int,
        "assignment_id": str,
        "ticket_id": str,
        "stage": str,
        "outcome": str,
        "source_identity": dict,
        "report_paths": list,
        "checks": list,
        "cleanup": dict,
    }
    if (
        not isinstance(manifest, dict)
        or any(type(manifest.get(key)) is not kind for key, kind in required_types.items())
        or manifest["schema_version"] != SCHEMA_VERSION
        or not manifest["assignment_id"].strip()
        or not manifest["ticket_id"].strip()
        or manifest["stage"] != stage
        or manifest["outcome"] != outcome
        or ticket_id is not None and manifest["ticket_id"] != ticket_id
    ):
        return False

    source = manifest["source_identity"]
    if set(("repository", "checkout", "base_revision", "target_revision", "dirty_content_manifest")) - set(source):
        return False
    if not all(
        isinstance(source.get(key), str)
        and _canonical_path(source[key])
        and Path(source[key]).is_dir()
        for key in ("repository", "checkout")
    ):
        return False
    if not isinstance(source.get("base_revision"), str) or not source["base_revision"].strip():
        return False
    target = source.get("target_revision")
    dirty = source.get("dirty_content_manifest")
    if not (isinstance(target, str) and target.strip()) and not _existing_absolute_file(dirty):
        return False

    reports = manifest["report_paths"]
    if not reports or any(not _existing_absolute_file(path) for path in reports):
        return False
    checks = manifest["checks"]
    if not checks or not any(isinstance(check, dict) and check.get("result") == "pass" for check in checks):
        return False
    for check in checks:
        if not isinstance(check, dict):
            return False
        if not isinstance(check.get("command"), str) or not check["command"].strip():
            return False
        if check.get("result") not in {"pass", "fail", "blocked", "not_run"}:
            return False
        evidence_path = check.get("evidence_path")
        if evidence_path is not None and not _existing_absolute_file(evidence_path):
            return False
        skips = check.get("explicit_skips")
        if not isinstance(skips, list):
            return False

    cleanup = manifest["cleanup"]
    if (
        cleanup.get("processes") not in {"stopped", "retained", "unknown"}
        or cleanup.get("resources") not in {"released", "retained", "unknown"}
        or not isinstance(cleanup.get("details"), list)
        or any(not isinstance(item, str) for item in cleanup["details"])
    ):
        return False
    return True


def _read_valid_handoff(path, *, stage, outcome, ticket_id=None):
    try:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError):
        return None
    return manifest if _valid_handoff_manifest(
        manifest, stage=stage, outcome=outcome, ticket_id=ticket_id
    ) else None


def _parse_ticket(path):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        end = lines.index("---", 1) if lines and lines[0] == "---" else -1
    except (OSError, ValueError) as exc:
        raise ValueError(f"{path.name}: invalid frontmatter") from exc
    if end < 0:
        raise ValueError(f"{path.name}: invalid frontmatter")
    data = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep or key in data:
            raise ValueError(f"{path.name}: invalid metadata")
        try:
            data[key] = json.loads(value.strip())
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}: invalid metadata") from exc
    required = {"id": str, "title": str, "status": str, "spec": str, "spec_refs": list, "blocked_by": list, "exclusive_resources": list, "external_blockers": list, "available": bool, "superseded_by": list}
    if any(type(data.get(key)) is not kind for key, kind in required.items()):
        raise ValueError(f"{path.name}: incomplete metadata")
    if not re.fullmatch(r"T-[0-9]{3,}", data["id"]) or path.stem != data["id"] or not data["title"].strip() or data["status"] not in TICKET_STATUSES:
        raise ValueError(f"{path.name}: invalid identity or lifecycle")
    for key in ("spec_refs", "blocked_by", "exclusive_resources", "external_blockers", "superseded_by"):
        values = data[key]
        if any(not isinstance(value, str) or not value.strip() for value in values) or len(values) != len(set(values)):
            raise ValueError(f"{path.name}: invalid {key}")
    for key in ("assignee", "implementation_ref", "review_ref", "integration_ref"):
        if key in data and data[key] is not None and (not isinstance(data[key], str) or not data[key].strip()):
            raise ValueError(f"{path.name}: invalid {key}")
    if data["status"] == "in_progress" and not data.get("assignee"):
        raise ValueError(f"{path.name}: active work needs an assignee")
    if data["status"] in {"implemented", "in_review", "revision_required", "ready"} and not data.get("implementation_ref"):
        raise ValueError(f"{path.name}: lifecycle state needs implementation evidence")
    if data["status"] in {"ready", "revision_required"} and not data.get("review_ref"):
        raise ValueError(f"{path.name}: lifecycle state needs review evidence")
    review_ref = data.get("review_ref")
    if review_ref is not None and (Path(review_ref).is_absolute() or not (path.parent / review_ref).is_file()):
        raise ValueError(f"{path.name}: missing review evidence")
    integration_ref = data.get("integration_ref")
    if integration_ref is not None:
        workflow_root = path.parent.parent if path.parent.name == "tickets" else path.parent
        try:
            integration_path = (path.parent / integration_ref).resolve(strict=True)
            integration_path.relative_to(workflow_root.resolve())
        except (OSError, ValueError):
            raise ValueError(f"{path.name}: missing integration evidence") from None
        if Path(integration_ref).is_absolute() or not integration_path.is_file():
            raise ValueError(f"{path.name}: missing integration evidence")
        if _read_valid_handoff(
            integration_path,
            stage="integration",
            outcome="integrated",
            ticket_id=data["id"],
        ) is None:
            raise ValueError(f"{path.name}: invalid integration evidence")
        if data["status"] != "ready" or not data["available"]:
            raise ValueError(f"{path.name}: invalid integration lifecycle")
    if data["status"] == "ready" and data["external_blockers"]:
        raise ValueError(f"{path.name}: ready work cannot retain external blockers")
    if bool(data["superseded_by"]) != (data["status"] == "superseded"):
        raise ValueError(f"{path.name}: invalid supersession")
    if data["available"] and data["status"] not in {"implemented", "in_review", "ready"}:
        raise ValueError(f"{path.name}: invalid availability")
    return data


def read_tickets(workflow: Path) -> dict:
    workflow = Path(workflow)
    directory = workflow / "tickets"
    if not directory.is_dir():
        directory = workflow
    result = {}
    for path in sorted(directory.glob("T-*.md")):
        if path.is_symlink() or not path.is_file():
            continue
        data = _parse_ticket(path)
        if data["id"] in result:
            raise ValueError(f"duplicate ticket ID {data['id']}")
        result[data["id"]] = data
    return result


def _revision_count(workflow: Path, ticket_id: str) -> int:
    """Count review decisions that explicitly returned a ticket for revision."""
    directory = Path(workflow) / "reviews" / ticket_id
    if not directory.is_dir() or directory.is_symlink():
        return 0
    count = 0
    for path in sorted(directory.glob("R-[0-9][0-9][0-9].md")):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            heading = path.read_text(encoding="utf-8")[:4096].lower()
        except (OSError, UnicodeDecodeError):
            continue
        if re.search(r"\brevision[ _-]+required\b", heading):
            count += 1
    return count


_TELEMETRY_PATHS = {
    ("type",), ("timestamp",),
    ("payload", "id"), ("payload", "session_id"), ("payload", "agent_path"),
    ("payload", "parent_thread_id"), ("payload", "model"), ("payload", "type"),
    ("payload", "payload", "model_context_window"),
    ("payload", "payload", "info", "model_context_window"),
    ("payload", "payload", "info", "last_token_usage", "input_tokens"),
    *{("payload", "payload", "info", "total_token_usage", field) for field in TOKEN_FIELDS},
    ("payload", "model_context_window"), ("payload", "info", "model_context_window"),
    ("payload", "info", "last_token_usage", "input_tokens"),
    *{("payload", "info", "total_token_usage", field) for field in TOKEN_FIELDS},
}

_CLAUDE_TELEMETRY_PATHS = {
    ("type",), ("sessionId",), ("timestamp",), ("requestId",), ("uuid",),
    ("message", "model"),
    ("message", "usage", "input_tokens"),
    ("message", "usage", "cache_creation_input_tokens"),
    ("message", "usage", "cache_read_input_tokens"),
    ("message", "usage", "output_tokens"),
    ("message", "usage", "thinking_tokens"),
}


class _SelectiveJson:
    """Parse JSON grammar while materializing only allowlisted scalar values."""

    def __init__(self, raw, allowed):
        self.raw, self.allowed, self.index, self.values = raw, allowed, 0, {}

    def _space(self):
        while self.index < len(self.raw) and self.raw[self.index] in b" \t\r\n": self.index += 1

    def _string(self, materialize):
        if self.index >= len(self.raw) or self.raw[self.index] != ord('"'): raise ValueError("invalid JSON string")
        start = self.index; self.index += 1; escaped = False
        while self.index < len(self.raw):
            byte = self.raw[self.index]; self.index += 1
            if escaped:
                escaped = False
            elif byte == ord('\\'):
                escaped = True
            elif byte == ord('"'):
                if materialize:
                    try: return json.loads(self.raw[start:self.index].decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise ValueError("invalid JSON string") from exc
                return None
            elif byte < 0x20:
                raise ValueError("invalid JSON string")
        raise ValueError("unterminated JSON string")

    def _scalar(self):
        self._space(); start = self.index
        if self.index < len(self.raw) and self.raw[self.index] == ord('"'):
            return self._string(True)
        while self.index < len(self.raw) and self.raw[self.index] not in b",]} \t\r\n": self.index += 1
        token = self.raw[start:self.index]
        if token == b"null": return None
        if token == b"true": return True
        if token == b"false": return False
        try: return int(token)
        except ValueError: raise ValueError("invalid JSON scalar")

    def _skip_scalar(self):
        self._space(); start = self.index
        while self.index < len(self.raw) and self.raw[self.index] not in b",]} \t\r\n": self.index += 1
        token = self.raw[start:self.index]
        if token not in {b"null", b"true", b"false"} and not JSON_NUMBER.fullmatch(token):
            raise ValueError("invalid JSON scalar")

    def _skip(self):
        # Untrusted JSON can contain arbitrarily deep arrays/objects. The parser
        # needs only shallow allowlisted telemetry paths, so reject deep input.
        if getattr(self, "_skip_depth", 0) >= 32:
            raise ValueError("JSON nesting exceeds telemetry limit")
        self._skip_depth = getattr(self, "_skip_depth", 0) + 1
        try:
            return self._skip_inner()
        finally:
            self._skip_depth -= 1

    def _skip_inner(self):
        self._space()
        if self.index >= len(self.raw): raise ValueError("truncated JSON")
        byte = self.raw[self.index]
        if byte == ord('"'):
            self._string(False); return
        if byte == ord('{'):
            self.index += 1; self._space()
            if self.index < len(self.raw) and self.raw[self.index] == ord('}'):
                self.index += 1; return
            while True:
                self._space(); self._string(False); self._space()
                if self.index >= len(self.raw) or self.raw[self.index] != ord(':'): raise ValueError("invalid JSON object")
                self.index += 1; self._skip(); self._space()
                if self.index < len(self.raw) and self.raw[self.index] == ord('}'):
                    self.index += 1; return
                if self.index >= len(self.raw) or self.raw[self.index] != ord(','): raise ValueError("invalid JSON object")
                self.index += 1
        if byte == ord('['):
            self.index += 1; self._space()
            if self.index < len(self.raw) and self.raw[self.index] == ord(']'):
                self.index += 1; return
            while True:
                self._skip(); self._space()
                if self.index < len(self.raw) and self.raw[self.index] == ord(']'):
                    self.index += 1; return
                if self.index >= len(self.raw) or self.raw[self.index] != ord(','): raise ValueError("invalid JSON array")
                self.index += 1
        self._skip_scalar()

    def _walk(self, path=()):
        self._space()
        if path in self.allowed:
            self.values[path] = self._scalar(); return
        if not any(candidate[:len(path)] == path for candidate in self.allowed):
            self._skip(); return
        if self.index >= len(self.raw) or self.raw[self.index] != ord('{'):
            self._skip(); return
        self.index += 1; self._space()
        if self.index < len(self.raw) and self.raw[self.index] == ord('}'):
            self.index += 1; return
        while True:
            self._space(); key = self._string(True); self._space()
            if not isinstance(key, str) or self.index >= len(self.raw) or self.raw[self.index] != ord(':'): raise ValueError("invalid JSON object")
            self.index += 1; self._walk(path + (key,)); self._space()
            if self.index < len(self.raw) and self.raw[self.index] == ord('}'):
                self.index += 1; return
            if self.index >= len(self.raw) or self.raw[self.index] != ord(','): raise ValueError("invalid JSON object")
            self.index += 1

    def parse(self):
        self._walk(); self._space()
        if self.index != len(self.raw): raise ValueError("trailing JSON data")
        return self.values


def _fast_json_string_end(raw, index, limit):
    if index >= limit or raw[index] != ord('"'): return None
    index += 1; escaped = False
    while index < limit:
        byte = raw[index]; index += 1
        if escaped: escaped = False
        elif byte == ord('\\'): escaped = True
        elif byte == ord('"'): return index
        elif byte < 0x20: return None
    return None


def _fast_skip_value(raw, index, limit, depth=0):
    if depth > 32: return None
    while index < limit and raw[index] in b" \t\r\n": index += 1
    if index >= limit: return None
    byte = raw[index]
    if byte == ord('"'): return _fast_json_string_end(raw, index, limit)
    if byte in (ord('{'), ord('[')):
        close = ord('}') if byte == ord('{') else ord(']')
        index += 1
        while True:
            while index < limit and raw[index] in b" \t\r\n": index += 1
            if index < limit and raw[index] == close: return index + 1
            if byte == ord('{'):
                index = _fast_json_string_end(raw, index, limit)
                if index is None: return None
                while index < limit and raw[index] in b" \t\r\n": index += 1
                if index >= limit or raw[index] != ord(':'): return None
                index += 1
            index = _fast_skip_value(raw, index, limit, depth + 1)
            if index is None: return None
            while index < limit and raw[index] in b" \t\r\n": index += 1
            if index < limit and raw[index] == close: return index + 1
            if index >= limit or raw[index] != ord(','): return None
            index += 1
    while index < limit and raw[index] not in b",]} \t\r\n": index += 1
    return index if index else None


def _fast_top_level_type(raw, limit=4096):
    """Read only small top-level scalar fields, stopping as soon as ``type`` is known."""
    limit = min(len(raw), limit); index = 0
    while index < limit and raw[index] in b" \t\r\n": index += 1
    if index >= limit or raw[index] != ord('{'): return None
    index += 1
    for _ in range(8):
        while index < limit and raw[index] in b" \t\r\n": index += 1
        start = index; end = _fast_json_string_end(raw, index, limit)
        if end is None: return None
        key = raw[start + 1:end - 1]; index = end
        while index < limit and raw[index] in b" \t\r\n": index += 1
        if index >= limit or raw[index] != ord(':'): return None
        index += 1
        while index < limit and raw[index] in b" \t\r\n": index += 1
        if key == b"type":
            value_start = index; value_end = _fast_json_string_end(raw, index, limit)
            if value_end is None: return None
            try: return raw[value_start + 1:value_end - 1].decode("ascii")
            except UnicodeDecodeError: return None
        index = _fast_skip_value(raw, index, limit)
        if index is None: return None
        while index < limit and raw[index] in b" \t\r\n": index += 1
        if index < limit and raw[index] == ord('}'): return None
        if index >= limit or raw[index] != ord(','): return None
        index += 1
    return None


def _complete_record_bytes(source):
    """Yield bounded complete records; drain oversized records without materializing them."""
    while True:
        raw = source.readline(MAX_SAFE_RECORD_BYTES + 1)
        if not raw: return
        if raw.endswith(b"\n"):
            yield raw, True
            continue
        prefix = raw
        while raw and not raw.endswith(b"\n"):
            raw = source.readline(MAX_SAFE_RECORD_BYTES + 1)
        if not raw: return
        yield prefix, False


class TelemetryParseError(ValueError):
    """A safe, displayable reason that an exact telemetry read failed."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _safe_telemetry_fields(raw, complete):
    if not complete:
        kind = _fast_top_level_type(raw)
        if kind in {"session_meta", "turn_context", "event_msg", None}:
            raise TelemetryParseError("oversized_record")
        return None
    kind = _fast_top_level_type(raw)
    if kind not in {"session_meta", "turn_context", "event_msg"}:
        if kind is not None:
            return None
        try:
            fields = _SelectiveJson(raw, _TELEMETRY_PATHS).parse()
        except (ValueError, RecursionError) as exc:
            raise TelemetryParseError("malformed_telemetry") from exc
        kind = fields.get(("type",))
        if kind not in {"session_meta", "turn_context", "event_msg"}:
            return None
        return fields
    if kind == "event_msg":
        event_match = FAST_EVENT_TYPE.search(raw[:4096])
        event_kind = event_match.group(1).decode("ascii") if event_match else None
        if event_kind not in {"token_count", "token_usage_record", "task_started"}:
            try:
                fields = _SelectiveJson(raw, _TELEMETRY_PATHS).parse()
            except (ValueError, RecursionError) as exc:
                raise TelemetryParseError("malformed_telemetry") from exc
            if fields.get(("payload", "type")) not in {"token_count", "token_usage_record", "task_started"}:
                return None
            return fields
    try:
        return _SelectiveJson(raw, _TELEMETRY_PATHS).parse()
    except (ValueError, RecursionError) as exc:
        raise TelemetryParseError("malformed_telemetry") from exc


def _rollout_id(path):
    match = UUID_SUFFIX.search(path.stem)
    return match.group(1).lower() if match else None


def _complete_totals(value):
    if not isinstance(value, dict) or set(TOKEN_FIELDS) - set(value):
        return None
    result = {}
    for key in TOKEN_FIELDS:
        number = value[key]
        if not isinstance(number, int) or isinstance(number, bool) or number < 0:
            return None
        result[key] = number
    if result["cached_input_tokens"] > result["input_tokens"]:
        return None
    if result["reasoning_output_tokens"] > result["output_tokens"]:
        return None
    if result["total_tokens"] != result["input_tokens"] + result["output_tokens"]:
        return None
    return result


def _context_status(latest, context_window):
    if latest is None: return "unavailable"
    if not isinstance(context_window, int) or isinstance(context_window, bool) or context_window <= 0: return "unavailable"
    occupancy = latest / context_window
    if occupancy >= CRITICAL_CONTEXT_OCCUPANCY: return "critical"
    if occupancy >= WARNING_CONTEXT_OCCUPANCY: return "warning"
    return "normal"


def _empty_telemetry_state():
    return {"meta": None, "current_model": None, "task_window": None,
            "primary_latest": None, "primary_totals": None,
            "primary_archived_totals": None, "primary_reset_allowed": False,
            "fallback_latest": None, "fallback_totals": None,
            "fallback_archived_totals": None, "fallback_reset_allowed": False}


def _sum_totals(left, right):
    if left is None: return copy.deepcopy(right)
    if right is None: return copy.deepcopy(left)
    return {key: left[key] + right[key] for key in TOKEN_FIELDS}


def _consume_telemetry_fields(state, fields):
    kind = fields.get(("type",))
    if kind == "session_meta" and state["meta"] is None:
        identifier = fields.get(("payload", "id"))
        if not isinstance(identifier, str):
            raise TelemetryParseError("malformed_telemetry")
        root_id = fields.get(("payload", "session_id"))
        agent_path = fields.get(("payload", "agent_path"))
        parent_id = fields.get(("payload", "parent_thread_id"))
        state["meta"] = {
            "session_id": identifier,
            "root_session_id": root_id if isinstance(root_id, str) else identifier,
            "agent_path": agent_path if isinstance(agent_path, str) else None,
            "parent_session_id": parent_id if isinstance(parent_id, str) else None,
        }
        return
    if kind == "turn_context":
        candidate = fields.get(("payload", "model"))
        if isinstance(candidate, str):
            state["current_model"] = candidate
        return
    if kind != "event_msg":
        return
    event_kind = fields.get(("payload", "type"))
    if event_kind == "task_started":
        candidate = fields.get(("payload", "payload", "model_context_window"), fields.get(("payload", "model_context_window")))
        if isinstance(candidate, int) and not isinstance(candidate, bool) and candidate > 0:
            state["task_window"] = candidate
        for stream in ("primary", "fallback"):
            state[f"{stream}_reset_allowed"] = True
        return
    if event_kind not in {"token_count", "token_usage_record"}:
        return
    nested = ("payload", "payload", "info")
    direct = ("payload", "info")
    def observed(suffix):
        return fields.get(nested + suffix, fields.get(direct + suffix))
    totals = _complete_totals({field: observed(("total_token_usage", field)) for field in TOKEN_FIELDS})
    latest_input = observed(("last_token_usage", "input_tokens"))
    if totals is None or not isinstance(latest_input, int) or isinstance(latest_input, bool) or latest_input < 0:
        if event_kind == "token_count":
            raise TelemetryParseError("malformed_telemetry")
        return
    stream = "primary" if event_kind == "token_count" else "fallback"
    prior = state[f"{stream}_totals"]
    if prior is not None and any(totals[key] < prior[key] for key in TOKEN_FIELDS):
        if not state[f"{stream}_reset_allowed"]:
            raise TelemetryParseError("malformed_telemetry")
        state[f"{stream}_archived_totals"] = _sum_totals(
            state[f"{stream}_archived_totals"], prior
        )
    state[f"{stream}_reset_allowed"] = False
    window = observed(("model_context_window",))
    if not isinstance(window, int) or isinstance(window, bool) or window <= 0:
        window = state["task_window"]
    observed_at = fields.get(("timestamp",))
    state[f"{stream}_totals"] = totals
    state[f"{stream}_latest"] = {
        "latest_input": latest_input,
        "context_window": window if isinstance(window, int) and window > 0 else None,
        "model": state["current_model"],
        "observed_at": observed_at if isinstance(observed_at, str) else None,
    }


def _telemetry_from_state(state, expected_id):
    meta = state["meta"]
    if meta is None or meta["session_id"].lower() != expected_id:
        raise TelemetryParseError("session_identity_mismatch")
    stream = "primary" if state["primary_latest"] is not None else "fallback"
    latest = state[f"{stream}_latest"]
    totals = _sum_totals(state[f"{stream}_archived_totals"], state[f"{stream}_totals"])
    if latest is None or totals is None:
        raise TelemetryParseError("token_data_not_reported")
    result = {
        **meta,
        "provider": "codex",
        "model": latest["model"],
        "model_observation": "observed" if latest["model"] else None,
        "observed_at": latest["observed_at"],
        "latest_input_tokens": latest["latest_input"],
        "context_window": latest["context_window"],
        "model_context_window": latest["context_window"],
        "context_status": _context_status(latest["latest_input"], latest["context_window"]),
        "totals": totals,
    }
    if result["context_status"] == "unavailable":
        result["unavailable_reason"] = "context_window_not_reported"
    result["context_occupancy"] = latest["latest_input"] / latest["context_window"] if latest["context_window"] else None
    result["total_tokens"] = totals["total_tokens"]
    result["cumulative_tokens"] = totals["total_tokens"]
    return result


def _read_token_telemetry_state(path, start_offset=0, prior_state=None):
    """Parse complete records after ``start_offset`` and return exact state plus offset."""
    path = Path(path)
    try:
        path.lstat()
        if path.is_symlink() or not path.is_file() or path.suffix != ".jsonl":
            return None, prior_state, start_offset, "session_file_missing"
    except OSError:
        return None, prior_state, start_offset, "session_file_missing"
    expected_id = _rollout_id(path)
    if expected_id is None:
        return None, prior_state, start_offset, "session_identity_mismatch"
    state = copy.deepcopy(prior_state) if prior_state is not None else _empty_telemetry_state()
    complete_offset = start_offset
    try:
        with path.open("rb") as source:
            source.seek(start_offset)
            while True:
                record_start = source.tell()
                raw = source.readline(MAX_SAFE_RECORD_BYTES + 1)
                if not raw:
                    break
                if raw.endswith(b"\n"):
                    complete = True
                else:
                    prefix = raw
                    while raw and not raw.endswith(b"\n"):
                        raw = source.readline(MAX_SAFE_RECORD_BYTES + 1)
                    if not raw:
                        break
                    raw, complete = prefix, False
                fields = _safe_telemetry_fields(raw, complete)
                if fields is not None:
                    _consume_telemetry_fields(state, fields)
                complete_offset = source.tell()
    except TelemetryParseError as exc:
        return None, prior_state, start_offset, exc.reason
    except (OSError, ValueError, RecursionError):
        return None, prior_state, start_offset, "telemetry_read_failed"
    try:
        telemetry = _telemetry_from_state(state, expected_id)
    except TelemetryParseError as exc:
        return None, state, complete_offset, exc.reason
    return telemetry, state, complete_offset, None


def read_token_telemetry(path: Path, *, return_state=False):
    """Return only safe rollout identity, ancestry, model, timestamp, and token data."""
    result = _read_token_telemetry_state(path)
    return result if return_state else result[0]


def read_claude_telemetry(path: Path):
    """Return privacy-bounded model and usage evidence from a Claude transcript."""
    path = Path(path)
    try:
        path.lstat()
        if path.is_symlink() or not path.is_file() or path.suffix != ".jsonl":
            return None
    except OSError:
        return None
    expected_id = _rollout_id(path)
    if expected_id is None:
        return None
    requests = {}
    try:
        with path.open("rb") as source:
            for raw, complete in _complete_record_bytes(source):
                if not complete:
                    if _fast_top_level_type(raw) in {"assistant", None}:
                        raise TelemetryParseError("oversized_record")
                    continue
                if _fast_top_level_type(raw) not in {"assistant", None}:
                    continue
                fields = _SelectiveJson(raw, _CLAUDE_TELEMETRY_PATHS).parse()
                if fields.get(("type",)) != "assistant":
                    continue
                session_id = fields.get(("sessionId",))
                if not isinstance(session_id, str) or session_id.lower() != expected_id:
                    raise TelemetryParseError("session_identity_mismatch")
                request_id = fields.get(("requestId",))
                if not isinstance(request_id, str) or not request_id:
                    request_id = fields.get(("uuid",))
                model = fields.get(("message", "model"))
                timestamp = fields.get(("timestamp",))
                if (
                    not isinstance(request_id, str) or not request_id
                    or not isinstance(model, str) or not model.strip()
                    or _parse_time(timestamp) is None
                ):
                    raise TelemetryParseError("malformed_telemetry")
                counters = {}
                for field in (
                    "input_tokens", "cache_creation_input_tokens",
                    "cache_read_input_tokens", "output_tokens", "thinking_tokens",
                ):
                    value = fields.get(("message", "usage", field), 0)
                    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                        raise TelemetryParseError("malformed_telemetry")
                    counters[field] = value
                requests[request_id] = {
                    "model": model,
                    "timestamp": timestamp,
                    "usage": counters,
                }
    except TelemetryParseError:
        raise
    except (OSError, ValueError, RecursionError) as exc:
        raise TelemetryParseError("telemetry_read_failed") from exc
    if not requests:
        return None
    latest = max(requests.values(), key=lambda item: _parse_time(item["timestamp"]))
    totals = {
        "input_tokens": sum(item["usage"]["input_tokens"] for item in requests.values()),
        "cached_input_tokens": sum(
            item["usage"]["cache_creation_input_tokens"]
            + item["usage"]["cache_read_input_tokens"]
            for item in requests.values()
        ),
        "output_tokens": sum(item["usage"]["output_tokens"] for item in requests.values()),
        "reasoning_output_tokens": sum(item["usage"]["thinking_tokens"] for item in requests.values()),
    }
    totals["total_tokens"] = sum(totals.values())
    latest_usage = latest["usage"]
    latest_input = (
        latest_usage["input_tokens"]
        + latest_usage["cache_creation_input_tokens"]
        + latest_usage["cache_read_input_tokens"]
    )
    return {
        "session_id": expected_id,
        "root_session_id": expected_id,
        "agent_path": None,
        "parent_session_id": None,
        "provider": "claude",
        "model": latest["model"],
        "model_observation": "observed",
        "observed_at": latest["timestamp"],
        "latest_input_tokens": latest_input,
        "context_window": None,
        "model_context_window": None,
        "context_occupancy": None,
        "context_status": "unavailable",
        "totals": totals,
        "total_tokens": totals["total_tokens"],
        "cumulative_tokens": totals["total_tokens"],
        "unavailable_reason": "context_window_not_reported",
    }


def _read_progress(workflow):
    directory = Path(workflow) / "progress"
    if directory.is_symlink() or not directory.is_dir(): return []
    records = []
    for path in sorted(directory.glob("*.json")):
        if path.is_symlink() or not path.is_file(): continue
        try: record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError): continue
        if _valid_progress(record, path.name): records.append(record)
    return records


class TelemetryCache:
    """Incremental rollout cache that retains only the last exact observation."""

    def __init__(self):
        self._entries = {}
        self._identities = {}
        self._failures = {}
        self.unavailable_paths = {}
        self.unavailable_sessions = {}
        self._lock = threading.Lock()

    def read(self, path):
        try:
            stat = path.stat()
        except OSError:
            return None
        key = str(path)
        fingerprint = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
        with self._lock:
            entry = self._entries.get(key)
            if entry and entry[0] == fingerprint:
                return entry[1]
        if entry and fingerprint[:2] == entry[0][:2] and stat.st_size >= entry[3]:
            telemetry, state, offset, reason = _read_token_telemetry_state(path, entry[3], entry[2])
        else:
            telemetry, state, offset, reason = read_token_telemetry(path, return_state=True)
        try:
            after = path.stat()
        except OSError:
            with self._lock:
                self._failures[key] = "session_file_missing"
            return None
        after_fingerprint = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        replaced_or_rewritten = (
            after_fingerprint[:2] != fingerprint[:2]
            or after.st_size < stat.st_size
            or (after.st_size == stat.st_size and after.st_mtime_ns != stat.st_mtime_ns)
        )
        if replaced_or_rewritten:
            with self._lock:
                self._failures[key] = "changed_during_read"
            return None
        with self._lock:
            if telemetry is not None:
                self._entries[key] = (fingerprint, telemetry, state, offset)
                self._failures.pop(key, None)
            else:
                self._failures[key] = reason or "telemetry_read_failed"
        return telemetry

    def failure(self, path):
        with self._lock:
            return self._failures.get(str(path))

    def last_exact(self, path):
        with self._lock:
            entry = self._entries.get(str(path))
            return copy.deepcopy(entry[1]) if entry and entry[1] is not None else None

    def prune(self, paths):
        present = {str(path) for path in paths}
        with self._lock:
            for key in set(self._entries) - present:
                del self._entries[key]
            for key in set(self._identities) - present:
                del self._identities[key]
            for key in set(self._failures) - present:
                del self._failures[key]

    def reset_selection(self):
        with self._lock:
            self.unavailable_paths = {}
            self.unavailable_sessions = {}

    def mark_unavailable_path(self, agent_path, reason):
        with self._lock:
            self.unavailable_paths[agent_path] = reason

    def unavailable_path(self, agent_path):
        with self._lock:
            return self.unavailable_paths.get(agent_path)

    def mark_unavailable_session(self, session_id, reason, last_exact=None):
        with self._lock:
            self.unavailable_sessions[session_id] = (reason, copy.deepcopy(last_exact))

    def unavailable_session(self, session_id):
        with self._lock:
            return copy.deepcopy(self.unavailable_sessions.get(session_id))

    def identity(self, path):
        try:
            stat = path.stat()
        except OSError:
            return None
        key = str(path)
        fingerprint = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
        with self._lock:
            entry = self._identities.get(key)
            if entry and entry[0] == fingerprint: return entry[1]
        identity = _read_session_identity(path)
        try:
            after = path.stat()
        except OSError:
            return None
        after_fingerprint = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        replaced_or_rewritten = (
            after_fingerprint[:2] != fingerprint[:2]
            or after.st_size < stat.st_size
            or (after.st_size == stat.st_size and after.st_mtime_ns != stat.st_mtime_ns)
        )
        if replaced_or_rewritten: return None
        with self._lock:
            self._identities[key] = (fingerprint, identity)
        return identity


_IDENTITY_PATHS = {("type",), ("payload", "id"), ("payload", "session_id"), ("payload", "agent_path")}


def _read_session_identity(path):
    try:
        with path.open("rb") as source:
            for raw, complete in _complete_record_bytes(source):
                if not complete: continue
                kind = _fast_top_level_type(raw)
                if kind not in {"session_meta", None}: continue
                if len(raw) > MAX_SAFE_RECORD_BYTES: continue
                fields = _SelectiveJson(raw, _IDENTITY_PATHS).parse()
                if fields.get(("type",)) != "session_meta": continue
                identifier = fields.get(("payload", "id"))
                if not isinstance(identifier, str): return None
                root_id = fields.get(("payload", "session_id"))
                agent_path = fields.get(("payload", "agent_path"))
                return {"session_id": identifier, "root_session_id": root_id if isinstance(root_id, str) else identifier, "agent_path": agent_path if isinstance(agent_path, str) else None}
    except (OSError, ValueError, RecursionError):
        return None
    return None


def _discover_telemetry(roots, cache=None, records=None):
    found = []
    paths = []
    for root in roots:
        root = Path(root)
        if root.is_symlink() or not root.is_dir(): continue
        for path in root.rglob("*.jsonl"):
            if path.is_symlink() or not path.is_file(): continue
            paths.append(path)
    if records is not None:
        selector_cache = cache or TelemetryCache()
        selector_cache.reset_selection()
        explicit_ids = {record["session_id"] for record in records if record.get("session_id")}
        fallback_paths = {record["agent_path"] for record in records if not record.get("session_id")}
        direct = {path for path in paths if _rollout_id(path) in explicit_ids}
        selected = set(direct)
        needs_identity = bool(fallback_paths) or bool(explicit_ids - {_rollout_id(path) for path in direct})
        if needs_identity:
            by_session, by_path = {}, {}
            for path in paths:
                identity = selector_cache.identity(path)
                if not identity: continue
                by_session.setdefault(identity["session_id"], []).append(path)
                if identity["agent_path"]: by_path.setdefault(identity["agent_path"], []).append(path)
            for identifier in explicit_ids:
                candidates = by_session.get(identifier, [])
                if len(candidates) == 1: selected.add(candidates[0])
                elif len(candidates) > 1: selector_cache.mark_unavailable_session(identifier, "ambiguous_session_id")
            for agent_path in fallback_paths:
                candidates = by_path.get(agent_path, [])
                if len(candidates) == 1: selected.add(candidates[0])
                elif len(candidates) > 1: selector_cache.mark_unavailable_path(agent_path, "ambiguous_agent_path")
        selected_ids = {_rollout_id(path) for path in selected}
        for identifier in explicit_ids - selected_ids:
            if selector_cache.unavailable_session(identifier) is None:
                selector_cache.mark_unavailable_session(identifier, "session_file_missing")
        paths_to_read = sorted(selected)
    else:
        paths_to_read = paths
    for path in paths_to_read:
        telemetry = cache.read(path) if cache else read_token_telemetry(path)
        if telemetry:
            found.append(telemetry)
        elif cache:
            reason = cache.failure(path) or "telemetry_read_failed"
            last_exact = cache.last_exact(path)
            identifier = _rollout_id(path)
            if identifier:
                cache.mark_unavailable_session(identifier, reason, last_exact)
            identity = cache.identity(path)
            if records is not None and identity and identity.get("agent_path"):
                cache.mark_unavailable_path(identity["agent_path"], reason)
    if cache: cache.prune(paths)
    return found


def _discover_claude_telemetry(roots, records, selector_cache):
    """Select Claude transcripts only by an explicit progress session ID."""
    explicit_ids = {
        record["session_id"].lower()
        for record in records
        if isinstance(record.get("session_id"), str)
    }
    candidates = {}
    for root in roots:
        root = Path(root)
        if root.is_symlink() or not root.is_dir():
            continue
        for path in root.rglob("*.jsonl"):
            if path.is_symlink() or not path.is_file():
                continue
            identifier = _rollout_id(path)
            if identifier in explicit_ids:
                candidates.setdefault(identifier, []).append(path)
    found = []
    for identifier in explicit_ids:
        paths = candidates.get(identifier, [])
        if len(paths) > 1:
            selector_cache.mark_unavailable_session(identifier, "ambiguous_session_id")
            continue
        if not paths:
            continue
        try:
            telemetry = read_claude_telemetry(paths[0])
        except TelemetryParseError as exc:
            selector_cache.mark_unavailable_session(identifier, exc.reason)
            continue
        if telemetry is not None:
            found.append(telemetry)
    return found


def _unavailable(reason, session_id=None, last_exact=None):
    stale = None
    if last_exact is not None:
        stale = copy.deepcopy(last_exact)
        stale["stale"] = True
    return {"session_id": session_id, "root_session_id": None, "agent_path": None, "parent_session_id": None, "provider": None, "model": None, "model_observation": None, "observed_at": None, "latest_input_tokens": None, "context_window": None, "model_context_window": None, "context_occupancy": None, "context_status": "unavailable", "totals": None, "total_tokens": None, "cumulative_tokens": None, "unavailable_reason": reason, "last_exact_observation": stale}


def _agent_health(record, telemetry, now, stale_after, ticket_active=False):
    progress_at = _parse_time(record["updated_at"])
    heartbeat_at = _parse_time(record.get("heartbeat_at"))
    telemetry_at = _parse_time(telemetry.get("observed_at"))
    observations = [
        value for value in (progress_at, heartbeat_at, telemetry_at)
        if value is not None
    ]
    last_activity = max(observations) if observations else None
    progress_age = (now - progress_at).total_seconds() if progress_at else None
    heartbeat_age = (now - heartbeat_at).total_seconds() if heartbeat_at else None
    telemetry_age = (now - telemetry_at).total_seconds() if telemetry_at else None
    if record.get("blocker"):
        return "blocked", f"Blocked: {record['blocker']}", last_activity
    if _is_terminal(record["state"]):
        if record["state"].lower() == "stopped" and ticket_active:
            return (
                "stopped_unexpectedly",
                "The worker stopped while its ticket is still active.",
                last_activity,
            )
        return "stopped", "The runtime reported a terminal state.", last_activity
    if progress_age is not None and progress_age <= stale_after:
        return "healthy", "Progress was reported within the expected activity window.", last_activity
    if (
        telemetry_age is not None and telemetry_age <= stale_after
        or heartbeat_age is not None and heartbeat_age <= stale_after
    ):
        return (
            "quiet",
            "No recent progress milestone, but runtime activity is still being reported.",
            last_activity,
        )
    return (
        "stale",
        f"No progress or runtime activity was reported within {stale_after} seconds.",
        last_activity,
    )


def _agent_schedule(record, now):
    stage_started = _parse_time(record.get("stage_started_at")) or _parse_time(record["started_at"])
    elapsed = max(0, (now - stage_started).total_seconds())
    expected = record.get("expected_duration_seconds")
    if expected is None:
        return elapsed, "not_estimated", None
    overdue = max(0, elapsed - expected)
    return elapsed, ("overdue" if overdue > 0 else "on_schedule"), overdue


def _is_terminal(state):
    return isinstance(state, str) and state.lower() in TERMINAL_STATES


def _is_reviewer_role(role):
    """Recognize the base reviewer role and documented specialized reviewers."""
    normalized = role.replace("_", "-") if isinstance(role, str) else ""
    return normalized == "reviewer" or normalized.endswith("-reviewer")


def _is_ticket_owner_role(role):
    """Only roles assigned to implement a ticket can create an owner conflict."""
    return role in {"implement", "implementer", "ticket-owner"}


def _is_expected_stage_handoff(record, ticket):
    """Recognize terminal records after the ticket has advanced past their stage."""
    if not ticket or record.get("state", "").lower() not in {"complete", "completed", "stopped"}:
        return False
    status = ticket["status"]
    if _is_ticket_owner_role(record.get("role")):
        return status in {"implemented", "in_review", "revision_required", "ready"}
    if _is_reviewer_role(record.get("role")):
        return status in {"revision_required", "ready"}
    return False


def _newest_unique(records):
    """Return the uniquely latest record by aware progress time, else ``None``."""
    if not records:
        return None
    dated = [(_parse_time(record.get("updated_at")), record) for record in records]
    if any(timestamp is None for timestamp, _record in dated):
        return None
    latest = max(timestamp for timestamp, _record in dated)
    winners = [record for timestamp, record in dated if timestamp == latest]
    return winners[0] if len(winners) == 1 else None


def _latest_record(records):
    """Return a deterministic latest progress record for an aggregate display."""
    return max(records, key=lambda record: (_parse_time(record["updated_at"]), record["agent_path"]))


def _is_current_assignment(record, tickets):
    """Project reservation status without treating progress silence as liveness proof."""
    if _is_terminal(record["state"]):
        return False
    ticket_id = record.get("ticket_id")
    if ticket_id is None or ticket_id not in tickets:
        return True
    return tickets[ticket_id]["status"] not in {"ready", "superseded"}


def build_snapshot(workflow: Path, session_roots: list[Path], now: datetime, stale_after: int, capacity: int | None, telemetry_cache=None, telemetry_override=None, default_unavailable_reason=None, claude_session_roots=None) -> dict:
    workflow = Path(workflow)
    now = now.astimezone(timezone.utc) if now.tzinfo else now.replace(tzinfo=timezone.utc)
    tickets, records = read_tickets(workflow), _read_progress(workflow)
    selector_cache = telemetry_cache or TelemetryCache()
    if telemetry_override is None:
        telemetry = _discover_telemetry(session_roots, selector_cache, records)
        telemetry += _discover_claude_telemetry(
            claude_session_roots or [], records, selector_cache
        )
    else:
        telemetry = telemetry_override
    by_path, by_session = {}, {}
    for item in telemetry:
        if item["agent_path"]: by_path.setdefault(item["agent_path"], []).append(item)
        by_session.setdefault(item["session_id"], []).append(item)
    agents, alerts = [], []
    for record in sorted(records, key=lambda item: item["agent_path"]):
        has_explicit_session = record.get("session_id") is not None
        matches = by_session.get(record.get("session_id"), []) if has_explicit_session else []
        if len(matches) == 1: observation = matches[0]
        elif has_explicit_session and len(matches) > 1: observation = _unavailable("ambiguous_session_id", record["session_id"])
        elif has_explicit_session:
            failure = selector_cache.unavailable_session(record["session_id"])
            reason, last_exact = failure if failure else (default_unavailable_reason or "session_file_missing", None)
            observation = _unavailable(reason, record["session_id"], last_exact)
        else:
            matches = by_path.get(record["agent_path"], [])
            reason = selector_cache.unavailable_path(record["agent_path"])
            observation = _unavailable(reason) if reason else (matches[0] if len(matches) == 1 else _unavailable("ambiguous_agent_path" if matches else (default_unavailable_reason or "not_reported")))
        ticket = tickets.get(record.get("ticket_id"))
        ticket_active = bool(ticket and ticket["status"] not in {"ready", "superseded"})
        stopped_expected = _is_expected_stage_handoff(record, ticket)
        health, health_reason, last_activity = _agent_health(
            record, observation, now, stale_after, ticket_active and not stopped_expected
        )
        elapsed = (now - _parse_time(record["started_at"])).total_seconds()
        stage_elapsed, schedule_status, overdue_seconds = _agent_schedule(record, now)
        current_assignment = _is_current_assignment(record, tickets)
        agent = {
            **{key: record.get(key) for key in REQUIRED_PROGRESS + OPTIONAL_PROGRESS},
            "started_at": record["started_at"],
            "updated_at": record["updated_at"],
            "elapsed_seconds": max(0, elapsed),
            "last_progress_at": record["updated_at"],
            "last_activity_at": last_activity.isoformat() if last_activity else None,
            "health": health,
            "health_reason": health_reason,
            "stage_elapsed_seconds": stage_elapsed,
            "schedule_status": schedule_status,
            "overdue_seconds": overdue_seconds,
            "current_assignment": current_assignment,
            "telemetry": observation,
        }
        agents.append(agent)
    live_coordinators = [agent for agent in agents if agent["role"] == "coordinator" and agent["current_assignment"]]
    selected_coordinator = None
    if len(live_coordinators) == 1:
        selected_coordinator = live_coordinators[0]
        mode = selected_coordinator["state"]
    else:
        mode = "unknown"
        if len(live_coordinators) > 1:
            alerts.append({"kind": "coordinator_conflict", "severity": "coordinator_conflict", "message": "Multiple live coordinators"})
        elif not live_coordinators:
            terminal = _newest_unique([agent for agent in agents if agent["role"] == "coordinator" and _is_terminal(agent["state"])])
            if terminal is not None:
                selected_coordinator = terminal
                mode = terminal["state"]
    if selected_coordinator is not None and _is_terminal(mode):
        # The terminal coordinator record is the authoritative run boundary. Older
        # workers can retain nonterminal heartbeats for audit without consuming
        # capacity or surfacing inactivity warnings after the run has stopped.
        for agent in agents:
            agent["current_assignment"] = False
    for agent in agents:
        if agent.get("blocker") and (agent["current_assignment"] or _is_terminal(agent["state"])):
            alerts.append({"kind": "blocked", "severity": "blocked", "agent_path": agent["agent_path"], "ticket_id": agent.get("ticket_id"), "message": f"{agent['agent_path']}: {agent['blocker']}"})
        elif agent["health"] == "stopped_unexpectedly":
            alerts.append({"kind": "stopped_unexpectedly", "severity": "critical", "agent_path": agent["agent_path"], "ticket_id": agent.get("ticket_id"), "message": f"{agent['agent_path']}: worker stopped while work remains active"})
        elif agent["current_assignment"] and agent["health"] == "stale":
            alerts.append({"kind": agent["health"], "severity": agent["health"], "agent_path": agent["agent_path"], "ticket_id": agent.get("ticket_id"), "message": f"{agent['agent_path']}: {agent['health'].replace('_', ' ')}"})
        if agent["current_assignment"] and agent["schedule_status"] == "overdue":
            alerts.append({"kind": "overdue", "severity": "warning", "agent_path": agent["agent_path"], "ticket_id": agent.get("ticket_id"), "message": f"{agent['agent_path']}: stage is overdue by {round(agent['overdue_seconds'])} seconds"})
    reverse_dependencies = {ticket_id: [] for ticket_id in tickets}
    for candidate_id, candidate in tickets.items():
        for dependency in candidate["blocked_by"]:
            if dependency in reverse_dependencies:
                reverse_dependencies[dependency].append(candidate_id)
    ticket_views = []
    for ticket_id, ticket in sorted(tickets.items()):
        members = [agent for agent in agents if agent.get("ticket_id") == ticket_id]
        ticket_owners = [agent for agent in members if _is_ticket_owner_role(agent["role"])]
        current_members = [agent for agent in members if agent["current_assignment"]]
        live_owners = [agent for agent in ticket_owners if agent["current_assignment"]]
        owner_conflict = len(live_owners) > 1
        owner_label = None
        if len(live_owners) == 1:
            owner = live_owners[0]
        elif owner_conflict:
            owner = None
        elif current_members:
            reviewers = [agent for agent in current_members if _is_reviewer_role(agent["role"])]
            if ticket["status"] == "in_review" and reviewers:
                owner = _latest_record(reviewers)
                if len(reviewers) > 1:
                    owner_label = f"{len(reviewers)} reviewers"
            elif len(current_members) == 1:
                owner = current_members[0]
            else:
                owner = _latest_record(current_members)
        else:
            candidates = [
                agent for agent in (ticket_owners or members)
                if not _is_expected_stage_handoff(agent, ticket)
            ]
            owner = _newest_unique(candidates)
            owner_conflict = bool(candidates) and owner is None
        dependencies = [dependency for dependency in ticket["blocked_by"] if dependency not in tickets or tickets[dependency]["status"] != "ready" or not tickets[dependency]["available"]]
        blocker_members = current_members if current_members else ([owner] if owner and ticket["status"] != "ready" else [])
        blockers = [agent["blocker"] for agent in blocker_members if agent.get("blocker")] + list(ticket["external_blockers"])
        telemetry_complete = bool(members) and all(agent["telemetry"]["totals"] is not None for agent in members)
        totals = {key: sum(agent["telemetry"]["totals"][key] for agent in members) for key in TOKEN_FIELDS} if telemetry_complete else None
        integration_pending = ticket["status"] == "ready" and not ticket["available"]
        integrated = ticket["status"] == "ready" and ticket["available"] and bool(ticket.get("integration_ref"))
        integration_unreported = ticket["status"] == "ready" and ticket["available"] and not ticket.get("integration_ref")
        if integration_pending or integration_unreported:
            owner = selected_coordinator
            owner_label = None
            owner_conflict = False
        elif integrated:
            owner = None
            owner_label = None
            owner_conflict = False
        if blockers:
            ticket_health = "blocked"
        elif owner_conflict:
            ticket_health = "owner_conflict"
        elif integration_pending:
            ticket_health = "integration_pending"
        elif integration_unreported:
            ticket_health = "integration_unreported"
        elif integrated:
            ticket_health = "complete"
        elif dependencies:
            ticket_health = "waiting"
        elif owner is None and ticket["status"] in {"in_progress", "implemented", "in_review", "revision_required"}:
            ticket_health = "not_reported"
        else:
            ticket_health = owner["health"] if owner else "on_track"
        if integrated:
            stage, summary_text, next_action = "integrated", "Reviewed implementation is integrated in the agreed base.", "Await whole-feature verification or downstream work."
        elif integration_unreported:
            stage, summary_text, next_action = "integration_unreported", "Reviewed implementation is marked available, but exact integration evidence is not reported.", "Record the exact integration handoff manifest."
        elif integration_pending:
            stage, summary_text, next_action = "integration_pending", "Reviewed and ready; integration is still pending.", "Integrate the reviewed implementation and mark the ticket available."
        else:
            stage = owner["stage"] if owner else ticket["status"]
            summary_text = f"Waiting on: {', '.join(dependencies)}" if dependencies and owner is None else (owner["summary"] if owner else None)
            next_action = f"Wait for {', '.join(dependencies)} to become available." if dependencies and owner is None else (owner["next_action"] if owner else None)
        projected_owner = owner_label or (
            owner["agent_path"] if owner else (
                ticket.get("assignee")
                if not owner_conflict and ticket["status"] == "in_progress"
                else None
            )
        )
        owner_telemetry = owner["telemetry"] if owner else {}
        direct_unblocks = sorted(reverse_dependencies[ticket_id])
        ready_after_completion = []
        still_waiting_after_completion = []
        for candidate_id in direct_unblocks:
            candidate = tickets[candidate_id]
            remaining = sorted(
                dependency for dependency in candidate["blocked_by"]
                if dependency != ticket_id and (
                    dependency not in tickets
                    or tickets[dependency]["status"] != "ready"
                    or not tickets[dependency]["available"]
                )
            )
            if (
                candidate["status"] == "pending"
                and not remaining
                and not candidate["external_blockers"]
            ):
                ready_after_completion.append(candidate_id)
            elif remaining:
                still_waiting_after_completion.append({
                    "ticket_id": candidate_id,
                    "waiting_on": remaining,
                })
        health_reason = owner["health_reason"] if owner else (
            "No active worker is reporting this ticket stage."
            if ticket_health == "not_reported"
            else None
        )
        ticket_views.append({"id": ticket_id, "title": ticket["title"], "status": ticket["status"], "available": ticket["available"], "integration_ref": ticket.get("integration_ref"), "owner": projected_owner, "owner_conflict": owner_conflict, "stage": stage, "state": owner["state"] if owner else None, "summary": summary_text, "next_action": next_action, "blockers": blockers, "waiting_on": dependencies, "direct_unblocks": direct_unblocks, "ready_after_completion": ready_after_completion, "still_waiting_after_completion": still_waiting_after_completion, "health": ticket_health, "health_reason": health_reason, "updated_at": owner["updated_at"] if owner else None, "last_progress_at": owner["last_progress_at"] if owner else None, "last_activity_at": owner["last_activity_at"] if owner else None, "elapsed_seconds": owner["elapsed_seconds"] if owner else None, "stage_elapsed_seconds": owner["stage_elapsed_seconds"] if owner else None, "expected_duration_seconds": owner.get("expected_duration_seconds") if owner else None, "schedule_status": owner["schedule_status"] if owner else "not_estimated", "overdue_seconds": owner["overdue_seconds"] if owner else None, "runtime_provider": owner.get("runtime_provider") if owner else None, "requested_model": owner.get("requested_model") if owner else None, "observed_provider": owner_telemetry.get("provider"), "observed_model": owner_telemetry.get("model"), "revision_count": _revision_count(workflow, ticket_id), "context_occupancy": owner_telemetry.get("context_occupancy"), "context_tokens": owner_telemetry.get("latest_input_tokens"), "context_window": owner_telemetry.get("context_window"), "telemetry_complete": telemetry_complete, "token_totals": totals, "total_tokens": totals["total_tokens"] if totals is not None else None, "cumulative_tokens": totals["total_tokens"] if totals is not None else None})
    active = [ticket for ticket in ticket_views if ticket["status"] != "superseded"]
    pipeline = round(sum(100 if ticket.get("integration_ref") else GATE_SCORE.get(ticket["status"], 0) for ticket in active) / len(active)) if active else 0
    for ticket in active:
        if ticket["owner_conflict"]:
            alerts.append({"kind": "owner_conflict", "severity": "owner_conflict", "ticket_id": ticket["id"], "message": f"{ticket['id']}: multiple live ticket owners"})
        if ticket["blockers"]:
            blocker_text = "; ".join(ticket["blockers"][:3])
            if len(ticket["blockers"]) > 3: blocker_text += f" (+{len(ticket['blockers']) - 3} more)"
            alerts.append({"kind": "blocked", "severity": "blocked", "ticket_id": ticket["id"], "message": f"{ticket['id']}: {blocker_text}"})
        if ticket["health"] == "integration_unreported":
            alerts.append({"kind": "integration_unreported", "severity": "warning", "ticket_id": ticket["id"], "message": f"{ticket['id']}: available in the agreed base, but exact integration evidence is not reported"})
    telemetry_complete = bool(agents) and all(agent["telemetry"]["totals"] is not None for agent in agents)
    cumulative_totals = {key: sum(agent["telemetry"]["totals"][key] for agent in agents) for key in TOKEN_FIELDS} if telemetry_complete else None
    cumulative = cumulative_totals["total_tokens"] if cumulative_totals else None
    reserved = sum(agent["current_assignment"] for agent in agents)
    all_integrated = bool(active) and all(
        ticket["status"] == "ready" and ticket["available"] and ticket.get("integration_ref")
        for ticket in active
    )
    whole_feature_verified = all_integrated and any(
        agent["role"] == "verifier"
        and agent["stage"] in {"feature_verification", "whole_feature_verification"}
        and agent["state"] == "whole_feature_verified"
        and isinstance(agent.get("handoff_path"), str)
        and _canonical_path(agent["handoff_path"])
        and _read_valid_handoff(
            agent["handoff_path"],
            stage="whole_feature_verification",
            outcome="whole_feature_verified",
        ) is not None
        for agent in agents
    )
    implemented_states = {"implemented", "in_review", "revision_required", "ready"}
    summary = {"active_agents": reserved, "reserved_agents": reserved, "capacity": capacity, "ready": sum(ticket["status"] == "ready" for ticket in active), "active": sum(ticket["status"] in {"in_progress", "implemented", "in_review", "revision_required"} for ticket in active), "attention": len(alerts), "tickets_ready": sum(ticket["status"] == "ready" for ticket in active), "tickets_implemented": sum(ticket["status"] in implemented_states for ticket in active), "tickets_reviewed": sum(ticket["status"] == "ready" for ticket in active), "tickets_available": sum(ticket["available"] for ticket in active), "tickets_integrated": sum(bool(ticket.get("integration_ref")) and ticket["status"] == "ready" and ticket["available"] for ticket in active), "whole_feature_verified": whole_feature_verified, "tickets_active": sum(ticket["status"] in {"in_progress", "in_review"} for ticket in active), "tickets_blocked": sum(bool(ticket["blockers"]) for ticket in active), "pipeline_progress": pipeline, "telemetry_complete": telemetry_complete, "cumulative_token_totals": cumulative_totals, "token_totals": cumulative_totals, "cumulative_tokens": cumulative, "total_tokens": cumulative}
    run = {"workflow": str(workflow), "name": workflow.name.replace("-", " ").title(), "mode": mode, "coordinator_agent_path": selected_coordinator["agent_path"] if selected_coordinator else None}
    return {"generated_at": now.isoformat(), "run": run, "summary": summary, "tickets": ticket_views, "agents": agents, "alerts": alerts, "telemetry_available": bool(telemetry)}


def _default_sessions_root(): return Path.home() / ".codex" / "sessions"


def _default_claude_sessions_root(): return Path.home() / ".claude" / "projects"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest="command", required=True)
    heartbeat = commands.add_parser("heartbeat"); heartbeat.add_argument("workflow", type=Path)
    for name in ("agent_path", "role", "stage", "state", "summary", "next_action"):
        heartbeat.add_argument("--" + name.replace("_", "-"), required=True)
    heartbeat.add_argument("--parent", dest="parent_agent_path", default="/root")
    heartbeat.add_argument("--ticket", dest="ticket_id"); heartbeat.add_argument("--session-id"); heartbeat.add_argument("--blocker"); heartbeat.add_argument("--file-lease"); heartbeat.add_argument("--handoff-path")
    heartbeat.add_argument("--reserved-test-resource", dest="reserved_test_resources", action="append")
    heartbeat.add_argument("--stage-started-at")
    heartbeat.add_argument("--expected-duration-seconds", type=int)
    heartbeat.add_argument("--estimate-set-at")
    heartbeat.add_argument("--estimate-note")
    heartbeat.add_argument("--runtime-provider")
    heartbeat.add_argument("--requested-model")
    pulse = commands.add_parser("pulse"); pulse.add_argument("workflow", type=Path); pulse.add_argument("--agent-path", required=True)
    snapshot = commands.add_parser("snapshot"); snapshot.add_argument("workflow", type=Path); snapshot.add_argument("--sessions-root", type=Path, action="append"); snapshot.add_argument("--claude-sessions-root", type=Path, action="append"); snapshot.add_argument("--capacity", type=int); snapshot.add_argument("--stale-after", type=int, default=600)
    worker = commands.add_parser("snapshot-worker"); worker.add_argument("workflow", type=Path); worker.add_argument("--sessions-root", type=Path, action="append"); worker.add_argument("--claude-sessions-root", type=Path, action="append"); worker.add_argument("--capacity", type=int); worker.add_argument("--stale-after", type=int, default=600)
    serve = commands.add_parser("serve"); serve.add_argument("workflow", type=Path); serve.add_argument("--sessions-root", type=Path, action="append"); serve.add_argument("--claude-sessions-root", type=Path, action="append"); serve.add_argument("--capacity", type=int); serve.add_argument("--host", default="127.0.0.1"); serve.add_argument("--port", type=int, default=0); serve.add_argument("--stale-after", type=int, default=600)
    args = parser.parse_args(argv)
    if args.command == "heartbeat":
        values = vars(args).copy(); workflow = values.pop("workflow"); values.pop("command"); print(write_progress(workflow, values)); return 0
    if args.command == "pulse":
        print(pulse_progress(args.workflow, args.agent_path)); return 0
    roots = args.sessions_root or [_default_sessions_root()]
    claude_roots = args.claude_sessions_root or [_default_claude_sessions_root()]
    if args.command == "snapshot":
        data = build_snapshot(args.workflow, roots, datetime.now(timezone.utc), args.stale_after, args.capacity, claude_session_roots=claude_roots)
        print(json.dumps(data, indent=2, sort_keys=True)); return 0
    if args.command == "snapshot-worker":
        cache = TelemetryCache()
        state_lock, output_lock = threading.Lock(), threading.Lock()
        try:
            initial = build_snapshot(
                args.workflow, roots, datetime.now(timezone.utc), args.stale_after,
                args.capacity, cache, telemetry_override=[],
                default_unavailable_reason="telemetry_refresh_pending",
                claude_session_roots=claude_roots,
            )
        except (OSError, ValueError):
            initial = None
        worker_state = {"snapshot": initial, "refreshing": False}

        def emit(message):
            with output_lock:
                sys.stdout.write(json.dumps(message, separators=(",", ":")) + "\n")
                sys.stdout.flush()

        def refresh_snapshot():
            try:
                data = build_snapshot(args.workflow, roots, datetime.now(timezone.utc), args.stale_after, args.capacity, cache, claude_session_roots=claude_roots)
                with state_lock:
                    worker_state["snapshot"] = data
                    worker_state["refreshing"] = False
                emit({"kind": "update", "ok": True, "snapshot": data, "refreshing": False})
            except (OSError, ValueError):
                with state_lock:
                    worker_state["refreshing"] = False
                emit({"kind": "update", "ok": False, "error": "snapshot_unavailable", "refreshing": False})

        for request in sys.stdin:
            try:
                parsed = json.loads(request)
                request_id = parsed.get("id") if isinstance(parsed, dict) and parsed.get("command") == "snapshot" else None
            except json.JSONDecodeError:
                request_id = None if request.strip() == "snapshot" else False
            if request_id is False:
                continue
            with state_lock:
                if not worker_state["refreshing"]:
                    worker_state["refreshing"] = True
                    start_refresh = True
                else:
                    start_refresh = False
                current = worker_state["snapshot"]
            if current is None:
                emit({"kind": "response", "id": request_id, "ok": False, "error": "snapshot_unavailable", "refreshing": True})
            else:
                emit({"kind": "response", "id": request_id, "ok": True, "snapshot": current, "refreshing": True})
            if start_refresh:
                threading.Thread(target=refresh_snapshot, name="dashboard-telemetry-refresh", daemon=True).start()
        return 0
    server_script = Path(__file__).with_name("dashboard_server.ts")
    command = ["bun", str(server_script), "--workflow", str(args.workflow), "--host", args.host, "--port", str(args.port), "--stale-after", str(args.stale_after)]
    for root in roots:
        command.extend(("--sessions-root", str(root)))
    for root in claude_roots:
        command.extend(("--claude-sessions-root", str(root)))
    if args.capacity is not None:
        command.extend(("--capacity", str(args.capacity)))
    os.execvp(command[0], command)


if __name__ == "__main__": sys.exit(main())
