from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
class ArchivedDocument(Base):
    __tablename__ = 'archived_documents'
    document_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    archived_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
