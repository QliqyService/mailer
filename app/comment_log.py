from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CommentDeliveryLog, Status
from app.schemas import CommentCreatedEmail


class CommentLogRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, payload: CommentCreatedEmail, status: Status) -> None:
        row = CommentDeliveryLog(
            created_at=payload.created_at,
            form_id=payload.form_id,
            form_title=payload.form_title,
            form_public_url=payload.form_public_url,
            comment_id=payload.comment_id,
            comment_title=payload.comment_title,
            comment_text=payload.comment_text,
            comment_author_first_name=payload.comment_author_first_name,
            comment_author_last_name=payload.comment_author_last_name,
            comment_author_phone=payload.comment_author_phone,
            status=status,
        )

        self.session.add(row)
        await self.session.commit()
