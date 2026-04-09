from faststream.rabbit import RabbitQueue, RabbitRouter
from loguru import logger as LOGGER

from app.mailer import build_email, build_smtp_message, send_email
from app.schemas import CommentCreatedEmail, SmtpMessage
from app.settings import SETTINGS
from app.db.engine import SessionLocal
from app.comment_log import CommentLogRepo
from app.db.models import Status

QUEUE = f"{SETTINGS.APP_STAND}::{SETTINGS.APP_NAME}::comment_created"
SMTP_QUEUE = f"{SETTINGS.APP_STAND}::mailer::send_message_to_smtp"

router = RabbitRouter()


@router.subscriber(queue=RabbitQueue(name=QUEUE, durable=True))
async def comment_created(event: dict) -> None:
    """
    Обработчик события comment_created.
    Получает событие из RabbitMQ и отправляет email владельцу формы.
    """
    LOGGER.debug(f"[MAILER] comment_created received: {event}")

    payload = CommentCreatedEmail.model_validate(event)
    msg = build_email(payload)

    try:
        await send_email(msg)

        async with SessionLocal() as session:
            repo = CommentLogRepo(session)
            await repo.save(payload, Status.SENT)

        LOGGER.info(
            f"[MAILER] Email sent to={payload.recipient_email} "
            f"form_id={payload.form_id} comment_id={payload.comment_id}"
        )

    except Exception as e:
        async with SessionLocal() as session:
            repo = CommentLogRepo(session)
            await repo.save(payload, Status.FAILED)

        LOGGER.error(f"[MAILER] Send failed: {e!r}")
        raise


@router.subscriber(queue=RabbitQueue(name=SMTP_QUEUE, durable=True))
async def send_message_to_smtp(event: dict) -> None:
    """
    Универсальный обработчик SMTP-сообщений от других сервисов, включая auth.
    """
    LOGGER.debug(f"[MAILER] send_message_to_smtp received: {event}")

    payload = SmtpMessage.model_validate(event)
    message = build_smtp_message(payload)

    try:
        await send_email(message)
        LOGGER.info(f"[MAILER] SMTP email sent to={payload.recipients} subject={payload.subject}")
    except Exception as e:
        LOGGER.error(f"[MAILER] SMTP send failed: {e!r}")
        raise
