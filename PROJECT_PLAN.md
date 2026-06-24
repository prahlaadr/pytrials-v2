# pytrials-v2: ClinicalTrials.gov API v2 Python SDK

## Project overview

A modern, fully-typed Python SDK for the ClinicalTrials.gov API v2. No authentication required (public API). The goal is to become the default Python library for anyone working with clinical trial data programmatically.

**Package name:** `pytrials-v2`
**PyPI:** `pip install pytrials-v2`
**GitHub:** `github.com/raami/pytrials-v2`
**License:** MIT
**Python:** 3.10+

---

## Why this exists

The ClinicalTrials.gov API v2 launched in March 2024 as a complete rewrite: JSON responses, token-based pagination, OpenAPI 3.0 spec, enumerated values instead of free text. The old v1 API (XML-based) was retired in June 2024. There is currently no proper Python SDK for v2. What exists:

- `pytrials` on PyPI: partially updated for v2, minimal type coverage, no async, no pagination helper, no query builder
- `clinical-trials-api` on npm: JavaScript, toy-level
- MCP servers (cyanheads, etc.): designed for LLM tool use, not developer integration
- Raw `requests.get()` examples in blog posts

The gap: a well-designed, Pydantic-modeled, async-capable Python SDK with ergonomic helpers for the patterns that clinical trial data consumers actually need.

---

## ClinicalTrials.gov API v2 endpoints

Base URL: `https://clinicaltrials.gov/api/v2`

| Endpoint | Method | Description |
|---|---|---|
| `/studies` | GET | Search studies with query params and filters |
| `/studies/{nctId}` | GET | Get full study record by NCT ID |
| `/stats/size` | GET | Get total study count for a query |
| `/stats/fieldValues` | GET | Get valid values for a field with counts |
| `/stats/listFields` | GET | Browse the study data model field tree |
| `/version` | GET | API version and data timestamp |
| `/studies/metadata` | GET | Study data structure metadata |

**No auth required.** Rate limit is approximately 50 requests per minute per IP.

---

## SDK architecture

### Layer 1: Public API surface

```python
from pytrials import ClinicalTrials

ctg = ClinicalTrials()

# Search studies
results = ctg.studies.search(
    condition="breast cancer",
    status=["RECRUITING"],
    phase=["PHASE3"],
    page_size=100,
    sort="LastUpdatePostDate:desc"
)

# Get single study
study = ctg.studies.get("NCT04852770")

# Count studies matching a query
count = ctg.stats.size(condition="diabetes", status=["RECRUITING"])

# Get valid values for a field
phases = ctg.stats.field_values("OverallStatus")

# API version info
version = ctg.version()
```

#### Module namespaces

**ctg.studies**
- `search(**kwargs)` -- search with query params, returns `StudySearchResult`
- `get(nct_id)` -- fetch single study, returns `Study`
- `search_all(**kwargs)` -- async generator, auto-paginates through all results
- `bulk_get(nct_ids: list)` -- fetch multiple studies by NCT ID list

**ctg.stats**
- `size(**kwargs)` -- total count for a query, returns `int`
- `field_values(field, **kwargs)` -- enum values with counts, returns `list[FieldValue]`
- `list_fields(parent=None)` -- browse study data model tree

**ctg.metadata**
- `fields()` -- available fields for field selection
- `search_areas()` -- valid search area definitions

**ctg.version**
- `__call__()` -- returns `VersionInfo` with api_version and data_timestamp

### Layer 2: QueryBuilder (fluent interface)

```python
from pytrials import ClinicalTrials, Query

ctg = ClinicalTrials()

# Fluent query construction
query = (
    Query()
    .condition("non-small cell lung cancer")
    .intervention("pembrolizumab")
    .sponsor("Merck")
    .location("United States")
    .status("RECRUITING", "NOT_YET_RECRUITING")
    .phase("PHASE3")
    .sort("LastUpdatePostDate:desc")
)

results = ctg.studies.search(query, page_size=50)
```

The `Query` object validates enum values at construction time (status, phase) and raises `InvalidQueryError` before hitting the API.

### Layer 3: Pydantic v2 models

Every API response is a validated Pydantic model. The study data structure is deeply nested, so models mirror the hierarchy:

```
Study
  protocolSection
    identificationModule (nctId, briefTitle, officialTitle, organization)
    statusModule (overallStatus, startDateStruct, completionDateStruct)
    sponsorCollaboratorsModule (leadSponsor, collaborators)
    descriptionModule (briefSummary, detailedDescription)
    conditionsModule (conditions, keywords)
    designModule (studyType, phases, enrollmentInfo, designInfo)
    armsInterventionsModule (armGroups, interventions)
    outcomesModule (primaryOutcomes, secondaryOutcomes)
    eligibilityModule (criteria, healthyVolunteers, sex, minimumAge, maximumAge)
    contactsLocationsModule (overallOfficials, locations)
    referencesModule (references, seeAlsoLinks)
  derivedSection
    miscInfoModule
    conditionBrowseModule (meshTerms)
    interventionBrowseModule (meshTerms)
  resultsSection (when hasResults=True)
    participantFlowModule
    baselineCharacteristicsModule
    outcomeMeasuresModule
    adverseEventsModule
  hasResults: bool
```

Key design decisions:
- All fields are `Optional` with sensible defaults (the API has many nullable fields)
- Date fields use a custom `CTGDate` type that handles the inconsistent formats ("2024-01-15", "January 2024", "January 15, 2024")
- Enum fields (status, phase, study type) are Python enums with validation
- `model_config = ConfigDict(extra="allow")` so new API fields don't break the SDK

### Layer 4: Core HTTP client

```python
# Internal, not public API
class CTGClient:
    base_url = "https://clinicaltrials.gov/api/v2"
    
    # httpx async client with:
    # - Automatic retry with exponential backoff (tenacity)
    # - Rate limiting (50 req/min token bucket)
    # - Configurable timeout (default 30s)
    # - Response validation via Pydantic
    # - Structured CTGError on 4xx/5xx
```

### Layer 5: Pagination

```python
# Auto-paginate through all results
async for study in ctg.studies.search_all(condition="cancer"):
    process(study)

# Or collect all at once (careful with large result sets)
all_studies = await ctg.studies.search_all(
    condition="cancer", 
    status=["COMPLETED"]
).collect()
```

The paginator handles `pageToken` transparently, respects rate limits between pages, and yields `Study` objects one at a time via async generator.

### Layer 6: pandas integration

```python
# Direct DataFrame output
df = ctg.studies.search(
    condition="diabetes",
    status=["RECRUITING"],
    page_size=100
).to_dataframe()

# Flattened columns: nct_id, brief_title, overall_status, 
# lead_sponsor, phase, enrollment, start_date, ...
```

The `.to_dataframe()` method flattens the nested study structure into a tabular format suitable for analysis. Users can specify which fields to include.

---

## Project structure

```
pytrials-v2/
  src/
    pytrials/
      __init__.py          # ClinicalTrials client, Query, enums
      client.py            # CTGClient (httpx, retry, rate limit)
      models/
        __init__.py
        study.py           # Study, ProtocolSection, etc.
        search.py          # StudySearchResult, pagination
        stats.py           # FieldValue, VersionInfo
        enums.py           # OverallStatus, Phase, StudyType
        dates.py           # CTGDate custom type
      modules/
        __init__.py
        studies.py         # StudiesModule (search, get, search_all)
        stats.py           # StatsModule (size, field_values)
        metadata.py        # MetadataModule (fields, search_areas)
      query.py             # QueryBuilder fluent interface
      pagination.py        # AsyncPaginator generator
      errors.py            # CTGError, RateLimitError, NotFoundError
      pandas_ext.py        # .to_dataframe() integration
  tests/
    conftest.py            # respx fixtures, sample responses
    test_client.py
    test_studies.py
    test_stats.py
    test_query.py
    test_pagination.py
    test_models.py
    fixtures/
      search_response.json
      study_detail.json
      stats_size.json
  docs/
    index.md
    quickstart.md
    api-reference/
      studies.md
      stats.md
      query-builder.md
      models.md
    guides/
      pagination.md
      pandas-integration.md
      common-patterns.md   # Competitive intel, site selection, patient matching
  pyproject.toml
  README.md
  LICENSE
  CHANGELOG.md
  .github/
    workflows/
      ci.yml               # pytest, mypy, ruff, coverage
      publish.yml           # PyPI publish on tag
```

---

## Tech stack

| Tool | Purpose |
|---|---|
| httpx | Async HTTP client (better than requests for async) |
| pydantic v2 | Response validation and type safety |
| tenacity | Retry with exponential backoff |
| respx | Mock httpx in tests |
| pytest + pytest-asyncio | Test framework |
| ruff | Linting and formatting |
| mypy (strict) | Static type checking |
| mkdocs-material | Documentation site |
| mike | Docs versioning |
| hatch | Build backend and environment management |

---

## Release roadmap

### v0.1.0: Core (weeks 1-2)

Ship a working SDK that covers the basic use cases.

- [ ] `ClinicalTrials` client class with httpx
- [ ] `ctg.studies.search()` with all query params
- [ ] `ctg.studies.get()` single study by NCT ID
- [ ] Pydantic models for Study, ProtocolSection, and key submodules
- [ ] Enum types for OverallStatus, Phase, StudyType
- [ ] Basic error handling (CTGError with status_code, message)
- [ ] pytest suite with respx mocking
- [ ] README with quickstart
- [ ] PyPI publish via GitHub Actions

### v0.2.0: Ergonomics (weeks 3-4)

Make the SDK pleasant to use for real workflows.

- [ ] QueryBuilder fluent interface with validation
- [ ] AsyncPaginator (async generator for search_all)
- [ ] `ctg.stats.size()` and `ctg.stats.field_values()`
- [ ] `ctg.version()` endpoint
- [ ] Retry with exponential backoff (tenacity)
- [ ] Rate limiter (token bucket, 50 req/min)
- [ ] CTGDate custom type for inconsistent date formats
- [ ] `bulk_get()` for multiple NCT IDs

### v0.3.0: Data science (weeks 5-6)

Make it useful for analysts and researchers.

- [ ] `.to_dataframe()` pandas integration
- [ ] CSV export option (format=csv passthrough)
- [ ] `ctg.metadata.fields()` and `search_areas()`
- [ ] mkdocs-material documentation site
- [ ] "Common patterns" guide (competitive intel, site selection, patient matching)
- [ ] mypy strict mode passing
- [ ] 90%+ test coverage

### v1.0.0: Stable (week 8+)

- [ ] Full model coverage for resultsSection (outcomes, adverse events, participant flow)
- [ ] CLI tool (`pytrials search --condition "diabetes" --status RECRUITING`)
- [ ] Jupyter notebook examples
- [ ] Docs site deployed (GitHub Pages or Vercel)
- [ ] Community feedback incorporated

---

## Competitive differentiation

What this SDK does that nothing else offers:

1. **Full Pydantic models.** Every field in the API response is typed. IDE autocomplete works everywhere. `study.protocol_section.eligibility_module.minimum_age` not `study["protocolSection"]["eligibilityModule"]["minimumAge"]`.

2. **QueryBuilder with validation.** Catches invalid status values, phase values, and sort options before the request is sent. No more 400 errors from typos.

3. **Auto-pagination.** `async for study in ctg.studies.search_all(...)` handles pageToken transparently. Nobody should write a pagination loop manually.

4. **pandas-native.** `.to_dataframe()` flattens the deeply nested study structure into analysis-ready columns. This is what 80% of users actually want.

5. **Date normalization.** The API returns dates in at least three formats. The SDK normalizes them into Python `date` objects.

6. **Rate limit awareness.** Built-in token bucket respects the 50 req/min limit. No more 429 errors during bulk operations.

7. **Domain expertise in the API design.** Search patterns (condition + intervention + sponsor + location + status + phase) are first-class, not afterthoughts. The QueryBuilder reflects how regulatory professionals, CROs, and biotech analysts actually query this data.

---

## Example use cases to document

### Competitive intelligence
Search what trials a specific sponsor is running, filter by phase and status, export to DataFrame for analysis.

### Clinical site selection
Find facilities running trials for a condition in a geography. The locations data in contactsLocationsModule is rich enough for this.

### Patient matching
Search recruiting trials by condition, location, age range, and healthy volunteer status. This is the patient-facing use case.

### Regulatory landscape
Count trials by phase and status for a therapeutic area. Use stats endpoints for aggregate views.

### Drug pipeline tracking
Track all trials for a specific intervention across phases. Use sort by last update to catch new filings.

---

## Marketing and distribution

- PyPI package with clear README
- Blog post on dev.to or Medium: "Building the Python SDK ClinicalTrials.gov should have shipped"
- Post in r/bioinformatics, r/clinicalresearch, r/Python
- LinkedIn post (leveraging your existing healthcare audience)
- Submit to awesome-python and awesome-healthcare lists
- Present at OOP Data Camp (you're already going)
- Cross-reference from OpenTrialGraph

---

## Key API quirks to handle

1. **Date inconsistency.** Some dates are "2024-01-15", others "January 2024", others "January 15, 2024". The SDK should normalize to `datetime.date` or a `CTGDate` that preserves precision (year-only vs. full date).

2. **Nullable arrays.** conditions, interventions, locations, collaborators can all be null or empty arrays. Models must handle both.

3. **Large responses.** A single study with results can be 200KB+ of JSON. The resultsSection (outcomes, adverse events, participant flow, baseline) is massive. Consider lazy loading or optional field selection.

4. **pageSize default is 10.** Most users want more. The SDK should default to 100 or let users set a client-level default.

5. **Enumerated values are case-sensitive.** RECRUITING works, recruiting doesn't. The SDK should handle case normalization.

6. **CSV format returns flat columns.** The JSON and CSV response schemas are different. The SDK should abstract this.
