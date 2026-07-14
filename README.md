# Kudos

Scores each student's contribution to a shared Google Doc: who wrote what, how much of it survived to the final draft, how substantive it was, and how consistently they participated — then emits a contract JSON for a React-based web dashboard and flags anything that needs a teacher's review.

Built and verified end-to-end against offline fixtures in `mock_api/` before any live Google API integration.

## Architecture

The project has evolved from a CLI script into a full-stack application:

* **Backend:** FastAPI (Python) handles the data pipeline and serves the API.
* **Frontend:** React + Vite (TypeScript/Tailwind) provides an interactive teacher dashboard to view reports and trigger new analyses.

### Pipeline Flow

```
React Frontend -> POST /api/analyze -> source -> diff -> classify -> score -> consistency -> flag -> emit -> JSON

```

### Backend Modules

| Module | Responsibility |
| --- | --- |
| `main.py` | FastAPI server. Exposes `GET /api/reports` to list output and `POST /api/analyze` to trigger the pipeline. |
| `sources.py` | `MockSource` reads `mock_api/`; `LiveSource` is a stub for the real Drive APIs. |
| `diff.py` | Word-diffs consecutive revisions, attributes additions to editors, guards against crediting moved text or dead-end deletions. |
| `classify.py` | Rule-based or LLM-based tier classification (`substantive` / `moderate` / `low_effort`) per contribution. |
| `score.py` | Ownership (40%) + Substance (35%) + Consistency (25%) → 0-100 total. |
| `consistency.py` | Coverage of distinct active days across the project window. |
| `flag.py` | Advisory review flags + group summary stats — never alters `total`. |
| `emit.py` | Shapes everything into the contract JSON, writes `output/eval_<run_id>.json`, and persists the run. |

## Setup

You will need two separate terminal windows to run the backend and frontend.

### 1. Backend Setup (Python)

Install dependencies (now including FastAPI and Uvicorn):

```bash
pip install -r requirements.txt

```

*(Optional)* If using the Gemini classifier, copy your API key into a backend `.env` file:

```text
GEMINI_API_KEY=your-key-here

```

### 2. Frontend Setup (React/Vite)

Navigate to your frontend directory and install the Node dependencies:

```bash
npm install

```

Create a `.env` file in the **root of your frontend directory** to point Vite to the Python server:

```text
VITE_API_BASE_URL=http://localhost:8000

```

## Usage

**Terminal 1 (Start the Backend):**

```bash
uvicorn main:app --reload

```

*The API will be available at `http://localhost:8000*`

**Terminal 2 (Start the Frontend):**

```bash
npm run dev

```

*The dashboard will be available at `http://localhost:5173*`

Once the app is running, use the **"+ Run New Analysis"** button in the React dashboard to process mock data or a live Google Doc ID. The generated JSON will automatically be saved to the `output/` folder and rendered on the screen.

## Contract JSON shape

```json
{
  "document": { "id": "", "name": "", "url": "" },
  "run": { "run_id": "", "triggered_by": "", "trigger_type": "", "project_start": "", "project_end": "", "source": "", "generated_at": "" },
  "students": [
    {
      "student_id": "", "name": "", "email": "",
      "scores": { "ownership": 0, "substance": 0, "consistency": 0, "total": 0 },
      "tier_breakdown": { "substantive": 0, "moderate": 0, "low_effort": 0 }, 
      "confidence": 0,
      "flags": [ { "type": "", "evidence": "" } ],
      "evidence": [ { "snippet": "", "timestamp": "", "word_count": 0, "survived": 0, "tier": "", "confidence": 0 } ]
    }
  ],
  "group_summary": { "contribution_equality": 0, "median_total": 0, "needs_review_count": 0 }
}

```

## Notes

* `classify_cache.json`, `output/`, and `runs.db` are generated and gitignored.
* Frontend build artifacts (`node_modules/`, `dist/`) are gitignored.
* `mock_api/` and `roster.json` are fixture/source data, not generated — kept in version control.