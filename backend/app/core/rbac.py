"""Role to scope mapping (backend-spec section 8, api-contract section 4).

A user token carries the API scopes granted to the web client and the user's roles. The gateway
lets a user exercise only the scopes that one of their roles allows, so an over-broad token (a
client scope added by mistake) never grants more than the role matrix. Service identities have no
roles and keep exactly the scopes the identity provider issued to them.
"""

from collections.abc import Iterable

# Clients that act for a signed-in user; every other client is a service identity.
USER_CLIENT_IDS = frozenset({"aucoff-web"})

_ALL = {"catalog:read", "docs:read", "copilot:use"}

ROLE_SCOPES: dict[str, frozenset[str]] = {
    "compliance_officer": frozenset(
        _ALL
        | {
            "mapping:write",
            "scope:write",
            "assessment:run",
            "evidence:read",
            "evidence:write",
            "result:review",
            "finding:write",
            "report:read",
            "report:generate",
            "questionnaire:read",
            "questionnaire:write",
            "questionnaire:approve",
        }
    ),
    "ciso": frozenset(
        _ALL
        | {
            "mapping:write",
            "scope:write",
            "assessment:run",
            "evidence:read",
            "result:review",
            "finding:write",
            "report:read",
            "report:generate",
            "audit:read",
            "questionnaire:read",
            "questionnaire:write",
            "questionnaire:approve",
        }
    ),
    "engineer": frozenset(
        _ALL
        | {
            "connector:write",
            "evidence:read",
            "evidence:write",
            "finding:write",
            "questionnaire:read",
        }
    ),
    "auditor": frozenset(
        _ALL
        | {"evidence:read", "report:read", "report:generate", "audit:read", "questionnaire:read"}
    ),
    "executive": frozenset(_ALL | {"report:read", "report:generate"}),
    "admin": frozenset(_ALL | {"connector:write", "admin:write", "audit:read", "ops:read"}),
}


def scopes_for_roles(roles: Iterable[str]) -> frozenset[str]:
    allowed: set[str] = set()
    for role in roles:
        allowed |= ROLE_SCOPES.get(role, frozenset())
    return frozenset(allowed)


def effective_scopes(
    token_scopes: frozenset[str], roles: Iterable[str], authorised_party: str | None
) -> frozenset[str]:
    """Scopes the caller may use: token scopes, narrowed by roles for user tokens."""
    if authorised_party in USER_CLIENT_IDS:
        return token_scopes & scopes_for_roles(roles)
    return token_scopes
