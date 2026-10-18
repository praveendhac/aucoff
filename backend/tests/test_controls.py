"""Control catalogue format and own-words guards (T-006, LIC-6)."""

from pathlib import Path

from app.domain.controls import MAX_DESCRIPTION_CHARS, validate_directory

GOOD = """
catalogue_version: 0.1.0
controls:
  - id: UC-IAM-001
    title: Multi-factor authentication for administrators
    description: Admin access to production needs a second authentication factor.
    domain: identity-access
    severity: high
    check_type: hybrid
    status: draft
    author: Test Author
    requirements:
      - {framework: soc2-2017, ref: CC6.1}
      - {framework: pci-dss-4.0.1, ref: "8.4.2"}
"""


def write(tmp: Path, name: str, text: str) -> None:
    (tmp / name).write_text(text, encoding="utf-8")


def test_valid_catalogue_passes(tmp_path: Path) -> None:
    write(tmp_path, "iam.yaml", GOOD)
    assert validate_directory(tmp_path) == []


def test_empty_directory_passes(tmp_path: Path) -> None:
    assert validate_directory(tmp_path) == []


def test_duplicate_ids_across_files_fail(tmp_path: Path) -> None:
    write(tmp_path, "a.yaml", GOOD)
    write(tmp_path, "b.yaml", GOOD)
    assert any("duplicate control id UC-IAM-001" in e for e in validate_directory(tmp_path))


def test_unknown_framework_fails(tmp_path: Path) -> None:
    write(tmp_path, "a.yaml", GOOD.replace("pci-dss-4.0.1", "made-up"))
    assert any("unknown framework" in e for e in validate_directory(tmp_path))


def test_pasted_looking_long_description_fails(tmp_path: Path) -> None:
    long_text = "x" * (MAX_DESCRIPTION_CHARS + 1)
    write(
        tmp_path,
        "a.yaml",
        GOOD.replace(
            "Admin access to production needs a second authentication factor.",
            long_text,
        ),
    )
    assert validate_directory(tmp_path)


def test_links_in_text_fail(tmp_path: Path) -> None:
    write(
        tmp_path,
        "a.yaml",
        GOOD.replace("a second authentication factor", "a factor, see https://example.test/clause"),
    )
    assert any("links belong" in e for e in validate_directory(tmp_path))


def test_extra_fields_and_bad_ids_fail(tmp_path: Path) -> None:
    write(tmp_path, "a.yaml", GOOD.replace("UC-IAM-001", "IAM-1"))
    assert validate_directory(tmp_path)
    write(tmp_path, "a.yaml", GOOD + "    standard_text: copied clause\n")
    assert validate_directory(tmp_path)


def test_mixed_catalogue_versions_fail(tmp_path: Path) -> None:
    write(tmp_path, "a.yaml", GOOD)
    write(tmp_path, "b.yaml", GOOD.replace("UC-IAM-001", "UC-IAM-002").replace("0.1.0", "0.2.0"))
    assert any("catalogue_version" in e for e in validate_directory(tmp_path))
