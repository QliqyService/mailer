from email.message import EmailMessage
from email.utils import formatdate, make_msgid

import aiosmtplib

from app.schemas import CommentCreatedEmail
from app.settings import SETTINGS


def build_email(event: CommentCreatedEmail) -> EmailMessage:
    message = EmailMessage()

    message["From"] = f"Qliqy Notifications <{SETTINGS.MAIL_FROM}>"
    message["To"] = str(event.recipient_email)
    message["Reply-To"] = SETTINGS.MAIL_FROM
    message["Date"] = formatdate(localtime=False)
    message["Message-ID"] = make_msgid(domain="qliqy.org")

    subject_form = event.form_title or str(event.form_id)
    message["Subject"] = f"Новый комментарий к форме: {subject_form}"

    author = (
        " ".join(
            x
            for x in [event.comment_author_first_name, event.comment_author_last_name]
            if x
        ).strip()
        or "Аноним"
    )

    body = "\n".join(
        [
            f"Вам оставили новый комментарий к форме: {event.form_title or event.form_id}",
            f"Ссылка: {event.form_public_url or '-'}",
            "",
            f"Автор: {author}",
            f"Телефон: {event.comment_author_phone or '-'}",
            "",
            f"Заголовок: {event.comment_title or '-'}",
            f"Текст: {event.comment_text or '-'}",
            "",
            f"Время: {event.created_at.isoformat()}",
            "",
            f"form_id: {event.form_id}",
            f"comment_id: {event.comment_id}",
        ]
    )

    message.set_content(body)

    return message


async def send_email(message: EmailMessage) -> None:
    await aiosmtplib.send(
        message,
        hostname=SETTINGS.SMTP_HOST,
        port=SETTINGS.SMTP_PORT,
        username=SETTINGS.SMTP_USER,
        password=SETTINGS.SMTP_PASSWORD,
        start_tls=True,
    )