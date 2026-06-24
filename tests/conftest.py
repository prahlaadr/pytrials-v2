"""Shared test fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

BASE_URL = "https://clinicaltrials.gov/api/v2"


def _load(name: str) -> dict[str, Any]:
    with (FIXTURES / name).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
    return data


@pytest.fixture
def search_response() -> dict[str, Any]:
    return _load("search_response.json")


@pytest.fixture
def study_detail() -> dict[str, Any]:
    return _load("study_detail.json")
