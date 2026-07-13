# Kudos

Scores each student's contribution to a shared Google Doc: who wrote what, how
much of it survived to the final draft, how substantive it was, and how
consistently they participated — then emits a contract JSON for a dashboard
and flags anything that needs a teacher's review.

Built and verified end-to-end against offline fixtures in `mock_api/` before
any live Google API integration.

## How it works

```
source (mock or live) -> diff -> classify -> score -> consistency -> flag -> emit
```

| Module | Responsibility |
|---|---|
| `sources.py` | `MockSource` reads `mock_api/`; `LiveSource` is a stub for the real Drive APIs |
| `diff.py` | Word-diffs consecutive revisions, attributes additions to editors, guards against crediting moved text or dead-end deletions |
| `classify.py` | Gemini-based tier classification (`substantive` / `moderate` / `low_effort`) per contribution, disk-cached |
| `score.py` | Ownership (40%) + Substance (35%) + Consistency (25%) → 0-100 total |
| `consistency.py` | Coverage of distinct active days across the project window |
| `flag.py` | Advisory review flags + group summary stats — never alters `total` |
| `emit.py` | Shapes everything into the contract JSON, writes `output/eval_<run_id>.json`, persists the run to SQLite |
| `main.py` | Wires the pipeline together and picks the source |

## Setup

```
pip install -r requirements.txt
```

Copy your Gemini API key into `.env`:

```
GEMINI_API_KEY=your-key-here
```

Get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

## Usage

```
python main.py --source mock
```

Writes `output/eval_<run_id>.json` and appends a row to `runs.db`.

`--source live --document-id <id>` will run the pipeline against a real
Google Doc once `LiveSource` is filled in (not yet implemented).

## Contract JSON shape

```
{
  "document": { "id", "name", "url" },
  "run": { "run_id", "triggered_by", "trigger_type", "project_start", "project_end", "source", "generated_at" },
  "students": [
    {
      "student_id", "name", "email",
      "scores": { "ownership", "substance", "consistency", "total" },
      "tier_breakdown": { "substantive", "moderate", "low_effort" },  // words per tier
      "confidence",
      "flags": [ { "type", "evidence" } ],
      "evidence": [ { "snippet", "timestamp", "word_count", "survived", "tier", "confidence" } ]
    }
  ],
  "group_summary": { "contribution_equality", "median_total", "needs_review_count" }
}
```

## Notes

- `classify_cache.json`, `output/`, and `runs.db` are generated and gitignored.
- `mock_api/` and `roster.json` are fixture/source data, not generated — kept in version control.
