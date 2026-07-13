"""Rubric scoring: Ownership (40%) + Substance (35%) + Consistency (25%) -> 0-100 total."""

from classify import llm_classify

TIER_WEIGHTS = {"substantive": 1.0, "moderate": 0.5, "low_effort": 0.1}
WEIGHTS = {"ownership": 0.40, "substance": 0.35, "consistency": 0.25}
EVIDENCE_SNIPPET_MAX_CHARS = 120


def _snippet(text: str) -> str:
    if len(text) <= EVIDENCE_SNIPPET_MAX_CHARS:
        return text
    return text[: EVIDENCE_SNIPPET_MAX_CHARS - 1] + "…"


def _ownership(student_contributions: list[dict], all_contributions: list[dict]) -> float:
    """Share of the group's total surviving words that this student contributed."""
    total_surviving = sum(c["word_count"] * c["survived"] for c in all_contributions)
    if total_surviving == 0:
        return 0.0
    student_surviving = sum(c["word_count"] * c["survived"] for c in student_contributions)
    return student_surviving / total_surviving


def score_student(student_contributions: list[dict], all_contributions: list[dict], consistency: float) -> dict:
    """consistency: 0-1, supplied by consistency.py (Step 5) — pass 0.0 until that's wired in."""
    tier_breakdown = {"substantive": 0, "moderate": 0, "low_effort": 0}
    weighted_tier_sum = 0.0
    weighted_confidence_sum = 0.0
    total_words = 0
    evidence = []

    for c in student_contributions:
        classification = llm_classify(c["added_text"])
        tier, confidence = classification["tier"], classification["confidence"]

        tier_breakdown[tier] += c["word_count"]
        weighted_tier_sum += TIER_WEIGHTS[tier] * c["word_count"]
        weighted_confidence_sum += confidence * c["word_count"]
        total_words += c["word_count"]

        evidence.append(
            {
                "snippet": _snippet(c["added_text"]),
                "timestamp": c["timestamp"],
                "word_count": c["word_count"],
                "survived": c["survived"],
                "tier": tier,
                "confidence": confidence,
            }
        )

    ownership = _ownership(student_contributions, all_contributions)
    substance = weighted_tier_sum / total_words if total_words else 0.0
    confidence = weighted_confidence_sum / total_words if total_words else 0.0
    total = 100 * (WEIGHTS["ownership"] * ownership + WEIGHTS["substance"] * substance + WEIGHTS["consistency"] * consistency)

    return {
        "scores": {
            "ownership": round(ownership, 4),
            "substance": round(substance, 4),
            "consistency": round(consistency, 4),
            "total": round(total, 1),
        },
        "tier_breakdown": tier_breakdown,
        "confidence": round(confidence, 4),
        "evidence": evidence,
    }


def score_all(students: list[dict], contributions: list[dict], consistency_scores: dict[str, float] | None = None) -> dict[str, dict]:
    """students: roster['students']. consistency_scores: email -> 0-1, defaults to 0.0 (Step 5 fills this in)."""
    consistency_scores = consistency_scores or {}

    contributions_by_email: dict[str, list[dict]] = {}
    for c in contributions:
        contributions_by_email.setdefault(c["editor_email"], []).append(c)

    return {
        student["email"]: score_student(
            contributions_by_email.get(student["email"], []),
            contributions,
            consistency_scores.get(student["email"], 0.0),
        )
        for student in students
    }
