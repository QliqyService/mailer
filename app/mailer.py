from datetime import datetime
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from html import escape

import aiosmtplib

from app.schemas import CommentCreatedEmail, SmtpMessage
from app.settings import SETTINGS


def _format_author(event: CommentCreatedEmail) -> str:
    return (
        " ".join(
            part
            for part in [event.comment_author_first_name, event.comment_author_last_name]
            if part
        ).strip()
        or "Anonymous"
    )


def _format_created_at(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M UTC")


def _build_plain_text(event: CommentCreatedEmail) -> str:
    author = _format_author(event)
    form_name = event.form_title or str(event.form_id)

    lines = [
        f"You received a new comment on your Qliqy form: {form_name}",
        "",
        "Comment details",
        f"- Author: {author}",
        f"- Phone: {event.comment_author_phone or '-'}",
        f"- Title: {event.comment_title or '-'}",
        f"- Message: {event.comment_text or '-'}",
        f"- Received: {_format_created_at(event.created_at)}",
        "",
        f"Public form link: {event.form_public_url or '-'}",
        "",
        "Technical details",
        f"- Form ID: {event.form_id}",
        f"- Comment ID: {event.comment_id}",
    ]

    return "\n".join(lines)


def _build_html(event: CommentCreatedEmail) -> str:
    author = escape(_format_author(event))
    form_name = escape(event.form_title or str(event.form_id))
    phone = escape(event.comment_author_phone or "-")
    comment_title = escape(event.comment_title or "-")
    comment_text = escape(event.comment_text or "-").replace("\n", "<br>")
    created_at = escape(_format_created_at(event.created_at))
    form_id = escape(str(event.form_id))
    comment_id = escape(str(event.comment_id))
    form_public_url = event.form_public_url or ""
    safe_form_public_url = escape(form_public_url)

    open_form_block = ""
    if form_public_url:
        open_form_block = f"""
          <p style="margin:0 0 24px;">
            <a href="{safe_form_public_url}" style="display:inline-block;padding:12px 18px;background:#111827;color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;">
              Open Public Form
            </a>
          </p>
        """

    return f"""\
<html>
  <body style="margin:0;padding:24px;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#111827;">
    <div style="max-width:640px;margin:0 auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:18px;overflow:hidden;">
      <div style="padding:24px 24px 16px;background:linear-gradient(135deg,#0f172a,#1f2937);color:#ffffff;">
        <p style="margin:0 0 8px;font-size:13px;letter-spacing:.08em;text-transform:uppercase;opacity:.8;">QLIQY Notification</p>
        <h1 style="margin:0;font-size:24px;line-height:1.25;">New comment received</h1>
        <p style="margin:12px 0 0;font-size:15px;line-height:1.6;opacity:.9;">
          Someone left a new message on your form <strong>{form_name}</strong>.
        </p>
      </div>
      <div style="padding:24px;">
        {open_form_block}
        <table role="presentation" style="width:100%;border-collapse:collapse;margin-bottom:24px;">
          <tr>
            <td style="padding:10px 0;color:#6b7280;width:170px;">Author</td>
            <td style="padding:10px 0;font-weight:600;">{author}</td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#6b7280;">Phone</td>
            <td style="padding:10px 0;">{phone}</td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#6b7280;">Title</td>
            <td style="padding:10px 0;">{comment_title}</td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#6b7280;">Received</td>
            <td style="padding:10px 0;">{created_at}</td>
          </tr>
        </table>
        <div style="margin-bottom:24px;padding:18px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:14px;">
          <p style="margin:0 0 8px;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#6b7280;">Message</p>
          <p style="margin:0;font-size:15px;line-height:1.7;">{comment_text}</p>
        </div>
        <div style="padding-top:18px;border-top:1px solid #e5e7eb;color:#6b7280;font-size:13px;line-height:1.7;">
          <div>Form ID: <code>{form_id}</code></div>
          <div>Comment ID: <code>{comment_id}</code></div>
          <div>Public URL: <a href="{safe_form_public_url}" style="color:#2563eb;text-decoration:none;">{safe_form_public_url or '-'}</a></div>
        </div>
      </div>
    </div>
  </body>
</html>
"""


def build_email(event: CommentCreatedEmail) -> EmailMessage:
    message = EmailMessage()

    message["From"] = f"Qliqy Notifications <{SETTINGS.MAIL_FROM}>"
    message["To"] = str(event.recipient_email)
    message["Reply-To"] = SETTINGS.MAIL_FROM
    message["Date"] = formatdate(localtime=False)
    message["Message-ID"] = make_msgid(domain="qliqy.org")

    subject_form = event.form_title or str(event.form_id)
    message["Subject"] = f"New comment on Qliqy form: {subject_form}"

    message.set_content(_build_plain_text(event))
    message.add_alternative(_build_html(event), subtype="html")

    return message


def build_smtp_message(payload: SmtpMessage) -> EmailMessage:
    message = EmailMessage()

    message["From"] = f"Qliqy Notifications <{SETTINGS.MAIL_FROM}>"
    message["To"] = ", ".join(str(recipient) for recipient in payload.recipients)
    message["Reply-To"] = SETTINGS.MAIL_FROM
    message["Date"] = formatdate(localtime=False)
    message["Message-ID"] = make_msgid(domain="qliqy.org")
    message["Subject"] = payload.subject

    message.set_content("Please view this email in HTML format.")
    message.add_alternative(payload.html_message, subtype="html")

    return message


async def send_email(message: EmailMessage) -> None:
    port = SETTINGS.SMTP_PORT
    await aiosmtplib.send(
        message,
        hostname=SETTINGS.SMTP_HOST,
        port=port,
        username=SETTINGS.SMTP_USER,
        password=SETTINGS.SMTP_PASSWORD,
        use_tls=(port == 465),
        start_tls=(port == 587),
        timeout=30,
    )
