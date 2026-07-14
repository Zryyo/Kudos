import json
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your existing pipeline modules
from consistency import consistency_scores
from diff import _load_revisions_with_text, attribute_contributions
from emit import build_contract, load_roster, persist_run, write_contract
from flag import apply_flags
from score import score_all
from sources import LiveSource, MockSource

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = Path("output")

# --- DATA MODELS ---
class AnalysisRequest(BaseModel):
    source: str = "mock"
    document_id: str | None = None
    roster: str = "roster.json"

# --- EXISTING GET ENDPOINT ---
@app.get("/api/reports")
async def get_reports():
    reports_data = []
    if OUTPUT_DIR.exists() and OUTPUT_DIR.is_dir():
        for file_path in OUTPUT_DIR.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    reports_data.append(data)
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")
    return reports_data

# --- NEW POST ENDPOINT (The Pipeline) ---
@app.post("/api/analyze")
async def run_analysis(req: AnalysisRequest):
    try:
        # 1. Validate & Build Source
        if req.source == "live" and not req.document_id:
            raise HTTPException(status_code=400, detail="document_id is required when source is live")
            
        source = MockSource() if req.source == "mock" else LiveSource(document_id=req.document_id)

        # 2. Run Pipeline
        revisions = _load_revisions_with_text(source)
        contributions = attribute_contributions(revisions)

        roster = load_roster(req.roster)
        
        consistency = consistency_scores(
            roster["students"], revisions, roster["run"]["project_start"], roster["run"]["project_end"]
        )
        
        student_scores = score_all(roster["students"], contributions, consistency)
        
        group_summary = apply_flags(
            student_scores, revisions, roster["run"]["project_start"], roster["run"]["project_end"]
        )
        
        run_id = uuid.uuid4().hex[:8]
        
        contract = build_contract(roster, student_scores, group_summary, run_id, req.source)

        # 3. Save & Return
        write_contract(contract)
        persist_run(contract)
        
        # Return the generated JSON directly to the frontend so it can display it instantly
        return contract

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))