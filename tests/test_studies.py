"""Tests for the studies module, with httpx mocked via respx."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from pytrials import ClinicalTrials, NotFoundError, OverallStatus, Phase

BASE_URL = "https://clinicaltrials.gov/api/v2"


@respx.mock
def test_search_parses_result(search_response: dict[str, Any]) -> None:
    route = respx.get(f"{BASE_URL}/studies").mock(
        return_value=httpx.Response(200, json=search_response)
    )

    ctg = ClinicalTrials()
    result = ctg.studies.search(condition="breast cancer")

    assert route.called
    assert result.total_count == 1234
    assert result.next_page_token == "abc"
    assert len(result.studies) == 1
    assert result.studies[0].nct_id == "NCT04852770"
    assert result.studies[0].brief_title.startswith("A Study of Drug X")
    assert result.studies[0].overall_status is OverallStatus.RECRUITING


@respx.mock
def test_search_maps_query_params(search_response: dict[str, Any]) -> None:
    route = respx.get(f"{BASE_URL}/studies").mock(
        return_value=httpx.Response(200, json=search_response)
    )

    ctg = ClinicalTrials()
    ctg.studies.search(
        condition="breast cancer",
        status=[OverallStatus.RECRUITING],
        phase=Phase.PHASE3,
        page_size=50,
        sort="LastUpdatePostDate:desc",
    )

    request = route.calls.last.request
    params = request.url.params
    assert params["query.cond"] == "breast cancer"
    assert params["filter.overallStatus"] == "RECRUITING"
    assert params["aggFilters"] == "phase:PHASE3"
    assert params["pageSize"] == "50"
    assert params["sort"] == "LastUpdatePostDate:desc"
    assert params["countTotal"] == "true"


@respx.mock
def test_get_parses_study(study_detail: dict[str, Any]) -> None:
    respx.get(f"{BASE_URL}/studies/NCT04852770").mock(
        return_value=httpx.Response(200, json=study_detail)
    )

    ctg = ClinicalTrials()
    study = ctg.studies.get("NCT04852770")

    assert study.nct_id == "NCT04852770"
    assert study.brief_title.startswith("A Study of Drug X")
    assert study.protocol_section is not None
    assert study.protocol_section.design_module is not None
    assert Phase.PHASE3 in study.protocol_section.design_module.phases


@respx.mock
def test_get_missing_raises_not_found() -> None:
    respx.get(f"{BASE_URL}/studies/NCT00000000").mock(
        return_value=httpx.Response(404, json={"message": "Study not found"})
    )

    ctg = ClinicalTrials()
    with pytest.raises(NotFoundError) as excinfo:
        ctg.studies.get("NCT00000000")

    assert excinfo.value.status_code == 404
    assert "not found" in excinfo.value.message.lower()
