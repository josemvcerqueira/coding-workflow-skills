#!/usr/bin/env python3
"""Safe progress and telemetry data layer for the local workflow dashboard."""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath

SCHEMA_VERSION = 1
WARNING_INPUT_TOKENS = 160_000
CRITICAL_INPUT_TOKENS = 200_000
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")
TERMINAL_STATES = {"complete", "completed", "stopped"}
REQUIRED_PROGRESS = ("agent_path", "parent_agent_path", "role", "stage", "state", "summary", "next_action")
OPTIONAL_PROGRESS = ("ticket_id", "session_id", "blocker", "file_lease", "reserved_test_resources")
PROGRESS_KEYS = set(REQUIRED_PROGRESS) | set(OPTIONAL_PROGRESS) | {"schema_version", "started_at", "updated_at"}
TICKET_STATUSES = {"pending", "in_progress", "implemented", "in_review", "revision_required", "ready", "superseded"}
GATE_SCORE = {"pending": 0, "in_progress": 25, "implemented": 50, "revision_required": 50, "in_review": 75, "ready": 100}
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
    for key in ("ticket_id", "session_id", "blocker", "file_lease"):
        if key in record and record[key] is not None and (not isinstance(record[key], str) or not record[key].strip()):
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
    for key in ("assignee", "implementation_ref", "review_ref"):
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


def _complete_safe_records(path):
    with path.open("rb") as source:
        for raw, complete in _complete_record_bytes(source):
            if not complete:
                # An oversized event may be a primary token_count in an unfamiliar
                # field order; never permit fallback telemetry past that uncertainty.
                kind = _fast_top_level_type(raw)
                if kind in {"session_meta", "turn_context", "event_msg", None}:
                    raise ValueError("oversized possibly relevant telemetry record")
                continue
            kind = _fast_top_level_type(raw)
            if kind not in {"session_meta", "turn_context", "event_msg"}:
                if kind is not None: continue
                if len(raw) > MAX_SAFE_RECORD_BYTES: continue
                fields = _SelectiveJson(raw, _TELEMETRY_PATHS).parse()
                kind = fields.get(("type",))
                if kind not in {"session_meta", "turn_context", "event_msg"}: continue
                yield fields
                continue
            if kind == "event_msg":
                event_match = FAST_EVENT_TYPE.search(raw[:4096])
                event_kind = event_match.group(1).decode("ascii") if event_match else None
                if event_kind not in {"token_count", "token_usage_record", "task_started"}:
                    if len(raw) > MAX_SAFE_RECORD_BYTES: continue
                    fields = _SelectiveJson(raw, _TELEMETRY_PATHS).parse()
                    if fields.get(("payload", "type")) not in {"token_count", "token_usage_record", "task_started"}: continue
                    yield fields
                    continue
            fields = _SelectiveJson(raw, _TELEMETRY_PATHS).parse()
            yield fields


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


def _lifetime_totals(events):
    if not events:
        return None
    prior = None
    for totals in events:
        if prior is not None:
            if any(totals[key] < prior[key] for key in TOKEN_FIELDS): return None
        prior = totals
    return prior


def _context_status(latest):
    if latest is None: return "unavailable"
    if latest >= CRITICAL_INPUT_TOKENS: return "critical"
    if latest >= WARNING_INPUT_TOKENS: return "warning"
    return "normal"


def read_token_telemetry(path: Path) -> dict | None:
    """Return only safe rollout identity, ancestry, model, timestamp, and token data."""
    path = Path(path)
    try:
        path.lstat()
        if path.is_symlink() or not path.is_file() or path.suffix != ".jsonl": return None
    except OSError:
        return None
    expected_id = _rollout_id(path)
    if expected_id is None: return None
    meta = None; current_model = None; task_window = None; primary = []; fallback = []
    try:
        for fields in _complete_safe_records(path):
            kind = fields.get(("type",))
            if kind == "session_meta" and meta is None:
                identifier = fields.get(("payload", "id"))
                if not isinstance(identifier, str): return None
                session_id = fields.get(("payload", "session_id"))
                agent_path = fields.get(("payload", "agent_path"))
                parent_session_id = fields.get(("payload", "parent_thread_id"))
                meta = {"session_id": identifier, "root_session_id": session_id if isinstance(session_id, str) else identifier, "agent_path": agent_path if isinstance(agent_path, str) else None, "parent_session_id": parent_session_id if isinstance(parent_session_id, str) else None}
            elif kind == "turn_context":
                candidate = fields.get(("payload", "model"))
                if isinstance(candidate, str): current_model = candidate
            elif kind == "event_msg":
                event_kind = fields.get(("payload", "type"))
                if event_kind == "task_started":
                    candidate = fields.get(("payload", "payload", "model_context_window"), fields.get(("payload", "model_context_window")))
                    if isinstance(candidate, int) and candidate > 0: task_window = candidate
                    continue
                if event_kind not in {"token_count", "token_usage_record"}: continue
                nested = ("payload", "payload", "info")
                direct = ("payload", "info")
                def observed(suffix):
                    return fields.get(nested + suffix, fields.get(direct + suffix))
                totals = _complete_totals({field: observed(("total_token_usage", field)) for field in TOKEN_FIELDS})
                if totals is None:
                    if event_kind == "token_count": return None
                    continue
                latest_input = observed(("last_token_usage", "input_tokens"))
                if not isinstance(latest_input, int) or isinstance(latest_input, bool) or latest_input < 0:
                    if event_kind == "token_count": return None
                    continue
                window = observed(("model_context_window",))
                if not isinstance(window, int) or window <= 0: window = task_window
                observed_at = fields.get(("timestamp",))
                event_data = {"totals": totals, "latest_input": latest_input, "context_window": window if isinstance(window, int) and window > 0 else None, "model": current_model, "observed_at": observed_at if isinstance(observed_at, str) else None}
                (primary if event_kind == "token_count" else fallback).append(event_data)
    except (OSError, ValueError, RecursionError):
        return None
    if meta is None or meta["session_id"].lower() != expected_id: return None
    stream = primary if primary else fallback
    if not stream: return None
    latest = stream[-1]
    totals = _lifetime_totals([item["totals"] for item in stream])
    if totals is None: return None
    result = {**meta, "model": latest["model"], "observed_at": latest["observed_at"], "latest_input_tokens": latest["latest_input"], "context_window": latest["context_window"], "model_context_window": latest["context_window"], "context_status": _context_status(latest["latest_input"]), "totals": totals}
    result["context_occupancy"] = latest["latest_input"] / latest["context_window"] if latest["context_window"] else None
    result["total_tokens"] = totals["total_tokens"]
    result["cumulative_tokens"] = totals["total_tokens"]
    return result


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
    """Stat-keyed rollout cache that never returns a value for changed files."""

    def __init__(self):
        self._entries = {}
        self._identities = {}
        self.unavailable_paths = {}
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
        telemetry = read_token_telemetry(path)
        try:
            after = path.stat()
        except OSError:
            return None
        after_fingerprint = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if after_fingerprint != fingerprint:
            return None
        with self._lock:
            self._entries[key] = (fingerprint, telemetry)
        return telemetry

    def prune(self, paths):
        present = {str(path) for path in paths}
        with self._lock:
            for key in set(self._entries) - present:
                del self._entries[key]
            for key in set(self._identities) - present:
                del self._identities[key]

    def reset_selection(self):
        with self._lock:
            self.unavailable_paths = {}

    def mark_unavailable_path(self, agent_path, reason):
        with self._lock:
            self.unavailable_paths[agent_path] = reason

    def unavailable_path(self, agent_path):
        with self._lock:
            return self.unavailable_paths.get(agent_path)

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
        if after_fingerprint != fingerprint: return None
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
            for agent_path in fallback_paths:
                candidates = by_path.get(agent_path, [])
                if len(candidates) == 1: selected.add(candidates[0])
                elif len(candidates) > 1: selector_cache.mark_unavailable_path(agent_path, "ambiguous_agent_path")
        paths_to_read = sorted(selected)
    else:
        paths_to_read = paths
    for path in paths_to_read:
        telemetry = cache.read(path) if cache else read_token_telemetry(path)
        if telemetry: found.append(telemetry)
    if cache: cache.prune(paths)
    return found


def _unavailable(reason):
    return {"session_id": None, "root_session_id": None, "agent_path": None, "parent_session_id": None, "model": None, "observed_at": None, "latest_input_tokens": None, "context_window": None, "model_context_window": None, "context_occupancy": None, "context_status": "unavailable", "totals": None, "total_tokens": None, "cumulative_tokens": None, "unavailable_reason": reason}


def _agent_health(record, telemetry, now, stale_after):
    if record.get("blocker"): return "blocked"
    if _is_terminal(record["state"]): return "complete"
    if telemetry["context_status"] in {"warning", "critical"}: return "context_" + telemetry["context_status"]
    updated = _parse_time(record["updated_at"])
    if updated and (now - updated).total_seconds() > stale_after: return "stale"
    return "on_track"


def _is_terminal(state):
    return isinstance(state, str) and state.lower() in TERMINAL_STATES


def _is_reviewer_role(role):
    """Recognize the base reviewer role and documented specialized reviewers."""
    return isinstance(role, str) and (role == "reviewer" or role.endswith("-reviewer"))


def _is_ticket_owner_role(role):
    """Only roles assigned to implement a ticket can create an owner conflict."""
    return role in {"implementer", "ticket-owner"}


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


def build_snapshot(workflow: Path, session_roots: list[Path], now: datetime, stale_after: int, capacity: int | None, telemetry_cache=None) -> dict:
    workflow = Path(workflow)
    now = now.astimezone(timezone.utc) if now.tzinfo else now.replace(tzinfo=timezone.utc)
    tickets, records = read_tickets(workflow), _read_progress(workflow)
    selector_cache = telemetry_cache or TelemetryCache()
    telemetry = _discover_telemetry(session_roots, selector_cache, records)
    by_path, by_session = {}, {}
    for item in telemetry:
        if item["agent_path"]: by_path.setdefault(item["agent_path"], []).append(item)
        by_session.setdefault(item["session_id"], []).append(item)
    agents, alerts = [], []
    for record in sorted(records, key=lambda item: item["agent_path"]):
        has_explicit_session = record.get("session_id") is not None
        matches = by_session.get(record.get("session_id"), []) if has_explicit_session else []
        if len(matches) == 1: observation = matches[0]
        elif has_explicit_session and len(matches) > 1: observation = _unavailable("ambiguous_session_id")
        elif has_explicit_session: observation = _unavailable("session_id_not_reported")
        else:
            matches = by_path.get(record["agent_path"], [])
            reason = selector_cache.unavailable_path(record["agent_path"])
            observation = _unavailable(reason) if reason else (matches[0] if len(matches) == 1 else _unavailable("ambiguous_agent_path" if matches else "not_reported"))
        health = _agent_health(record, observation, now, stale_after)
        elapsed = (now - _parse_time(record["started_at"])).total_seconds()
        agent = {**{key: record.get(key) for key in REQUIRED_PROGRESS + OPTIONAL_PROGRESS}, "started_at": record["started_at"], "updated_at": record["updated_at"], "elapsed_seconds": max(0, elapsed), "health": health, "telemetry": observation}
        agents.append(agent)
        if health not in {"on_track", "complete"}: alerts.append({"kind": health, "severity": health, "agent_path": record["agent_path"], "ticket_id": record.get("ticket_id"), "message": f"{record['agent_path']}: {health.replace('_', ' ')}"})
    ticket_views = []
    for ticket_id, ticket in sorted(tickets.items()):
        members = [agent for agent in agents if agent.get("ticket_id") == ticket_id]
        ticket_owners = [agent for agent in members if _is_ticket_owner_role(agent["role"])]
        current_members = [agent for agent in members if not _is_terminal(agent["state"])]
        live_owners = [agent for agent in ticket_owners if not _is_terminal(agent["state"])]
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
            candidates = ticket_owners or members
            owner = _newest_unique(candidates)
            owner_conflict = bool(candidates) and owner is None
        dependencies = [dependency for dependency in ticket["blocked_by"] if dependency not in tickets or tickets[dependency]["status"] != "ready" or not tickets[dependency]["available"]]
        blocker_members = current_members if current_members else ([owner] if owner else [])
        blockers = [agent["blocker"] for agent in blocker_members if agent.get("blocker")] + list(ticket["external_blockers"]) + dependencies
        telemetry_complete = bool(members) and all(agent["telemetry"]["totals"] is not None for agent in members)
        totals = {key: sum(agent["telemetry"]["totals"][key] for agent in members) for key in TOKEN_FIELDS} if telemetry_complete else None
        ticket_health = "blocked" if blockers else ("owner_conflict" if owner_conflict else (owner["health"] if owner else "on_track"))
        ticket_views.append({"id": ticket_id, "title": ticket["title"], "status": ticket["status"], "owner": owner_label or (owner["agent_path"] if owner else (None if owner_conflict else ticket.get("assignee"))), "owner_conflict": owner_conflict, "stage": owner["stage"] if owner else None, "state": owner["state"] if owner else None, "summary": owner["summary"] if owner else None, "next_action": owner["next_action"] if owner else None, "blockers": blockers, "health": ticket_health, "updated_at": owner["updated_at"] if owner else None, "elapsed_seconds": owner["elapsed_seconds"] if owner else None, "telemetry_complete": telemetry_complete, "token_totals": totals, "total_tokens": totals["total_tokens"] if totals is not None else None, "cumulative_tokens": totals["total_tokens"] if totals is not None else None})
    active = [ticket for ticket in ticket_views if ticket["status"] != "superseded"]
    pipeline = round(sum(GATE_SCORE.get(ticket["status"], 0) for ticket in active) / len(active)) if active else 0
    for ticket in active:
        if ticket["owner_conflict"]:
            alerts.append({"kind": "owner_conflict", "severity": "owner_conflict", "ticket_id": ticket["id"], "message": f"{ticket['id']}: multiple live ticket owners"})
        if ticket["blockers"]:
            blocker_text = "; ".join(ticket["blockers"][:3])
            if len(ticket["blockers"]) > 3: blocker_text += f" (+{len(ticket['blockers']) - 3} more)"
            alerts.append({"kind": "blocked", "severity": "blocked", "ticket_id": ticket["id"], "message": f"{ticket['id']}: {blocker_text}"})
    live_coordinators = [record for record in records if record["role"] == "coordinator" and not _is_terminal(record["state"])]
    if len(live_coordinators) == 1:
        mode = live_coordinators[0]["state"]
    else:
        mode = "unknown"
        if len(live_coordinators) > 1:
            alerts.append({"kind": "coordinator_conflict", "severity": "coordinator_conflict", "message": "Multiple live coordinators"})
        elif not live_coordinators:
            terminal = _newest_unique([record for record in records if record["role"] == "coordinator" and _is_terminal(record["state"])])
            if terminal is not None:
                mode = terminal["state"]
    telemetry_complete = bool(agents) and all(agent["telemetry"]["totals"] is not None for agent in agents)
    cumulative_totals = {key: sum(agent["telemetry"]["totals"][key] for agent in agents) for key in TOKEN_FIELDS} if telemetry_complete else None
    cumulative = cumulative_totals["total_tokens"] if cumulative_totals else None
    reserved = sum(not _is_terminal(agent["state"]) for agent in agents)
    summary = {"active_agents": reserved, "reserved_agents": reserved, "capacity": capacity, "ready": sum(ticket["status"] == "ready" for ticket in active), "active": sum(ticket["status"] in {"in_progress", "implemented", "in_review", "revision_required"} for ticket in active), "attention": len(alerts), "tickets_ready": sum(ticket["status"] == "ready" for ticket in active), "tickets_active": sum(ticket["status"] in {"in_progress", "in_review"} for ticket in active), "tickets_blocked": sum(bool(ticket["blockers"]) for ticket in active), "pipeline_progress": pipeline, "telemetry_complete": telemetry_complete, "cumulative_token_totals": cumulative_totals, "token_totals": cumulative_totals, "cumulative_tokens": cumulative, "total_tokens": cumulative}
    return {"generated_at": now.isoformat(), "run": {"workflow": str(workflow), "mode": mode}, "summary": summary, "tickets": ticket_views, "agents": agents, "alerts": alerts, "telemetry_available": bool(telemetry)}


def _default_sessions_root(): return Path.home() / ".codex" / "sessions"


class _DashboardServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def make_server(workflow: Path, session_roots: list[Path], capacity: int | None,
                host: str, port: int, stale_after: int) -> ThreadingHTTPServer:
    """Build a loopback-only, read-only dashboard server."""
    if host != "127.0.0.1":
        raise ValueError("dashboard host must be 127.0.0.1")
    if not isinstance(port, int) or isinstance(port, bool) or not 0 <= port <= 65535:
        raise ValueError("dashboard port must be between 0 and 65535")
    if capacity is not None and (not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1):
        raise ValueError("capacity must be a positive integer")
    if not isinstance(stale_after, int) or isinstance(stale_after, bool) or stale_after < 1:
        raise ValueError("stale_after must be a positive integer")

    workflow = Path(workflow)
    roots = tuple(Path(root) for root in session_roots)
    asset_path = Path(__file__).resolve().parent.parent / "assets" / "dashboard.html"
    asset = asset_path.read_bytes()
    telemetry_cache = TelemetryCache()

    class Handler(BaseHTTPRequestHandler):
        server_version = "WorkflowDashboard/1"

        def log_message(self, _format, *_args):
            return

        def _headers(self, status, content_type, length):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:")
            self.end_headers()

        def _send(self, status, content_type, body):
            self._headers(status, content_type, len(body))
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                self._send(200, "text/html; charset=utf-8", asset)
                return
            if self.path == "/health":
                self._send(200, "text/plain; charset=utf-8", b"ok\n")
                return
            if self.path == "/api/status":
                try:
                    snapshot = build_snapshot(
                        workflow,
                        list(roots),
                        datetime.now(timezone.utc),
                        stale_after,
                        capacity,
                        telemetry_cache,
                    )
                    body = json.dumps(snapshot, separators=(",", ":")).encode("utf-8")
                except (OSError, ValueError):
                    self._send(500, "application/json", b'{"error":"snapshot_unavailable"}')
                    return
                self._send(200, "application/json", body)
                return
            self.send_error(404)

        def _reject_mutation(self):
            self.send_error(405)

        do_POST = _reject_mutation
        do_PUT = _reject_mutation
        do_PATCH = _reject_mutation
        do_DELETE = _reject_mutation

    return _DashboardServer((host, port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest="command", required=True)
    heartbeat = commands.add_parser("heartbeat"); heartbeat.add_argument("workflow", type=Path)
    for name in ("agent_path", "role", "stage", "state", "summary", "next_action"):
        heartbeat.add_argument("--" + name.replace("_", "-"), required=True)
    heartbeat.add_argument("--parent", dest="parent_agent_path", default="/root")
    heartbeat.add_argument("--ticket", dest="ticket_id"); heartbeat.add_argument("--session-id"); heartbeat.add_argument("--blocker"); heartbeat.add_argument("--file-lease")
    heartbeat.add_argument("--reserved-test-resource", dest="reserved_test_resources", action="append")
    snapshot = commands.add_parser("snapshot"); snapshot.add_argument("workflow", type=Path); snapshot.add_argument("--sessions-root", type=Path, action="append"); snapshot.add_argument("--capacity", type=int)
    serve = commands.add_parser("serve"); serve.add_argument("workflow", type=Path); serve.add_argument("--sessions-root", type=Path, action="append"); serve.add_argument("--capacity", type=int); serve.add_argument("--host", default="127.0.0.1"); serve.add_argument("--port", type=int, default=0)
    args = parser.parse_args(argv)
    if args.command == "heartbeat":
        values = vars(args).copy(); workflow = values.pop("workflow"); values.pop("command"); print(write_progress(workflow, values)); return 0
    data = build_snapshot(args.workflow, args.sessions_root or [_default_sessions_root()], datetime.now(timezone.utc), 600, args.capacity)
    if args.command == "snapshot": print(json.dumps(data, indent=2, sort_keys=True)); return 0
    server = make_server(args.workflow, args.sessions_root or [_default_sessions_root()], args.capacity, args.host, args.port, 600)
    host, port = server.server_address
    print(json.dumps({"url": f"http://{host}:{port}", "pid": os.getpid(), "host": host, "port": port}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__": sys.exit(main())
