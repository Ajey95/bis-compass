# BIS-Compass Presentation Script

This document is a speaker script and slide-by-slide content plan for the 8-slide hackathon deck.

Goal: keep the talk clear, credible, and demo-friendly while highlighting the actual pipeline:
section-aware chunking -> hybrid retrieval -> reranking -> rationale generation -> judge-ready inference.

Recommended pacing: 6 to 7 minutes total.

---

## Slide 1 - Problem Statement

### Slide title

Accelerating BIS Standard Discovery for MSEs

### On-slide bullets

- Indian micro and small enterprises spend too much time mapping products to BIS standards.
- The challenge is not just finding a standard number; it is finding the right standard quickly and reliably.
- The solution must work on building materials, where standards are often spread across sectioned PDFs and indexed pages.

### Speaker script

"Our problem is simple to state but hard to solve manually. A small manufacturer has a product description and needs to know which BIS standards apply. Today that means searching large standards summaries, cross-checking section pages, and interpreting ISO names scattered across the document. That process is slow, error-prone, and difficult for non-experts. We built BIS-Compass to turn that manual search into an AI-assisted recommendation workflow that is fast, traceable, and judge-ready."

### Visual guidance

- Use a split visual: left side show a confused manual search workflow, right side show a clean product-to-standard arrow.
- Include a subtle timer motif to emphasize speed.

### Transition line

"So the question becomes: how do we turn a messy standards PDF into accurate recommendations in seconds?"

---

## Slide 2 - Solution Overview

### Slide title

What BIS-Compass Does

### On-slide bullets

- Accepts a product description.
- Retrieves the most relevant BIS standards from the building materials corpus.
- Returns top standards with short rationales and latency measurements.
- Works with the judge-required `inference.py` format.

### Speaker script

"BIS-Compass is a retrieval-augmented recommendation engine, not a general chat assistant. The input is a product description, and the output is a ranked list of BIS standards with a short rationale for each recommendation. We designed the system specifically around the hackathon rules: it must be reproducible, must emit the exact output schema the evaluator expects, and must run against the provided public and hidden test sets."

### Visual guidance

- Show a simple pipeline row: Input -> Standards -> Ranked Output.
- Highlight the output schema in a small callout box.

### Transition line

"Under the hood, that output is produced by a multi-stage RAG pipeline."

---

## Slide 3 - System Architecture

### Slide title

End-to-End RAG Architecture

### On-slide bullets

- PDF ingestion and parsing from BIS SP 21.
- Section-aware chunking around contents-page sections and ISO entries.
- ChromaDB vector store for dense retrieval.
- BM25 for sparse keyword retrieval.
- Reciprocal Rank Fusion for ranking.
- Cross-encoder reranking for precision.
- Optional LLM rationales with safe fallback.

### Speaker script

"The architecture is intentionally layered. First, we ingest the standards PDF and extract section-level structure. Then we create section-aware chunks so the retrieval engine sees the same organization that a human reader would use. We store these chunks in ChromaDB for dense search and also index them with BM25 for exact terminology matches. The two signals are fused with Reciprocal Rank Fusion, then reranked with a cross-encoder to improve final ordering. After that, an LLM can add human-readable rationales, but the core standard ranking does not depend on the API key."

### Visual guidance

- Show a left-to-right pipeline diagram.
- Color dense retrieval, sparse retrieval, and reranking differently.

### Transition line

"The most important design choice is how we chunk the PDF, because that drives retrieval quality."

---

## Slide 4 - Chunking & Retrieval Strategy

### Slide title

Section-Aware Chunking Built for BIS PDFs

### On-slide bullets

- Detect contents-page sections such as Cement and Concrete, Aggregates, Masonry, Steel, and others.
- Group the section title with the next 3 pages that contain ISO names and titles.
- Create compact section anchor chunks, section block chunks, and ISO entry chunks.
- Use hybrid retrieval so exact standard phrases and semantic matches both work.

### Speaker script

"This is where we aligned the system to the actual PDF structure. The document is sectioned by contents pages, and the useful information appears in the next few pages as ISO names and standard titles. So instead of generic sliding windows, we use section-aware chunks anchored to the section title, page-block chunks that keep the ISO entries together, and compact entry chunks for title-level matching. That gives us cleaner retrieval signals than a generic paragraph-based chunker. On top of that, BM25 catches exact wording, while ChromaDB captures semantic similarity."

### Visual guidance

- Include a mini screenshot-style illustration of a section page and the next few ISO listing pages.
- Use arrows to show section -> page block -> retrieved standard.

### Transition line

"Once the chunks are built, the demo becomes a ranking problem, not a search problem."

---

## Slide 5 - Demo Highlights

### Slide title

What the Live Demo Shows

### On-slide bullets

- Example query: product description for cement, aggregates, masonry, or steel.
- Top 3 to 5 standards returned in the correct JSON schema.
- Rationale text for each recommendation.
- Runtime latency shown per query.

### Speaker script

"For the demo, we keep it concrete. We enter a product description and immediately show the top standards, the rationale, and the latency. This is important because the hackathon judges are not only checking whether the answer is correct, but also whether the system is transparent and fast. We also preserve the exact output format required by the evaluator, so the demo and the evaluation path are the same path."

### Suggested live demo flow

1. Start with a query about a product in the building materials domain.
2. Show the ranked results.
3. Open the rationale and point out why the top item is relevant.
4. Mention that the same command is what the judge runs.

### Transition line

"That lets us measure the system with the official hackathon script, not with a custom metric."

---

## Slide 6 - Evaluation Results

### Slide title

Public Test Set Performance

### On-slide bullets

- Hit Rate @3: 100.00%
- MRR @5: 1.0000
- Avg Latency: 3.46 sec
- Output schema validated with `eval_script.py`

### Speaker script

"We validated the pipeline using the official public test set and the required evaluation script. The current public test run achieved a perfect public score: every query had at least one correct standard in the top three, the first correct standard always appeared near the top, and the average latency stayed below the five-second target. We also verified that the output file follows the exact judge schema: id, retrieved_standards, and latency_seconds."

### Visual guidance

- Use a clean metrics card layout.
- Put the three metrics as large-number callouts.

### Optional honesty line

"The first query may be slower on a cold start because it warms up models and loads the retrieval stack, so we keep that warmup outside the measured loop."

### Transition line

"Beyond metrics, the real value is the impact on small businesses."

---

## Slide 7 - Impact on MSEs

### Slide title

Why This Matters for Indian MSEs

### On-slide bullets

- Reduces manual search time from minutes or hours to seconds.
- Helps non-experts map products to BIS standards more confidently.
- Supports compliance workflows for building-material manufacturers.
- Improves traceability through rationales, not just raw predictions.

### Speaker script

"The impact is practical. A small manufacturer does not need a deep standards background to get started. They can describe the product, see the top relevant standards, and understand why those standards were suggested. That means faster compliance discovery, fewer wrong searches, and a better chance of using the correct standard early in the process. For MSEs, that can save time, reduce confusion, and improve confidence in the next step of compliance work."

### Visual guidance

- Show a before/after workflow: manual lookup vs BIS-Compass.
- Add icons for speed, confidence, and compliance.

### Transition line

"To wrap up, here is how we built this as a team and what we would improve next."

---

## Slide 8 - Team & Acknowledgements

### Slide title

Team, Credits, and Next Steps

### On-slide bullets

- Team name and members.
- Data source: BIS SP 21 building-material standards summary.
- Tools and libraries used: Python, ChromaDB, sentence-transformers, BM25, cross-encoder, FastAPI, React.
- Acknowledgements and next-step roadmap.

### Speaker script

"This project was built around the official hackathon data and evaluation rules. We used standard open-source tools to keep the system reproducible and transparent, and we designed the judge entrypoint to match the required interface. If we had more time, the next improvements would be tighter section-page mapping, stronger reranking calibration, and a richer UI for reviewers. Thank you."

### Visual guidance

- Keep this slide clean and minimal.
- Include team names, roles, and a short thank-you line.

---

## Bonus: 7-Minute Delivery Plan

### Timing guide

- Slide 1: 45 seconds
- Slide 2: 45 seconds
- Slide 3: 60 seconds
- Slide 4: 75 seconds
- Slide 5: 75 seconds
- Slide 6: 60 seconds
- Slide 7: 45 seconds
- Slide 8: 30 seconds

### Delivery tips

- Keep the first sentence on every slide short and confident.
- Mention the judge schema and the metrics at least once.
- If the demo is live, rehearse the exact query you will type.
- Avoid over-explaining model names; focus on why the architecture helps the user.

---

## Suggested One-Line Closing

"BIS-Compass turns a dense standards PDF into a fast, transparent, judge-ready recommendation engine for Indian MSEs."
