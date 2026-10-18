"""Unified control catalogue: schema and validation (spec 10a, T-006, constitution LIC-6).

The v1 control set is authored by the owner as YAML files under `data/controls/`. Each control is
written in AUCoFF's own words and points to framework requirements by clause identifier only;
standards text is never stored (LIC-6). This module defines the file format and the checks that
run in CI, so a malformed or copied-looking control cannot be merged.
"""

import re
from collections import Counter
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

# Frameworks the first catalogue release covers (owner decision 2026-10-19). More are added here
# when the owner extends the set.
FRAMEWORKS = frozenset({"soc2-2017", "pci-dss-4.0.1", "rbi-dpsc-2026", "iso27001-2022"})

# Own-words guard (LIC-6): a control description is a short summary, not a pasted clause.
MAX_DESCRIPTION_CHARS = 600
MAX_TITLE_CHARS = 120
CONTROL_ID = re.compile(r"^UC-[A-Z]{2,6}-\d{3}$")
URL = re.compile(r"https?://", re.I)


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Requirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework: str
    ref: Annotated[
        str, StringConstraints(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9.()\-_ /]+$")
    ]


class Control(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Annotated[str, StringConstraints(pattern=CONTROL_ID.pattern)]
    title: Annotated[str, StringConstraints(min_length=3, max_length=MAX_TITLE_CHARS)]
    description: Annotated[str, StringConstraints(min_length=20, max_length=MAX_DESCRIPTION_CHARS)]
    domain: Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9-]{1,40}$")]
    severity: Severity
    check_type: Literal["automated", "manual", "hybrid"]
    requirements: list[Requirement] = Field(min_length=1)
    # draft = AI- or colleague-proposed, approved = reviewed and accepted by the owner.
    status: Literal["draft", "approved"] = "draft"
    author: Annotated[str, StringConstraints(min_length=2, max_length=80)]


class ControlFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    catalogue_version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    controls: list[Control]


def validate_file(path: Path) -> tuple[ControlFile | None, list[str]]:
    errors: list[str] = []
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        parsed = ControlFile.model_validate(raw)
    except (yaml.YAMLError, ValidationError, OSError) as exc:
        return None, [f"{path}: {exc}"]
    for control in parsed.controls:
        for req in control.requirements:
            if req.framework not in FRAMEWORKS:
                errors.append(f"{path}: {control.id}: unknown framework '{req.framework}'")
        if URL.search(control.description) or URL.search(control.title):
            errors.append(f"{path}: {control.id}: links belong in references, not in the text")
    return parsed, errors


def validate_directory(directory: Path) -> list[str]:
    """Validate every `*.yaml` file; ids must be unique across the whole catalogue."""
    errors: list[str] = []
    ids: Counter[str] = Counter()
    versions: set[str] = set()
    for path in sorted(directory.glob("*.yaml")):
        parsed, file_errors = validate_file(path)
        errors.extend(file_errors)
        if parsed:
            versions.add(parsed.catalogue_version)
            ids.update(c.id for c in parsed.controls)
    errors.extend(f"duplicate control id {cid}" for cid, n in ids.items() if n > 1)
    if len(versions) > 1:
        errors.append(f"files disagree on catalogue_version: {sorted(versions)}")
    return errors
