"""Live broker permission test (T-123). Runs inside the cluster (backend image) as a service pod.

Environment: MQ_HOST, MQ_CA, GW_PASSWORD, SC_PASSWORD (the two services' own passwords).
"""
import asyncio
import os
import ssl

import aio_pika
from aio_pika.exceptions import AMQPError

from app.core.config import Settings
from app.messaging.broker import UnauthorisedSender, build_message, connect, require_sender

HOST, CA = os.environ["MQ_HOST"], os.environ["MQ_CA"]
failed = False


def check(name: str, ok: bool) -> None:
    global failed
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    failed |= not ok


def settings(user: str, password: str) -> Settings:
    return Settings(mq_host=HOST, mq_user=user, mq_password=password, mq_ca_file=CA)


async def refused(awaitable) -> bool:
    try:
        await awaitable
    except (AMQPError, ConnectionError, OSError, asyncio.TimeoutError):
        return True
    return False


async def main() -> None:
    gw = await connect(settings("aucoff_gateway", os.environ["GW_PASSWORD"]))
    sc = await connect(settings("aucoff_scanner", os.environ["SC_PASSWORD"]))
    check("services connect over TLS with their own credentials", True)

    check("wrong password is refused", await refused(connect(settings("aucoff_gateway", "nope"))))
    check("guest account does not exist", await refused(connect(settings("guest", "guest"))))
    plain = aio_pika.connect_robust(host=HOST, port=5672, login="aucoff_gateway",
                                    password=os.environ["GW_PASSWORD"], virtualhost="aucoff", timeout=5)
    check("plain AMQP (no TLS) is not available", await refused(plain))
    untrusted = ssl.create_default_context()  # system store does not trust the local CA
    check("certificate is verified (untrusted CA is refused)", await refused(aio_pika.connect_robust(
        host=HOST, port=5671, login="aucoff_gateway", password=os.environ["GW_PASSWORD"],
        virtualhost="aucoff", ssl=True, ssl_context=untrusted, timeout=5)))

    gch = await gw.channel()
    sch = await sc.channel()
    work = await gch.get_exchange("aucoff.work", ensure=False)

    await work.publish(build_message(b"hello", sender="aucoff_gateway"), routing_key="work.gateway.scanner.run")
    inbox = await sch.get_queue("aucoff.scanner.inbox", ensure=False)
    msg = None
    for _ in range(20):
        msg = await inbox.get(no_ack=False, fail=False)
        if msg:
            break
        await asyncio.sleep(0.25)
    check("scanner receives the gateway's message", msg is not None and msg.body == b"hello")
    check("broker stamped the true sender", msg is not None and require_sender(msg, {"aucoff_gateway"}) == "aucoff_gateway")
    try:
        require_sender(msg, {"aucoff_scanner"})
        check("consumer rejects a message from an unexpected sender", False)
    except UnauthorisedSender:
        check("consumer rejects a message from an unexpected sender", True)
    if msg:
        await msg.ack()

    async def attempt(coro_factory) -> bool:
        ch = await gw.channel()
        try:
            return await refused(coro_factory(ch))
        finally:
            if not ch.is_closed:
                await ch.close()

    async def publish_as(ch, user_id, key):
        ex = await ch.get_exchange("aucoff.work", ensure=False)
        await ex.publish(build_message(b"x", sender=user_id), routing_key=key)
        await asyncio.sleep(0.5)
        await ch.get_exchange("aucoff.work", ensure=True)  # surfaces a closed channel

    check("cannot publish pretending to be another service (user_id)",
          await attempt(lambda ch: publish_as(ch, "aucoff_scanner", "work.gateway.scanner.run")))
    check("cannot publish under another service's routing key",
          await attempt(lambda ch: publish_as(ch, "aucoff_gateway", "work.scanner.gateway.run")))
    check("cannot read another service's queue",
          await attempt(_consume))
    check("cannot declare queues (no configure permission)",
          await attempt(lambda ch: ch.declare_queue("aucoff.gateway.rogue", durable=True)))
    await gw.close()
    await sc.close()


async def _consume(ch):
    q = await ch.get_queue("aucoff.scanner.inbox", ensure=False)
    await q.consume(lambda m: None)
    await asyncio.sleep(0.5)
    await ch.get_exchange("aucoff.work", ensure=True)


asyncio.run(main())
raise SystemExit(1 if failed else 0)
