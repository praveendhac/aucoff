"""Role to scope mapping (backend-spec section 8)."""

import pytest

from app.core.rbac import ROLE_SCOPES, effective_scopes, scopes_for_roles

ALL_API_SCOPES = {
    "catalog:read",
    "mapping:write",
    "scope:write",
    "assessment:run",
    "connector:write",
    "evidence:read",
    "evidence:write",
    "result:review",
    "finding:write",
    "report:read",
    "report:generate",
    "audit:read",
    "admin:write",
    "docs:read",
    "ops:read",
    "questionnaire:read",
    "questionnaire:write",
    "questionnaire:approve",
    "copilot:use",
}


def test_every_mapped_scope_is_a_known_api_scope() -> None:
    for role, scopes in ROLE_SCOPES.items():
        assert scopes <= ALL_API_SCOPES, role


def test_every_api_scope_is_granted_to_some_role() -> None:
    granted = set().union(*ROLE_SCOPES.values())
    assert granted >= ALL_API_SCOPES


@pytest.mark.parametrize(
    ("role", "scope", "allowed"),
    [
        ("auditor", "assessment:run", False),
        ("auditor", "audit:read", True),
        ("executive", "evidence:read", False),
        ("executive", "report:read", True),
        ("engineer", "result:review", False),
        ("engineer", "connector:write", True),
        ("compliance_officer", "admin:write", False),
        ("ciso", "questionnaire:approve", True),
        ("admin", "ops:read", True),
        ("admin", "result:review", False),
    ],
)
def test_matrix_spot_checks(role: str, scope: str, allowed: bool) -> None:
    assert (scope in scopes_for_roles([role])) is allowed


def test_user_token_is_narrowed_to_the_roles() -> None:
    token = frozenset(ALL_API_SCOPES)
    got = effective_scopes(token, ["executive"], "aucoff-web")
    assert got == ROLE_SCOPES["executive"]


def test_user_without_known_role_gets_nothing() -> None:
    assert effective_scopes(frozenset(ALL_API_SCOPES), [], "aucoff-web") == frozenset()
    assert effective_scopes(frozenset(ALL_API_SCOPES), ["made-up"], "aucoff-web") == frozenset()


def test_service_identity_keeps_its_issued_scopes() -> None:
    assert effective_scopes(frozenset({"ops:read"}), [], "svc-gateway") == {"ops:read"}


def test_roles_cannot_widen_a_token() -> None:
    assert effective_scopes(frozenset({"report:read"}), ["admin", "ciso"], "aucoff-web") == {
        "report:read"
    }
