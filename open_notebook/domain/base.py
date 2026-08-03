"""
Open Notebook Light - Domain Base Models
Modul: open_notebook/domain/base.py
Zweck: Bereinigte Pydantic Basismodelle mit Hex-UUIDs ohne SurrealDB-Record-ID Parsing.
Version: 2.0.0-light
"""
__version__ = "2.0.0-light"

import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class ObjectModel(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
