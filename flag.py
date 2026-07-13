"""Review flags + group-level summary. Flags are advisory annotations attached with evidence — they never alter `total`."""

import statistics
from datetime import date, datetime, timedelta

LOW_CONFIDENCE_THRESHOLD = 0.7
GRADE_BOUNDARIES = [60, 70, 80, 90]
GRADE_BOUNDARY_TOLERANCE = 3
FAR_BELOW_GROUP_RATIO = 0.6

# "activity concentrated at deadline": most of an editor's revisions landing in
# the final slice of the project window, from the ground-truth Devon case in
# BUILD_WITH_MOCKS.md (his edits sit on 06-09/13/14, the back third).
LATE_WINDOW_FRACTION = 0.15
LATE_WINDOW_MIN_SHARE = 0.5
LATE_WINDOW_MIN_EVENTS = 2


def _parse_date(timestamp: str) -> date:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date()


def _gini(values: list[float]) -> float:
    n = len(values)
    if n == 0 or sum(values) == 0:
        return 0.0
    ordered = sorted(values)
    weighted_sum = sum((i + 1) * x for i, x in enumerate(ordered))
    return (2 * weighted_sum) / (n * sum(ordered)) - (n + 1) / n


def _low_confidence_flag(result: dict) -> dict | None:
    confidence = result["confidence"]
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        return {
            "type": "low model confidence",
            "evidence": f"average classification confidence {confidence:.2f} is below {LOW_CONFIDENCE_THRESHOLD:.2f}",
        }
    return None


def _near_grade_boundary_flag(result: dict) -> dict | None:
    total = result["scores"]["total"]
    for boundary in GRADE_BOUNDARIES:
        if abs(total - boundary) <= GRADE_BOUNDARY_TOLERANCE:
            return {
                "type": "near grade boundary",
                "evidence": f"total {total:.1f} is within {GRADE_BOUNDARY_TOLERANCE} points of the {boundary} boundary",
            }
    return None


def _far_below_group_flag(result: dict, median_total: float) -> dict | None:
    total = result["scores"]["total"]
    if median_total > 0 and total < FAR_BELOW_GROUP_RATIO * median_total:
        return {
            "type": "contribution far below group",
            "evidence": f"total {total:.1f} is {total / median_total:.0%} of the group median {median_total:.1f}",
        }
    return None


def _activity_concentrated_at_deadline_flag(email: str, revisions: list[dict], start: str, end: str) -> dict | None:
    window_start, window_end = _parse_date(start), _parse_date(end)
    window_days = (window_end - window_start).days + 1
    if window_days <= 0:
        return None

    late_span = max(1, round(window_days * LATE_WINDOW_FRACTION))
    late_cutoff = window_end - timedelta(days=late_span - 1)

    editor_events = [_parse_date(rev["modifiedTime"]) for rev in revisions if rev["editor_email"] == email]
    if len(editor_events) < LATE_WINDOW_MIN_EVENTS:
        return None

    late_events = [d for d in editor_events if d >= late_cutoff]
    share = len(late_events) / len(editor_events)
    if share >= LATE_WINDOW_MIN_SHARE:
        return {
            "type": "activity concentrated at deadline",
            "evidence": (
                f"{len(late_events)} of {len(editor_events)} edits fell in the final {late_span} day(s) "
                f"of the project window ({late_cutoff.isoformat()}–{window_end.isoformat()})"
            ),
        }
    return None


def flag_student(email: str, result: dict, revisions: list[dict], start: str, end: str, median_total: float) -> list[dict]:
    checks = [
        _low_confidence_flag(result),
        _near_grade_boundary_flag(result),
        _far_below_group_flag(result, median_total),
        _activity_concentrated_at_deadline_flag(email, revisions, start, end),
    ]
    return [flag for flag in checks if flag is not None]


def apply_flags(student_scores: dict[str, dict], revisions: list[dict], start: str, end: str) -> dict:
    """Attaches `flags` to each entry in student_scores (in place) and returns group_summary."""
    totals = [result["scores"]["total"] for result in student_scores.values()]
    median_total = statistics.median(totals) if totals else 0.0
    ownership_shares = [result["scores"]["ownership"] for result in student_scores.values()]

    needs_review_count = 0
    for email, result in student_scores.items():
        flags = flag_student(email, result, revisions, start, end, median_total)
        result["flags"] = flags
        if flags:
            needs_review_count += 1

    return {
        "contribution_equality": round(1 - _gini(ownership_shares), 4) if ownership_shares else None,
        "median_total": round(median_total, 1),
        "needs_review_count": needs_review_count,
    }
