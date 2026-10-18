"""Consumer-side sender check and fail-closed configuration (T-123)."""

from types import SimpleNamespace
from typing import Any

import pytest

from app.core.config import Settings
from app.messaging.broker import UnauthorisedSender, build_message, connect, require_sender


def message(user_id: str | None) -> Any:
    return SimpleNamespace(user_id=user_id)


def test_message_names_its_sender_and_is_persistent() -> None:
    built = build_message(b"x", sender="aucoff_gateway")
    assert built.user_id == "aucoff_gateway"
    assert built.message_id
    assert built.delivery_mode == 2


def test_allowed_sender_is_accepted() -> None:
    assert require_sender(message("aucoff_gateway"), {"aucoff_gateway"}) == "aucoff_gateway"


@pytest.mark.parametrize("sender", [None, "", "aucoff_scanner"])
def test_other_or_unnamed_sender_is_rejected(sender: str | None) -> None:
    with pytest.raises(UnauthorisedSender):
        require_sender(message(sender), {"aucoff_gateway"})


async def test_connect_fails_closed_without_credentials() -> None:
    with pytest.raises(RuntimeError):
        await connect(Settings(mq_host="broker"))
