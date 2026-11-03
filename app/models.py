import uuid

from datetime import datetime, timezone

from sqlalchemy import Column, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Note(Base):

    __tablename__ = "notes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    text = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )