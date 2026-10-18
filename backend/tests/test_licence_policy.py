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


def test_psf_is_only_accepted_for_the_documented_exception() -> None:
    assert ok("typing_extensions", "PSF-2.0")
    assert not ok("other_package", "PSF-2.0")
