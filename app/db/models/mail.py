from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Status(StrEnum):
    SENT = "sent"
    FAILED = "failed"


class CommentDeliveryLog(Base):
    __tablename__ = "comment_delivery_log"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    form_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    form_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    form_public_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    comment_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    comment_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    comment_author_first_name: Mapped[str | None] = mapped_column(String(255))
    comment_author_last_name: Mapped[str | None] = mapped_column(String(255))
    comment_author_phone: Mapped[str | None] = mapped_column(String(64))

    status: Mapped[str] = mapped_column(String(16), nullable=False)
