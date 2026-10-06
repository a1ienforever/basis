from uuid import uuid4

from src.application.services import InboxService
from tests.fakes import FakeUnitOfWork


async def test_new_message_is_registered(uow: FakeUnitOfWork) -> None:
    message_id = uuid4()

    assert await InboxService().register(uow, "payments", message_id)

    assert ("payments", message_id) in uow.repository("inbox").rows


async def test_duplicate_message_is_rejected(uow: FakeUnitOfWork) -> None:
    message_id = uuid4()
    service = InboxService()
    await service.register(uow, "payments", message_id)

    assert not await service.register(uow, "payments", message_id)


async def test_same_message_is_registered_for_another_consumer(uow: FakeUnitOfWork) -> None:
    message_id = uuid4()
    service = InboxService()
    await service.register(uow, "payments", message_id)

    assert await service.register(uow, "webhooks", message_id)
