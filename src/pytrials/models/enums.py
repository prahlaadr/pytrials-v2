"""Enumerated values from the ClinicalTrials.gov API v2 data model.

These mirror the real, case sensitive values the API accepts and returns.
"""

from __future__ import annotations

from enum import Enum


class OverallStatus(str, Enum):
    """Recruitment status of a study (statusModule.overallStatus)."""

    ACTIVE_NOT_RECRUITING = "ACTIVE_NOT_RECRUITING"
    COMPLETED = "COMPLETED"
    ENROLLING_BY_INVITATION = "ENROLLING_BY_INVITATION"
    NOT_YET_RECRUITING = "NOT_YET_RECRUITING"
    RECRUITING = "RECRUITING"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    WITHDRAWN = "WITHDRAWN"
    AVAILABLE = "AVAILABLE"
    NO_LONGER_AVAILABLE = "NO_LONGER_AVAILABLE"
    TEMPORARILY_NOT_AVAILABLE = "TEMPORARILY_NOT_AVAILABLE"
    APPROVED_FOR_MARKETING = "APPROVED_FOR_MARKETING"
    WITHHELD = "WITHHELD"
    UNKNOWN = "UNKNOWN"


class Phase(str, Enum):
    """Clinical trial phase (designModule.phases)."""

    NA = "NA"
    EARLY_PHASE1 = "EARLY_PHASE1"
    PHASE1 = "PHASE1"
    PHASE2 = "PHASE2"
    PHASE3 = "PHASE3"
    PHASE4 = "PHASE4"


class StudyType(str, Enum):
    """Type of study (designModule.studyType)."""

    INTERVENTIONAL = "INTERVENTIONAL"
    OBSERVATIONAL = "OBSERVATIONAL"
    EXPANDED_ACCESS = "EXPANDED_ACCESS"
