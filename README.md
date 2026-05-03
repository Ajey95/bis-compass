# BIS-Compass

AI-powered BIS standards recommendation engine for Indian MSEs.

This repository is structured to satisfy the hackathon submission rules while staying easy for new visitors to run, evaluate, and demo.

## Quick Start

1. Install dependencies.
2. Run ingestion once to build `./chroma_db`.
3. Run `inference.py` on the public test set or your own JSON file.
4. Use `eval_script.py` to validate the output format and metrics.

## What This Project Does

BIS-Compass accepts a product description and returns the most relevant BIS building-material standards with a brief rationale and latency per query.

Example:

Input: `OPC Cement for structural concrete in coastal regions`

Output: ranked standards such as `IS 269:1989`, `IS 1489 (Part 1):1991`, and `IS 456:2000` with short rationales.

## Key Paths

- Judge entrypoint: [`inference.py`](inference.py)
- Public evaluation script: [`eval_script.py`](eval_script.py)
- Main application code: [`src/`](src)
- Ingestion script: [`scripts/ingest.py`](scripts/ingest.py)
- Frontend: [`frontend/`](frontend)
- Presentation script: [`presentation_script.md`](presentation_script.md)
- Optional local setup helper: [`verify_setup.py`](verify_setup.py)

## Architecture

```text
PDF / dataset.pdf
  -> pdf parser
  -> section-aware chunking
  -> ChromaDB + BM25 index
  -> hybrid retrieval + RRF
  -> cross-encoder reranker
  -> optional rationale generation
  -> judge-ready inference output
```

The current implementation is section-aware and hybrid:

- dense retrieval via embeddings and ChromaDB
- sparse retrieval via BM25
- fusion with Reciprocal Rank Fusion
- reranking before output

## Submission Layout

Keep these items in the repository you submit:

- [`inference.py`](inference.py)
- [`eval_script.py`](eval_script.py)
- [`requirements.txt`](requirements.txt)
- [`README.md`](README.md)
- [`src/`](src)
- [`scripts/`](scripts)
- [`frontend/`](frontend) if you are including the UI demo
- `presentation.pdf`

Also keep the data folder or your chosen data path documented clearly:

- [`data/`](data) for public test files or local outputs

Optional local helper files you may keep for your own checks:

- [`verify_setup.py`](verify_setup.py)
- [`presentation_script.md`](presentation_script.md)

The judge will run the root inference entrypoint, so do not rename or move it.

Suggested cleaned submission tree:

```text
bis-compass/
├── inference.py
├── eval_script.py
├── requirements.txt
├── README.md
├── presentation.pdf
├── src/
├── scripts/
├── data/            # public test outputs or local validation files
└── frontend/        # keep only if you want the UI demo included
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Optional: `GROQ_API_KEY` for live rationale generation

### Python Environment

From the repo root:

```powershell
cd d:\projects\buerau\bis-compass
pip install -r requirements.txt
```

### Optional API Key

Create a `.env` file if you want live LLM rationales:

```powershell
copy .env.example .env
```

Then add your `GROQ_API_KEY`. If you do not set it, the pipeline uses a local fallback for rationales.

## Data Setup

Place the BIS SP 21 PDF somewhere accessible and point the ingest script to it.

Common paths:

- `d:\projects\buerau\Bureau of Indian Standards x Sigma Squad AI Hackathon Materials\dataset.pdf`
- or `d:\projects\buerau\bis-compass\data\bis_sp21.pdf` if you copy it there

The data folder for your local test files can be:

- [`data/`](data)

## Ingestion

Run ingestion once to build the vector store:

```powershell
cd d:\projects\buerau\bis-compass
d:/projects/buerau/venv/Scripts/python.exe scripts/ingest.py --pdf "d:\projects\buerau\Bureau of Indian Standards x Sigma Squad AI Hackathon Materials\dataset.pdf"
```

What this does:

- parses the BIS PDF
- deduplicates standards
- creates section-aware chunks
- embeds the chunks
- writes the ChromaDB index to `./chroma_db`

## Running Inference

### Judge command

This is the exact style the judges will use:

```powershell
cd d:\projects\buerau\bis-compass
d:/projects/buerau/venv/Scripts/python.exe inference.py --input "d:\projects\buerau\Bureau of Indian Standards x Sigma Squad AI Hackathon Materials\public_test_set.json" --output team_results.json
```

### Public test validation

```powershell
d:/projects/buerau/venv/Scripts/python.exe eval_script.py --results team_results.json
```

Expected output fields per item:

```json
[
  {
    "id": "PUB-01",
    "retrieved_standards": ["IS 269: 1989", "IS 456: 2000"],
    "latency_seconds": 0.82
  }
]
```

## Frontend Demo

### Start the backend

```powershell
cd d:\projects\buerau\bis-compass
uvicorn src.api:app --reload --port 8000
```

### Start the frontend

```powershell
cd d:\projects\buerau\bis-compass\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Evaluation

The repository includes the mandatory evaluator at [`eval_script.py`](eval_script.py). It checks:

- Hit Rate @3
- MRR @5
- Avg Latency

These are the same metrics used in the public and hidden evaluation flow.

## Important Implementation Notes

- The pipeline uses hybrid retrieval: embeddings + BM25.
- The inference path is judge-safe and writes strict JSON.
- Rationales can be generated with Groq, but the system has a fallback when no API key is set.
- The first query may be slower on a cold start because it warms up the models and index.

## Troubleshooting

### `ModuleNotFoundError`

Run commands from the repo root and make sure dependencies are installed.

### ChromaDB telemetry warnings

Messages like `Failed to send telemetry event ...` are noisy but usually harmless.

### Inference output looks empty

Make sure you have already run ingestion so `./chroma_db` exists.

## Hackathon Checklist

- [`inference.py`](inference.py) is the root entrypoint the judge can call
- [`eval_script.py`](eval_script.py) is present
- output format is strict JSON with `id`, `retrieved_standards`, and `latency_seconds`
- data ingestion and retrieval are documented
- frontend and backend commands are included
- optional API usage is disclosed and not required
- optional local verification helper is kept as a convenience only

## Team and Credits

Built for the BIS × Sigma Squad AI Hackathon.


