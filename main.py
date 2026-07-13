"""Entry point: source -> diff -> (placeholder scores) -> contract JSON."""

import argparse
import uuid

from consistency import consistency_scores
from diff import _load_revisions_with_text, attribute_contributions
from emit import build_contract, load_roster, persist_run, write_contract
from flag import apply_flags
from score import score_all
from sources import LiveSource, MockSource


def build_source(args: argparse.Namespace):
    if args.source == "mock":
        return MockSource()
    return LiveSource(document_id=args.document_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["mock", "live"], default="mock")
    parser.add_argument("--document-id", default=None, help="Google Doc id (required for --source live)")
    parser.add_argument("--roster", default="roster.json")
    args = parser.parse_args()

    if args.source == "live" and not args.document_id:
        parser.error("--document-id is required when --source live")

    source = build_source(args)

    revisions = _load_revisions_with_text(source)
    contributions = attribute_contributions(revisions)

    roster = load_roster(args.roster)
    consistency = consistency_scores(
        roster["students"], revisions, roster["run"]["project_start"], roster["run"]["project_end"]
    )
    student_scores = score_all(roster["students"], contributions, consistency)
    group_summary = apply_flags(
        student_scores, revisions, roster["run"]["project_start"], roster["run"]["project_end"]
    )
    run_id = uuid.uuid4().hex[:8]
    contract = build_contract(roster, student_scores, group_summary, run_id, args.source)

    path = write_contract(contract)
    persist_run(contract)
    print(f"Wrote {path} ({len(contributions)} contributions across {len(revisions)} revisions)")


if __name__ == "__main__":
    main()
