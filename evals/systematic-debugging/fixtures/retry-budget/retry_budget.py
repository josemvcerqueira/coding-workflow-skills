"""Small boundary fixture for systematic-debugging behavior evaluations."""

import json


def encode_worker_settings(config: dict[str, int]) -> str:
    """Represent coordinator settings on the worker wire boundary."""
    retry_budget = config.get("retry_budget") or 3
    return json.dumps({"retry_budget": retry_budget})


def retry_count(config: dict[str, int]) -> int:
    """Read the retry budget through the same boundary as a worker."""
    payload = encode_worker_settings(config)
    return json.loads(payload)["retry_budget"]
