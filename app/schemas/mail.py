from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CommentCreatedEmail(BaseModel):
    created_at: datetime

    form_id: UUID
    form_title: str | None = None
    form_public_url: str | None = None

    comment_id: UUID
    comment_title: str | None = None
    comment_text: str | None = None

    comment_author_first_name: str | None = None
    comment_author_last_name: str | None = None
    comment_author_phone: str | None = None

    recipient_email: EmailStr
