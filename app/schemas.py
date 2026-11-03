from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):

    text: str = Field(min_length=1)


class NoteResponse(BaseModel):

    id: UUID

    text: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)