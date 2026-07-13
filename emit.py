"""Shape the contribution data into the contract JSON and persist each run."""

import json
import os
import sqlite3
from datetime import datetime, timezone


def load_roster(path: str = "roster.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_contract(roster: dict, student_scores: dict[str, dict], group_summary: dict, run_id: str, source_name: str) -> dict:
    """student_scores: email -> score.score_student() result, with `flags` attached by flag.apply_flags()."""
    students = []
    for student in roster["students"]:
        result = student_scores.get(student["email"])
        students.append(
            {
                "student_id": student["student_id"],
                "name": student["name"],
                "email": student["email"],
                "scores": result["scores"] if result else {"ownership": None, "substance": None, "consistency": None, "total": None},
                "tier_breakdown": result["tier_breakdown"] if result else None,
                "confidence": result["confidence"] if result else None,
                "flags": result.get("flags", []) if result else [],
                "evidence": result["evidence"] if result else [],
            }
        )

    return {
        "document": roster["document"],
        "run": {
            "run_id": run_id,
            "triggered_by": roster["run"]["triggered_by"],
            "trigger_type": roster["run"]["trigger_type"],
            "project_start": roster["run"]["project_start"],
            "project_end": roster["run"]["project_end"],
            "source": source_name,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        },
        "students": students,
        "group_summary": group_summary,
    }


def write_contract(contract: dict, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"eval_{contract['run']['run_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2)
    return path


def persist_run(contract: dict, db_path: str = "runs.db") -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                contract_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT OR REPLACE INTO runs (run_id, document_id, generated_at, contract_json) VALUES (?, ?, ?, ?)",
            (
                contract["run"]["run_id"],
                contract["document"]["id"],
                contract["run"]["generated_at"],
                json.dumps(contract),
            ),
        )
        conn.commit()
    finally:
        conn.close()
