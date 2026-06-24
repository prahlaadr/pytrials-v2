# pytrials-v2

A modern, fully-typed Python SDK for the [ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-api/api).

> Status: early development. See [PROJECT_PLAN.md](./PROJECT_PLAN.md) for the full design and roadmap.

## Why

The ClinicalTrials.gov API v2 (JSON, token pagination, OpenAPI 3.0) launched in 2024, and the old XML v1 API was retired. There is still no well-designed Python SDK for v2. pytrials-v2 aims to be the default: Pydantic-modeled, async-capable, with the ergonomic helpers clinical-trial data consumers actually need.

## What it offers

- Full Pydantic v2 models for every API response (real autocomplete, no dict-digging)
- A validating QueryBuilder that catches bad status, phase, and sort values before the request
- Async auto-pagination over `pageToken`
- DataFrame integration that flattens the nested study structure for analysis
- Date normalization across the API's inconsistent formats
- Built-in rate limiting (50 req/min) and retry with backoff

## Quickstart (planned API)

```python
from pytrials import ClinicalTrials

ctg = ClinicalTrials()

results = ctg.studies.search(condition="breast cancer", status=["RECRUITING"], phase=["PHASE3"])
study = ctg.studies.get("NCT04852770")
df = ctg.studies.search(condition="diabetes", status=["RECRUITING"]).to_dataframe()
```

## Roadmap

- **v0.1.0 Core**: client, search/get, core models, error handling, PyPI publish
- **v0.2.0 Ergonomics**: QueryBuilder, async paginator, stats endpoints, rate limiting
- **v0.3.0 Data science**: DataFrame integration, docs site, 90%+ coverage
- **v1.0.0 Stable**: full results-section models, CLI, notebook examples

## License

MIT
