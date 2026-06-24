# AGENTS.md

Python SDK for the ClinicalTrials.gov API v2. Full design and roadmap in `PROJECT_PLAN.md`.

## Conventions
- Python 3.10+. Package/deps via `uv`. Build backend: hatch.
- Lint/format: ruff. Types: mypy strict. Tests: pytest + pytest-asyncio, mock httpx with respx.
- Never use em dashes in any output (code, comments, docs, commits). Use periods, commas, colons, or parentheses.
- Never commit secrets (this API needs none; it is public and unauthenticated).

## Core stack (from the plan)
httpx, pydantic v2, tenacity, respx, pytest, ruff, mypy, mkdocs-material, mike, hatch.

## Recommended libraries to speed the build
- **datamodel-code-generator** — generate the Pydantic v2 models directly from the ClinicalTrials.gov OpenAPI 3.0 spec instead of hand-writing the deeply nested hierarchy. Biggest time saver.
- **aiolimiter** — async token-bucket rate limiter (the 50 req/min cap), instead of hand-rolling.
- **hishel** — httpx-native HTTP caching, useful given the rate limit and large study payloads.
- **stamina** — modern retry wrapper over tenacity, cleaner ergonomics (optional; tenacity is fine).
- **Typer** — for the v1.0 CLI (`pytrials search ...`).
- **Polars** for the DataFrame layer (matches the house data stack: DuckDB then Polars, avoid pandas). Offer `.to_polars()` as primary, `.to_pandas()` as a thin convenience.

## Demo / frontend
A live interactive demo (clinical-trial search playground) is the artifact's "live" surface. Best fit: **Marimo** (reactive Python notebook, export to WASM static HTML, deploy to a pyaarproject subdomain). Alternatives: Streamlit or Gradio for a quick search UI, FastHTML for a fuller pure-Python web app.
