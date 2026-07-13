"""Consistency: coverage of distinct active days across the project window, from revision timestamps."""

from datetime import date, datetime


def _parse_date(timestamp: str) -> date:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date()


def _active_days(editor_email: str, revisions: list[dict], activity: list[dict] | None) -> set[date]:
    days = {_parse_date(rev["modifiedTime"]) for rev in revisions if rev["editor_email"] == editor_email}
    if activity:
        # Optional enrichment path (off by default): the mock/live Activity API can surface
        # edit events revisions.list doesn't (e.g. edits folded into a later merged revision).
        days |= {_parse_date(event["timestamp"]) for event in activity if event.get("actor_email") == editor_email}
    return days


def timeline_spread_score(
    editor_email: str,
    revisions: list[dict],
    start: str,
    end: str,
    activity: list[dict] | None = None,
) -> float:
    """Coverage of distinct active days across the project window [start, end], 0-1."""
    window_start, window_end = _parse_date(start), _parse_date(end)
    window_days = (window_end - window_start).days + 1
    if window_days <= 0:
        return 0.0

    days_in_window = {
        d for d in _active_days(editor_email, revisions, activity) if window_start <= d <= window_end
    }
    return min(1.0, len(days_in_window) / window_days)


def consistency_scores(
    students: list[dict],
    revisions: list[dict],
    start: str,
    end: str,
    source=None,
    use_activity_enrichment: bool = False,
) -> dict[str, float]:
    """email -> timeline_spread_score. Pass source + use_activity_enrichment=True to also mine drive_activity.json."""
    activity = source.get_activity() if (use_activity_enrichment and source is not None) else None
    return {
        student["email"]: timeline_spread_score(student["email"], revisions, start, end, activity)
        for student in students
    }


if __name__ == "__main__":
    from diff import _load_revisions_with_text
    from emit import load_roster
    from sources import MockSource

    source = MockSource()
    revisions = _load_revisions_with_text(source)
    roster = load_roster()
    start, end = roster["run"]["project_start"], roster["run"]["project_end"]

    for student in roster["students"]:
        days = sorted(
            d.isoformat() for d in _active_days(student["email"], revisions, None)
        )
        score = timeline_spread_score(student["email"], revisions, start, end)
        print(f"{student['email']:<22} active_days={days}  spread={score:.3f}")
