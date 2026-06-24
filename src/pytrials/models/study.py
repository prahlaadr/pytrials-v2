"""Pydantic v2 models mirroring the ClinicalTrials.gov API v2 study record.

The models are intentionally minimal for v0.1 but use the real API field names
(camelCase) via aliases. Every model allows extra fields so that new API fields
do not break deserialization, and every field is optional because the API has
many nullable values.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .enums import OverallStatus, Phase, StudyType

_CONFIG = ConfigDict(populate_by_name=True, extra="allow")


class Organization(BaseModel):
    """Sponsoring or submitting organization (identificationModule.organization)."""

    model_config = _CONFIG

    full_name: str | None = Field(default=None, alias="fullName")
    org_class: str | None = Field(default=None, alias="class")


class IdentificationModule(BaseModel):
    """Identifiers and titles (protocolSection.identificationModule)."""

    model_config = _CONFIG

    nct_id: str | None = Field(default=None, alias="nctId")
    brief_title: str | None = Field(default=None, alias="briefTitle")
    official_title: str | None = Field(default=None, alias="officialTitle")
    organization: Organization | None = None


class StatusModule(BaseModel):
    """Recruitment status and key dates (protocolSection.statusModule)."""

    model_config = _CONFIG

    overall_status: OverallStatus | None = Field(default=None, alias="overallStatus")
    status_verified_date: str | None = Field(default=None, alias="statusVerifiedDate")


class Sponsor(BaseModel):
    """A lead sponsor or collaborator."""

    model_config = _CONFIG

    name: str | None = None
    org_class: str | None = Field(default=None, alias="class")


class SponsorCollaboratorsModule(BaseModel):
    """Lead sponsor and collaborators (protocolSection.sponsorCollaboratorsModule)."""

    model_config = _CONFIG

    lead_sponsor: Sponsor | None = Field(default=None, alias="leadSponsor")
    collaborators: list[Sponsor] = Field(default_factory=list)


class ConditionsModule(BaseModel):
    """Conditions and keywords (protocolSection.conditionsModule)."""

    model_config = _CONFIG

    conditions: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class DesignModule(BaseModel):
    """Study design (protocolSection.designModule)."""

    model_config = _CONFIG

    study_type: StudyType | None = Field(default=None, alias="studyType")
    phases: list[Phase] = Field(default_factory=list)


class ProtocolSection(BaseModel):
    """The protocol section of a study record."""

    model_config = _CONFIG

    identification_module: IdentificationModule | None = Field(
        default=None, alias="identificationModule"
    )
    status_module: StatusModule | None = Field(default=None, alias="statusModule")
    sponsor_collaborators_module: SponsorCollaboratorsModule | None = Field(
        default=None, alias="sponsorCollaboratorsModule"
    )
    conditions_module: ConditionsModule | None = Field(
        default=None, alias="conditionsModule"
    )
    design_module: DesignModule | None = Field(default=None, alias="designModule")


class Study(BaseModel):
    """A single ClinicalTrials.gov study record."""

    model_config = _CONFIG

    protocol_section: ProtocolSection | None = Field(
        default=None, alias="protocolSection"
    )
    has_results: bool = Field(default=False, alias="hasResults")

    @property
    def nct_id(self) -> str | None:
        """Convenience accessor for the NCT identifier."""
        protocol = self.protocol_section
        if protocol is None or protocol.identification_module is None:
            return None
        return protocol.identification_module.nct_id

    @property
    def brief_title(self) -> str | None:
        """Convenience accessor for the brief title."""
        protocol = self.protocol_section
        if protocol is None or protocol.identification_module is None:
            return None
        return protocol.identification_module.brief_title

    @property
    def overall_status(self) -> OverallStatus | None:
        """Convenience accessor for the recruitment status."""
        protocol = self.protocol_section
        if protocol is None or protocol.status_module is None:
            return None
        return protocol.status_module.overall_status
