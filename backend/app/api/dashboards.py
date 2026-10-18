"""Posture dashboard (api-contract.md API-70, design.md section 10.5).

Until the assessment engine produces real results, this endpoint returns fixed SYNTHETIC demo
numbers. The response says so (`data_source: "synthetic"`) and the web app shows a banner; nothing
here may be presented as a real compliance result. The shape is the contract the real
implementation will fill from assessment snapshots (database-spec, history tables).
"""

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.security import Principal, require_scope

router = APIRouter(prefix="/dashboards", tags=["dashboards"])
report_read = require_scope("report:read")

Severity = Literal["critical", "high", "medium", "low"]


class Kpi(BaseModel):
    value: float = Field(description="Current value.", examples=[78.4])
    delta_vs_previous: float = Field(description="Change since the previous scan.", examples=[2.1])


class Kpis(BaseModel):
    posture_score: Kpi = Field(description="Overall compliance posture score, 0-100 (M-01).")
    coverage_pct: Kpi = Field(description="Share of in-scope controls with a result (M-02).")
    open_findings: Kpi = Field(description="Open findings across severities (M-06).")
    pending_approvals: Kpi = Field(description="Results waiting for human approval (M-14).")
    evidence_freshness_pct: Kpi = Field(description="Evidence collected within its window (M-09).")


class StatusDistribution(BaseModel):
    passed: int = Field(alias="pass", description="Controls passing.")
    partial: int
    fail: int
    unknown: int
    not_applicable: int

    model_config = {"populate_by_name": True}


class SeverityComparison(BaseModel):
    severity: Severity
    latest: int = Field(description="Failing controls of this severity in the latest scan.")
    previous: int = Field(description="Same, in the scan before the latest.")
    before_previous: int = Field(description="Same, two scans before the latest.")


class FrameworkCoverage(BaseModel):
    framework_id: str = Field(examples=["soc2-2017"])
    name: str = Field(examples=["SOC 2 (Common Criteria)"])
    coverage_pct: float
    delta_vs_previous: float


class PostureDashboard(BaseModel):
    data_source: Literal["synthetic", "assessments"] = Field(
        description="`synthetic` means demo numbers, not real results."
    )
    kpis: Kpis
    status_distribution: StatusDistribution
    severity_comparison: list[SeverityComparison]
    frameworks: list[FrameworkCoverage]


def _synthetic() -> PostureDashboard:
    return PostureDashboard(
        data_source="synthetic",
        kpis=Kpis(
            posture_score=Kpi(value=78.4, delta_vs_previous=2.1),
            coverage_pct=Kpi(value=86.0, delta_vs_previous=3.5),
            open_findings=Kpi(value=42, delta_vs_previous=-6),
            pending_approvals=Kpi(value=7, delta_vs_previous=2),
            evidence_freshness_pct=Kpi(value=91.2, delta_vs_previous=-1.4),
        ),
        status_distribution=StatusDistribution.model_validate(
            {"pass": 312, "partial": 64, "fail": 38, "unknown": 21, "not_applicable": 15}
        ),
        severity_comparison=[
            SeverityComparison(severity="critical", latest=2, previous=4, before_previous=5),
            SeverityComparison(severity="high", latest=9, previous=12, before_previous=11),
            SeverityComparison(severity="medium", latest=17, previous=16, before_previous=19),
            SeverityComparison(severity="low", latest=14, previous=15, before_previous=18),
        ],
        frameworks=[
            FrameworkCoverage(
                framework_id="soc2-2017",
                name="SOC 2 (Common Criteria)",
                coverage_pct=91.0,
                delta_vs_previous=2.0,
            ),
            FrameworkCoverage(
                framework_id="pci-dss-4.0.1",
                name="PCI DSS v4.0.1",
                coverage_pct=82.5,
                delta_vs_previous=4.5,
            ),
            FrameworkCoverage(
                framework_id="rbi-dpsc-2026",
                name="RBI DPSC 2026",
                coverage_pct=74.0,
                delta_vs_previous=-1.0,
            ),
            FrameworkCoverage(
                framework_id="iso27001-2022",
                name="ISO/IEC 27001:2022",
                coverage_pct=88.0,
                delta_vs_previous=3.0,
            ),
        ],
    )


@router.get(
    "/posture",
    operation_id="postureDashboard",
    summary="Posture dashboard",
    description=(
        "KPI strip, control status distribution, severity counts for the latest scan and the "
        "previous two, and coverage per framework, with deltas against the previous scan. "
        "Requires scope `report:read`. Until assessments exist the numbers are synthetic and "
        "`data_source` is `synthetic`."
    ),
    response_model=PostureDashboard,
    response_model_by_alias=True,
)
def posture(_principal: Principal = Depends(report_read)) -> PostureDashboard:
    return _synthetic()
