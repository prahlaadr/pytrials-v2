"""pytrials-v2: a modern, fully-typed Python SDK for the ClinicalTrials.gov API v2."""

from __future__ import annotations

from .client import CTGClient
from .errors import CTGError, NotFoundError, RateLimitError
from .models import OverallStatus, Phase, Study, StudySearchResult, StudyType
from .modules.studies import StudiesModule

__version__ = "0.1.0"


class ClinicalTrials:
    """The main entry point for the SDK.

    Exposes module namespaces (currently :attr:`studies`) over a shared HTTP
    client. Async support, the QueryBuilder, pagination, and stats endpoints are
    planned for later releases.

    Example:
        >>> ctg = ClinicalTrials()
        >>> results = ctg.studies.search(condition="breast cancer")
        >>> study = ctg.studies.get("NCT04852770")
    """

    def __init__(
        self,
        base_url: str = "https://clinicaltrials.gov/api/v2",
        timeout: float = 30.0,
        page_size: int = 100,
    ) -> None:
        self._client = CTGClient(
            base_url=base_url,
            timeout=timeout,
            default_page_size=page_size,
        )
        self.studies = StudiesModule(self._client)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> ClinicalTrials:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


__all__ = [
    "CTGClient",
    "CTGError",
    "ClinicalTrials",
    "NotFoundError",
    "OverallStatus",
    "Phase",
    "RateLimitError",
    "StudiesModule",
    "Study",
    "StudySearchResult",
    "StudyType",
    "__version__",
]
