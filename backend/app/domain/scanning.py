"""Scanner framework: result schema, connector and adapter contracts, rollup (backend-spec 4a, 7).

Everything here is pure (no network, no files except the check-definition loader). A *connector*
reaches a source with read-only credentials and returns raw documents; a *scanner adapter* turns
them into normalised `CheckResult`s; `rollup` combines results into PROPOSED control results.
Proposed results are advisory: a person approves the final result (constitution AI-2).
"""

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, Protocol

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from app.domain.controls import Control, Severity


class CheckStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"  # the check could not be evaluated (API failure, missing data)
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class CheckResult:
    """One normalised result for one resource (backend-spec 4a)."""

    check_id: str
    tool: str
    tool_version: str
    rule_pack_version: str
    resource_ref: str
    status: CheckStatus
    severity: Severity
    observed_at: datetime
    evidence_ref: str  # SHA-256 of the evidence document the result was computed from
    detail: str = ""  # short explanation; never contains credentials or secret values


@dataclass(frozen=True)
class Evidence:
    """Metadata of a stored raw document (database-spec `evidence`)."""

    sha256: str
    source_type: str
    source_ref: str
    collected_at: datetime
    collector: str
    collector_version: str
    size: int


@dataclass(frozen=True)
class RawDocument:
    name: str  # for example "pods"
    content: bytes  # canonical JSON as collected
    source_ref: str  # for example "k8s:https://api.example/api/v1/pods"


@dataclass(frozen=True)
class Collection:
    documents: list[RawDocument]
    errors: list[str] = field(default_factory=list)  # partial failures: recorded, never skipped


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    missing: list[str]  # required read permissions that are absent
    excessive: list[str]  # write or secret-reading permissions that must not be granted


@dataclass(frozen=True)
class ScannerInfo:
    tool: str
    tool_version: str
    rule_pack_version: str
    licence: str
    required_permissions: list[str]


class Connector(Protocol):
    """Read-only access to one source (backend-spec 7)."""

    def validate(self) -> ValidationReport: ...
    def collect(self, scope: "Scope") -> Collection: ...
    def describe_permissions(self) -> list[str]: ...


@dataclass(frozen=True)
class Scope:
    namespaces: frozenset[str] | None = None  # None = everything the credentials can see


class ScannerAdapter(Protocol):
    def describe(self) -> ScannerInfo: ...
    def normalise(
        self, documents: dict[str, tuple[RawDocument, str]], observed_at: datetime
    ) -> list[CheckResult]: ...


# ---------- check definitions: tool check -> unified controls ----------

CheckId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(\.[a-z0-9-]+)+$")]


class CheckDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_check_id: CheckId
    unified_control_ids: list[
        Annotated[str, StringConstraints(pattern=r"^UC-[A-Z]{2,6}-\d{3}$")]
    ] = Field(min_length=1)
    severity: Severity
    rationale: Annotated[str, StringConstraints(min_length=10, max_length=300)]


class RulePack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    tool_version: str
    rule_pack_version: str
    licence: Literal["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause"]
    checks: list[CheckDefinition]


def load_rule_pack(path: Path) -> RulePack:
    try:
        return RulePack.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    except (yaml.YAMLError, ValidationError, OSError) as exc:
        raise ValueError(f"{path}: {exc}") from exc


def validate_rule_pack(pack: RulePack, controls: Sequence[Control]) -> list[str]:
    """Every definition must map to controls that exist, and check ids must be unique."""
    known = {c.id for c in controls}
    errors: list[str] = []
    seen: set[str] = set()
    for check in pack.checks:
        if check.tool_check_id in seen:
            errors.append(f"duplicate check {check.tool_check_id}")
        seen.add(check.tool_check_id)
        errors.extend(
            f"{check.tool_check_id}: unknown control {cid}"
            for cid in check.unified_control_ids
            if cid not in known
        )
    return errors


# ---------- rollup: check results -> proposed control results ----------


class ProposedStatus(StrEnum):
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProposedControlResult:
    control_id: str
    status: ProposedStatus
    passed: int
    failed: int
    errors: int
    check_ids: list[str]
    summary: str


def rollup(results: Iterable[CheckResult], pack: RulePack) -> list[ProposedControlResult]:
    """Combine check results per unified control.

    * all applicable results pass -> pass; all fail -> fail; a mix -> partial;
    * evaluation errors never count as a pass: with no failure they make the control unknown;
    * only not-applicable results (or none) -> no proposal (the control is not assessed here).
    """
    by_check = {c.tool_check_id: c for c in pack.checks}
    grouped: dict[str, list[CheckResult]] = defaultdict(list)
    for result in results:
        definition = by_check.get(result.check_id)
        if definition is None:
            continue
        for control_id in definition.unified_control_ids:
            grouped[control_id].append(result)

    proposals: list[ProposedControlResult] = []
    for control_id in sorted(grouped):
        rs = [r for r in grouped[control_id] if r.status is not CheckStatus.NOT_APPLICABLE]
        if not rs:
            continue
        passed = sum(r.status is CheckStatus.PASS for r in rs)
        failed = sum(r.status is CheckStatus.FAIL for r in rs)
        errors = sum(r.status is CheckStatus.ERROR for r in rs)
        if failed and not passed:
            status = ProposedStatus.FAIL
        elif failed:
            status = ProposedStatus.PARTIAL
        elif errors:
            status = ProposedStatus.UNKNOWN
        else:
            status = ProposedStatus.PASS
        proposals.append(
            ProposedControlResult(
                control_id=control_id,
                status=status,
                passed=passed,
                failed=failed,
                errors=errors,
                check_ids=sorted({r.check_id for r in rs}),
                summary=f"{passed} passed, {failed} failed, {errors} not evaluated",
            )
        )
    return proposals
