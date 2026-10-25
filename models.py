from __future__ import annotations

import hashlib
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import requests


class HFServiceError(Exception):
    pass


def generate_verification_id() -> str:
    suffix = str(uuid.uuid4().int % 100000).zfill(5)
    return f"PL-2026-{suffix}"


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _clamp_score(score: float) -> float:
    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return score


def _extract_ai_probability(raw: Any) -> float:
    entries: list[dict[str, Any]] = []
    if isinstance(raw, list):
        if raw and isinstance(raw[0], list):
            entries = [item for item in raw[0] if isinstance(item, dict)]
        else:
            entries = [item for item in raw if isinstance(item, dict)]
    elif isinstance(raw, dict):
        if "ai_probability" in raw:
            return _clamp_score(float(raw["ai_probability"]))
        if "score" in raw:
            return _clamp_score(float(raw["score"]))

    ai_score: float | None = None
    human_score: float | None = None
    max_score = 0.5

    for item in entries:
        label = str(item.get("label", "")).strip().lower()
        score = float(item.get("score", 0.0))
        max_score = max(max_score, score)

        if any(token in label for token in ("ai", "fake", "generated", "synthetic")):
            ai_score = max(score, ai_score or 0.0)
        if any(token in label for token in ("real", "human", "authentic")):
            human_score = max(score, human_score or 0.0)

    if ai_score is not None:
        return _clamp_score(ai_score)
    if human_score is not None:
        return _clamp_score(1.0 - human_score)
    return _clamp_score(max_score)


def _call_hf_api(
    *,
    endpoint: str,
    hf_token: str,
    payload: bytes | dict[str, Any],
    timeout_seconds: int = 30,
    max_attempts: int = 3,
) -> Any:
    headers = {"Authorization": f"Bearer {hf_token}"}
    if isinstance(payload, bytes):
        headers["Content-Type"] = "application/octet-stream"

    for attempt in range(1, max_attempts + 1):
        try:
            if isinstance(payload, bytes):
                response = requests.post(
                    endpoint,
                    headers=headers,
                    data=payload,
                    timeout=timeout_seconds,
                )
            else:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=timeout_seconds,
                )
        except requests.RequestException as exc:
            if attempt == max_attempts:
                raise HFServiceError(f"Hugging Face request failed: {exc}") from exc
            time.sleep(1.0)
            continue

        if response.status_code == 503:
            wait_seconds = 2.0
            try:
                payload_json = response.json()
                wait_seconds = float(payload_json.get("estimated_time", 2.0))
            except ValueError:
                pass

            if attempt == max_attempts:
                raise HFServiceError("Model is warming up. Please try again shortly.")
            time.sleep(min(max(wait_seconds, 1.0), 8.0))
            continue

        if response.status_code >= 400:
            message = response.text
            try:
                message_json = response.json()
                message = str(message_json)
            except ValueError:
                pass
            raise HFServiceError(f"Hugging Face API error ({response.status_code}): {message}")

        try:
            return response.json()
        except ValueError as exc:
            raise HFServiceError("Hugging Face API returned invalid JSON.") from exc

    raise HFServiceError("Hugging Face API request did not complete.")


def hf_image_score(image_bytes: bytes, hf_token: str, endpoint: str) -> dict[str, Any]:
    raw = _call_hf_api(endpoint=endpoint, hf_token=hf_token, payload=image_bytes)
    ai_probability = _extract_ai_probability(raw)
    return {"ai_probability": ai_probability, "raw_response": raw}


def hf_text_score(text: str, hf_token: str, endpoint: str) -> dict[str, Any]:
    raw = _call_hf_api(endpoint=endpoint, hf_token=hf_token, payload={"inputs": text})
    ai_probability = _extract_ai_probability(raw)
    return {"ai_probability": ai_probability, "raw_response": raw}


def risk_level_from_score(ai_probability: float) -> str:
    if ai_probability >= 0.75:
        return "High"
    if ai_probability >= 0.45:
        return "Medium"
    return "Low"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
