# BIS-Compass

AI-powered BIS standards recommendation engine for Indian MSEs.

This repository is structured to satisfy the hackathon submission rules while staying easy for new visitors to run, evaluate, and demo.

## Executive Summary

BIS-Compass is a retrieval-augmented recommendation system for BIS standards in the building-material domain. The goal is not to generate standards from scratch, but to retrieve the most relevant standards from the BIS corpus, rank them carefully, and return a judge-safe JSON response with latency information.

The final submission intentionally keeps the implementation simple to inspect and hard to misuse:

- the judge entrypoint stays at the repository root
- the retrieval pipeline is hybrid, combining dense and sparse search
- the reranker improves precision before any rationale generation
- the UI shows the top 3 results first and hides the remaining items behind a click-to-expand control
- the repo includes the dataset PDF and the prebuilt vector store for easy local verification

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

## Key Design Decisions

These are the main implementation choices that shaped the current submission.

### 1. Keep the judge path deterministic and top-level

The judge runs `inference.py` from the repository root. That file first tries the real RAG pipeline and only falls back to the deterministic scorer if the pipeline cannot complete. This avoids a broken submission when a model is unavailable while still using the actual retrieval stack whenever possible.

### 2. Use hybrid retrieval instead of one search method

The retrieval layer combines dense embeddings and BM25. Dense retrieval helps with semantic matching, while BM25 helps catch exact BIS standard language and keyword-heavy queries. The two are fused with Reciprocal Rank Fusion so the final list is less sensitive to any single retrieval weakness.

### 3. Add reranking before generation

The cross-encoder reranker is the precision step. It rescoring the candidate set after retrieval so the final output list is ordered more by query-document fit and less by the coarse first-stage retrieval score.

### 4. Keep rationale generation optional

Groq is used only when an API key is available. If the key is missing or the model cannot be called, the system falls back to local rationales and conservative relevance labels. That keeps the pipeline usable in offline or judge environments.

### 5. Normalize output for the judge

The API and inference output are strict JSON objects with stable field names. This matters more than prose because the evaluation script and judge expect predictable structure, not a chatty explanation.

### 6. Make the UI readable for a demo

The frontend is intentionally presentation-oriented. It shows the top 3 results by default, keeps extra results hidden behind a toggle, and surfaces latency and match strength without exposing confusing internal scoring details.

### 7. Ship the local assets needed for verification

The standalone repo includes `dataset.pdf` and `chroma_db/chroma.sqlite3` so a reviewer can inspect the data setup immediately. That reduces setup friction and avoids a blind first run.

### 8. Keep optional helper files, but label them clearly

Files such as `verify_setup.py` and `presentation_script.md` are useful for local work, but they are not required for the judge. The README keeps that distinction explicit so submission scope stays clear.

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
LAYER 1: Source Ingestion
  [dataset.pdf]
     -> [pdfplumber PDF parser]
     -> [section-aware chunker]
        - header / scope / requirement boundaries
        - section number, section title, page span metadata

LAYER 2: Index Building
  [ChromaDB vector store]
     -> [BAAI/bge-large embeddings]
  [BM25 sparse index]
     -> [rank-bm25]

LAYER 3: Retrieval
  [dense retrieval]      [sparse retrieval]
        \                    /
         -> [Reciprocal Rank Fusion (RRF)]
         -> [cross-encoder reranker]

LAYER 4: Explanation + Output
  [Groq LLM rationale generation]
     -> [strict JSON response]
     -> [FastAPI server / React UI]
```

The current implementation is section-aware and hybrid:

- the BIS PDF is split around section headings and standard entries, so chunks preserve the document's native structure instead of using blind fixed-size windows
- each parsed standard keeps metadata such as section number, section title, start page, and page span, which helps the retriever keep context close to the source
- dense retrieval via embeddings and ChromaDB finds semantically similar standards even when the query wording does not match the BIS text exactly
- sparse retrieval via BM25 catches exact product words, standard names, and legal-style phrases that embeddings may miss
- fusion with Reciprocal Rank Fusion combines both signals so the final candidate list is more stable than either method alone
- reranking before output uses a cross-encoder to score the candidate standards against the query more precisely than the first-stage retriever
- the LLM is used only after retrieval and reranking, mainly to produce a brief rationale and a conservative relevance label for each already-retrieved standard

The layered flow is intentional: the upper layers prepare clean BIS-aware chunks, the middle layers search from two different angles, and the lower layers only explain what has already been retrieved.

### Why the chunking looks section-aware

The BIS source material is organized around section headings and standard entries, so chunking is built around those boundaries instead of arbitrary fixed-length splits. That keeps the retrieval context closer to how the document is actually written and makes exact standards easier to recover.

### Why the repo includes both PDF and vector DB

The PDF is the source of truth. The ChromaDB SQLite file is a convenience artifact so the repo can be opened and verified without immediately re-running ingestion. If you want a fresh index, run ingestion again from the PDF.

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

The following additional files are present in this standalone repo because they improve reproducibility:

- [`dataset.pdf`](dataset.pdf)
- [`chroma_db/chroma.sqlite3`](chroma_db/chroma.sqlite3)

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
cd bis-compass
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

- `dataset.pdf` at the repository root
- or `data/bis_sp21.pdf` if you prefer to keep the source PDF under `data/`

The data folder for your local test files can be:

- [`data/`](data)

Recommended local data files:

- `dataset.pdf` for the BIS source document
- `data/public_test_set.json` for the sample public evaluation input
- `data/test_results.json` for a sample local output file

## Ingestion

Run ingestion once to build the vector store:

```powershell
cd bis-compass
python scripts/ingest.py --pdf dataset.pdf
```

What this does:

- parses the BIS PDF page by page and detects standard boundaries plus section context
- normalizes and deduplicates repeated standards so the same BIS entry is not indexed multiple times
- creates section-aware chunks that include an anchor chunk, a section block chunk, an entry chunk, and a detail chunk for recall support
- embeds the chunks and stores them in ChromaDB so the retriever can search the BIS corpus efficiently
- writes the ChromaDB index to `./chroma_db` and also builds the sparse BM25 side index used during hybrid retrieval

## Running Inference

### Judge command

This is the exact style the judges will use:

```powershell
cd bis-compass
python inference.py --input data/public_test_set.json --output team_results.json
```

### Public test validation

```powershell
python eval_script.py --results team_results.json
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
cd bis-compass
uvicorn src.api:app --reload --port 8000
```

### Start the frontend

```powershell
cd frontend
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

Local validation on the public test set produced the following exact output:

```text
Processing 10 queries...

[✓] PUB-01 | 0.081s | IS 269:1989
[✓] PUB-02 | 0.047s | IS 383:1970
[✓] PUB-03 | 0.936s | IS 458:2003
[✓] PUB-04 | 0.052s | IS 2185 (Part 2):1983
[✓] PUB-05 | 0.062s | IS 459:1992
[✓] PUB-06 | 0.060s | IS 455:1989
[✓] PUB-07 | 0.065s | IS 1489 (Part 2):1991
[✓] PUB-08 | 0.056s | IS 3466:1988
[✓] PUB-09 | 0.543s | IS 6909:1990
[✓] PUB-10 | 0.069s | IS 8042:1989

Total Queries Evaluated : 10
Hit Rate @3             : 100.00%
MRR @5                  : 1.0000
Avg Latency             : 0.20 sec
```

### How this submission maps to the judging criteria

#### Secondary Metrics: Manual + Semi-Auto

The rulebook gives extra weight to how useful the top-3 results look to a human judge and whether the system avoids invented standards.

- **Relevance Score**: The submission is optimized so the top 3 results are the strongest candidates first. Hybrid retrieval and reranking are used to maximize the chance that the visible results are genuinely relevant, while the UI makes the top 3 easy to inspect.
- **No Hallucinations**: The system is built to retrieve from the BIS corpus rather than generate standards from scratch. The prompt and fallback logic are conservative, and the output schema only includes standards that come from the retrieved set. The LLM is only asked to justify retrieved standards, not invent new ones.

#### Subjective Scoring

The repository is also shaped to score well on the manual assessment categories described in the rulebook.

- **Technical Excellence**: The codebase is organized into clear modules for ingestion, retrieval, reranking, generation, API serving, and judge entrypoints. The root inference path is deterministic and reproducible, and the evaluation command is documented.
- **Innovation**: The pipeline uses section-aware chunking, hybrid retrieval, Reciprocal Rank Fusion, and cross-encoder reranking instead of a single retrieval method. The layered architecture makes each step easy to reason about, from PDF parsing through chunking, dual retrieval, fusion, reranking, and final rationale generation, which improves both precision and robustness on BIS-style queries.
- **Usability & Impact**: The frontend is designed as a judge/demo view with top-3 emphasis, hidden extra results, visible latency, and a cleaner presentation of the strongest match.
- **Presentation**: The repository includes `presentation.pdf` and `presentation_script.md` so the final story is easy to demonstrate.

In short, the implementation choices were made to help the submission look strong in both automated metrics and manual review, not just on one of them.

## Important Implementation Notes

- The pipeline uses hybrid retrieval: embeddings + BM25.
- The inference path is judge-safe and writes strict JSON.
- Rationales can be generated with Groq, but the system has a fallback when no API key is set.
- The first query may be slower on a cold start because it warms up the models and index.
- `GROQ_MODEL` can be set in `.env` if you want to override the default Groq model name.
- The frontend metric now reports score-based strong matches instead of relying only on conservative label tags.
- The results panel shows three results by default and exposes the remaining two behind a toggle.
- The retrieval stack is intentionally layered: first-stage search broadens the candidate pool, reranking sharpens the order, and the LLM adds a short explanation after the ranking is already decided.
- The fallback path is there so the judge output still works even if an API key is missing, the model changes, or the external call fails.
- The output remains judge-friendly because the system only returns standards that were retrieved from the BIS corpus, not free-form generated standard numbers.

## Troubleshooting

### `ModuleNotFoundError`

Run commands from the repo root and make sure dependencies are installed.

### ChromaDB telemetry warnings

Messages like `Failed to send telemetry event ...` are noisy but usually harmless.

### Inference output looks empty

Make sure you have already run ingestion so `./chroma_db` exists.

### Groq call fails with a model error

Set `GROQ_MODEL=llama-3.1-8b-instant` in `.env` or keep the default value used by the code. The older Mixtral model name was deprecated.

### High relevance shows as 0 in the UI

The old relevance label was conservative by design. The current UI uses a score-based strong-match count so the demo better reflects retrieval quality.

## Hackathon Checklist

- [`inference.py`](inference.py) is the root entrypoint the judge can call
- [`eval_script.py`](eval_script.py) is present
- output format is strict JSON with `id`, `retrieved_standards`, and `latency_seconds`
- data ingestion and retrieval are documented
- frontend and backend commands are included
- optional API usage is disclosed and not required
- optional local verification helper is kept as a convenience only

## Submission Notes

This repo is meant to be a clean standalone submission, not a loose workspace snapshot. The important practical choices are:

- the source code lives under `src/`, `scripts/`, `frontend/`, and the root entrypoints
- the evaluation script is at the repository root so reviewers can run it directly
- the dataset PDF and vector DB are included for immediate verification
- temporary validation outputs are not required for submission and can be removed if you want a slimmer repo

## Team and Credits

Built for the BIS × Sigma Squad AI Hackathon.
