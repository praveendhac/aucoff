from scripts.check_licences import ok


def test_permissive_licences_pass() -> None:
    assert ok("x", "MIT")
    assert ok("x", "BSD-3-Clause")
    assert ok("x", "Apache-2.0 OR BSD-2-Clause")
    assert ok("x", "Mozilla Public License 2.0 (MPL 2.0)")


def test_copyleft_and_source_available_fail() -> None:
    for lic in ("AGPL-3.0", "GPL-2.0-only", "LGPL-2.1", "SSPL-1.0", "BUSL-1.1", "MIT AND GPL-3.0"):
        assert not ok("x", lic), lic


def test_unknown_licence_fails() -> None:
    assert not ok("x", "Proprietary")
    assert not ok("x", "UNKNOWN")


def test_owner_approved_licences_pass() -> None:
    for lic in ("PSF-2.0", "MIT-0", "MIT AND PSF-2.0", "0BSD", "BlueOak-1.0.0", "CC0-1.0"):
        assert ok("any_package", lic), lic
