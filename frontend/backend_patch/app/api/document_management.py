"""Document management routes; attach with app.include_router(document_management_router)."""
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from app.core.config import DATA_DIR
from app.core.database import SessionLocal, DocumentRecord, AuditRecord
from app.core.models import DocumentResult

from fastapi import Header
from app.core.config import API_KEY
import secrets

def require_key(x_api_key: str | None = Header(default=None)):
    if not API_KEY:
        raise HTTPException(503, 'CLINICAL_API_KEY must be configured')
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(401, 'Invalid API key')

router = APIRouter(prefix='/api/v1/documents', dependencies=[Depends(require_key)])

class RenameDocument(BaseModel):
    filename: str = Field(min_length=1, max_length=255)

class SetReviewStatus(BaseModel):
    status: str

@router.patch('/{document_id}/metadata', response_model=DocumentResult)
def rename_document(document_id: str, payload: RenameDocument):
    name = payload.filename.strip()
    if not name or name in ('.', '..') or '/' in name or '\\' in name or any(ord(c) < 32 for c in name):
        raise HTTPException(422, 'Invalid filename')
    with SessionLocal() as db:
        record = db.get(DocumentRecord, document_id)
        if record is None:
            raise HTTPException(404, 'Document not found')
        old_suffix = Path(record.filename).suffix.lower()
        if Path(name).suffix.lower() != old_suffix:
            raise HTTPException(422, 'File extension cannot be changed')
        result = DocumentResult.model_validate_json(record.result_json)
        result.filename = name
        record.filename = name
        record.result_json = result.model_dump_json()
        db.add(AuditRecord(document_id=document_id, action='document_renamed'))
        db.commit()
        return result

@router.post('/{document_id}/review-status', response_model=DocumentResult)
def set_review_status(document_id: str, payload: SetReviewStatus):
    if payload.status != 'pending':
        raise HTTPException(422, 'Only pending review status can be requested')
    with SessionLocal() as db:
        record = db.get(DocumentRecord, document_id)
        if record is None:
            raise HTTPException(404, 'Document not found')
        if record.review_status in ('approved', 'rejected'):
            raise HTTPException(409, 'Finalized documents cannot be reopened via this endpoint')
        result = DocumentResult.model_validate_json(record.result_json)
        result.review_status = 'pending'
        record.review_status = 'pending'
        record.result_json = result.model_dump_json()
        db.add(AuditRecord(document_id=document_id, action='review_requested'))
        db.commit()
        return result

@router.delete('/{document_id}', status_code=204)
def delete_document(document_id: str):
    with SessionLocal() as db:
        record = db.get(DocumentRecord, document_id)
        if record is None:
            raise HTTPException(404, 'Document not found')
        uploads_dir = (DATA_DIR / 'uploads').resolve()
        path = Path(record.storage_path).resolve()
        if path.parent != uploads_dir or path.name != document_id:
            raise HTTPException(403, 'Unsafe storage path')
        # Keep a durable audit entry even after deleting the document row.
        # Existing AuditRecord rows may have a foreign key to DocumentRecord;
        # remove dependent audit rows if necessary, after copying an audit to logs.
        import logging
        logging.getLogger(__name__).warning('Document deleted: %s', document_id)
        for item in db.scalars(select(AuditRecord).where(AuditRecord.document_id == document_id)).all():
            db.delete(item)
        db.delete(record)
        db.commit()
        try:
            path.unlink(missing_ok=True)
        except OSError:
            logging.getLogger(__name__).exception('Orphaned upload after deletion: %s', document_id)
