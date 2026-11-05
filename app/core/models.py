from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field

class TextBlock(BaseModel):
    block_id: str
    type: Literal['paragraph', 'table_cell', 'heading'] = 'paragraph'
    text: str
    page_number: int
    source_method: str
    bbox: list[float] | None = None
    confidence: float | None = None
    coordinate_system: str | None = None
    source_location: dict = Field(default_factory=dict)

class PageResult(BaseModel):
    page_number: int
    blocks: list[TextBlock] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

class ClinicalEntity(BaseModel):
    label: str
    text: str
    block_id: str
    start: int
    end: int
    status: Literal['candidate', 'verified', 'rejected'] = 'candidate'
    normalized: dict = Field(default_factory=dict)
    corrected_text: str | None = None
    reviewer_note: str | None = None

class DocumentResult(BaseModel):
    document_id: str
    status: Literal['completed', 'review_required', 'failed']
    filename: str
    mime_type: str
    sha256: str
    size_bytes: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = Field(default_factory=dict)
    pages: list[PageResult] = Field(default_factory=list)
    clinical_entities: list[ClinicalEntity] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    extraction_version: str = '1.1.0'
    review_status: Literal['not_required', 'pending', 'approved', 'rejected'] = 'not_required'
