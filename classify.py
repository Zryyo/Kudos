"""Classify each contribution's substance tier via the Gemini API, JSON-only, cached per contribution."""

import hashlib
import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
CACHE_PATH = "classify_cache.json"
TIERS = {"substantive", "moderate", "low_effort"}

PROMPT_TEMPLATE = """Classify this snippet of a student's contribution to a group document into exactly one tier:

- substantive: original analysis, reasoning, or well-developed content specific to the topic
- moderate: reasonable content, but thin, generic, or mostly restating existing points
- low_effort: filler, formatting-only, one-liners, or rambling with little substance

Respond with ONLY a JSON object, nothing else:
{{"tier": "substantive" | "moderate" | "low_effort", "confidence": <float 0-1>}}

Text:
\"\"\"
{text}
\"\"\"
"""

_cache: dict[str, dict] | None = None


def _load_cache() -> dict:
    global _cache
    if _cache is None:
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                _cache = json.load(f)
        else:
            _cache = {}
    return _cache


def _save_cache() -> None:
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(_cache, f, indent=2)


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_response(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"No JSON object found in model response: {raw!r}")
        parsed = json.loads(cleaned[start : end + 1])

    tier = parsed.get("tier")
    if tier not in TIERS:
        raise ValueError(f"Invalid tier in model response: {tier!r}")

    try:
        confidence = float(parsed.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    return {"tier": tier, "confidence": confidence}


def llm_classify(text: str, client: "genai.Client | None" = None) -> dict:
    """{tier, confidence} for a contribution's added_text, cached on disk by content hash."""
    cache = _load_cache()
    key = _cache_key(text)
    if key in cache:
        return cache[key]

    client = client or genai.Client()
    response = client.models.generate_content(
        model=MODEL,
        contents=PROMPT_TEMPLATE.format(text=text),
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    result = _parse_response(response.text)

    cache[key] = result
    _save_cache()
    return result
