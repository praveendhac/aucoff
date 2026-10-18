"""List endpoints for the first screens: unified controls, findings and evidence.

* `GET /unified-controls` (API-22) returns the REAL owner-authored catalogue from `data/controls`;
  an empty catalogue yields an empty list.
* `GET /findings` (API-47) and `GET /evidence` (API-37) return fixed SYNTHETIC demo rows
  (`data_source: synthetic`) until scanners and assessments exist. Nothing here is a real result.
"""

from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.pagination import Cursor, Limit, Page, paginate
from app.core.config import get_settings
from app.core.security import Principal, require_scope
from app.domain.controls import Control, load_catalogue

router = APIRouter(tags=["lists"])
catalog_read = require_scope("catalog:read")
finding_write = require_scope("finding:write")
evidence_read = require_scope("evidence:read")

SeverityName = Literal["critical", "high", "medium", "low"]
FindingStatus = Literal["open", "in_progress", "accepted_risk", "resolved"]
EvidenceSource = Literal["aws", "kubernetes", "github", "entra", "upload"]


class RequirementRef(BaseModel):
    framework: str = Field(examples=["soc2-2017"])
    ref: str = Field(examples=["CC6.1"])


class UnifiedControl(BaseModel):
    id: str = Field(examples=["UC-IAM-001"])
    title: str
    description: str
    domain: str
    severity: SeverityName
    check_type: Literal["automated", "manual", "hybrid"]
    status: Literal["draft", "approved"]
    requirements: list[RequirementRef]


class Finding(BaseModel):
    id: str = Field(examples=["F-0001"])
    title: str
    severity: SeverityName
    status: FindingStatus
    framework_id: str
    control_id: str
    first_seen: date
    age_days: int


class EvidenceItem(BaseModel):
    id: str = Field(examples=["E-0001"])
    title: str
    source: EvidenceSource
    collected_at: date
    fresh: bool = Field(description="Collected within its freshness window.")


def _to_api(control: Control) -> UnifiedControl:
    return UnifiedControl(
        id=control.id,
        title=control.title,
        description=control.description,
        domain=control.domain,
        severity=control.severity.value,
        check_type=control.check_type,
        status=control.status,
        requirements=[
            RequirementRef(framework=r.framework, ref=r.ref) for r in control.requirements
        ],
    )


@router.get(
    "/unified-controls",
    operation_id="listUnifiedControls",
    summary="List unified controls",
    description=(
        "The owner-authored unified control catalogue (scope `catalog:read`). Filter by "
        "`framework` (a requirement maps to it) or `domain`. An empty catalogue returns no items."
    ),
    response_model=Page[UnifiedControl],
)
def list_unified_controls(
    limit: Limit = 25,
    cursor: Cursor = None,
    framework: str | None = None,
    domain: str | None = None,
    _principal: Principal = Depends(catalog_read),
) -> Page[UnifiedControl]:
    try:
        controls = load_catalogue(Path(get_settings().controls_dir))
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="the control catalogue is invalid") from exc
    rows = [
        _to_api(c)
        for c in controls
        if (domain is None or c.domain == domain)
        and (framework is None or any(r.framework == framework for r in c.requirements))
    ]
    items, nxt = paginate(rows, limit, cursor)
    return Page[UnifiedControl](items=items, next_cursor=nxt, data_source="catalogue")


_SEVERITIES: list[SeverityName] = ["critical", "high", "medium", "low", "medium", "low", "high"]
_STATUSES: list[FindingStatus] = ["open", "in_progress", "open", "accepted_risk", "resolved"]
_FRAMEWORKS = ["soc2-2017", "pci-dss-4.0.1", "rbi-dpsc-2026", "iso27001-2022"]
_TOPICS = [
    "Administrator accounts without a second authentication factor",
    "Storage bucket allows public read access",
    "Audit logging disabled for a production account",
    "Encryption at rest not enforced on a database volume",
    "Container image runs as root",
    "Access review overdue for privileged roles",
    "TLS 1.0 still enabled on a public endpoint",
    "Backup restore test older than policy",
]
_ANCHOR = date(2026, 10, 19)


def _synthetic_findings() -> list[Finding]:
    rows: list[Finding] = []
    for i in range(40):
        age = 3 + (i * 7) % 120
        rows.append(
            Finding(
                id=f"F-{i + 1:04d}",
                title=_TOPICS[i % len(_TOPICS)],
                severity=_SEVERITIES[i % len(_SEVERITIES)],
                status=_STATUSES[i % len(_STATUSES)],
                framework_id=_FRAMEWORKS[i % len(_FRAMEWORKS)],
                control_id=f"UC-DEMO-{(i % 12) + 1:03d}",
                first_seen=_ANCHOR - timedelta(days=age),
                age_days=age,
            )
        )
    return rows


_SOURCES: list[EvidenceSource] = ["aws", "kubernetes", "github", "entra", "upload"]
_EVIDENCE_TITLES = [
    "IAM credential report",
    "Cluster RBAC configuration",
    "Branch protection settings",
    "Conditional access policies",
    "Information security policy (PDF)",
]


def _synthetic_evidence() -> list[EvidenceItem]:
    rows: list[EvidenceItem] = []
    for i in range(30):
        age = (i * 5) % 70
        rows.append(
            EvidenceItem(
                id=f"E-{i + 1:04d}",
                title=f"{_EVIDENCE_TITLES[i % len(_EVIDENCE_TITLES)]} #{i // 5 + 1}",
                source=_SOURCES[i % len(_SOURCES)],
                collected_at=_ANCHOR - timedelta(days=age),
                fresh=age <= 30,
            )
        )
    return rows


@router.get(
    "/findings",
    operation_id="listFindings",
    summary="List findings",
    description=(
        "Findings (scope `finding:write`), filterable by `severity` and `status`. Until scanners "
        "run, rows are synthetic demo data and `data_source` is `synthetic`."
    ),
    response_model=Page[Finding],
)
def list_findings(
    limit: Limit = 25,
    cursor: Cursor = None,
    severity: SeverityName | None = None,
    status: FindingStatus | None = None,
    _principal: Principal = Depends(finding_write),
) -> Page[Finding]:
    rows = [
        f
        for f in _synthetic_findings()
        if (severity is None or f.severity == severity) and (status is None or f.status == status)
    ]
    items, nxt = paginate(rows, limit, cursor)
    return Page[Finding](items=items, next_cursor=nxt, data_source="synthetic")


@router.get(
    "/evidence",
    operation_id="listEvidence",
    summary="List evidence",
    description=(
        "Evidence items (scope `evidence:read`), filterable by `source`. Until collectors run, "
        "rows are synthetic demo data and `data_source` is `synthetic`."
    ),
    response_model=Page[EvidenceItem],
)
def list_evidence(
    limit: Limit = 25,
    cursor: Cursor = None,
    source: EvidenceSource | None = None,
    _principal: Principal = Depends(evidence_read),
) -> Page[EvidenceItem]:
    rows = [e for e in _synthetic_evidence() if source is None or e.source == source]
    items, nxt = paginate(rows, limit, cursor)
    return Page[EvidenceItem](items=items, next_cursor=nxt, data_source="synthetic")
