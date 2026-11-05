"""Non-destructive document management. Archive keeps original, result and audit."""
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from app.core.database import SessionLocal, DocumentRecord, AuditRecord
from app.core.models import DocumentResult
from app.main import require_api_key
from app.api.archive_model import ArchivedDocument

router = APIRouter(prefix='/api/v1/documents', tags=['Document management'], dependencies=[Depends(require_api_key)])

class RenameRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)

class ReviewStatusRequest(BaseModel):
    status: str

def _record(db, document_id):
    record = db.get(DocumentRecord, document_id)
    if record is None or db.get(ArchivedDocument, document_id) is not None:
        raise HTTPException(404, 'Document not found')
    return record

@router.patch('/{document_id}/metadata', response_model=DocumentResult)
def rename_document(document_id: str, request: RenameRequest):
    name = Path(request.filename.replace('\\', '/')).name.strip()
    if name in ('', '.', '..') or len(name) > 255:
        raise HTTPException(422, 'Invalid filename')
    with SessionLocal() as db:
        record = _record(db, document_id)
        result = DocumentResult.model_validate_json(record.result_json)
        record.filename = result.filename = name
        record.result_json = result.model_dump_json()
        db.add(AuditRecord(document_id=document_id, action='document_renamed'))
        db.commit()
        return result

@router.post('/{document_id}/review-status', response_model=DocumentResult)
def mark_pending(document_id: str, request: ReviewStatusRequest):
    if request.status != 'pending':
        raise HTTPException(422, 'Only pending status is supported')
    with SessionLocal() as db:
        record = _record(db, document_id)
        if record.review_status in ('approved', 'rejected'):
            raise HTTPException(409, 'Finalized document cannot be reopened')
        result = DocumentResult.model_validate_json(record.result_json)
        record.review_status = result.review_status = 'pending'
        record.result_json = result.model_dump_json()
        db.add(AuditRecord(document_id=document_id, action='manual_review_requested'))
        db.commit()
        return result

@router.delete('/{document_id}', status_code=204)
def archive_document(document_id: str):
    """Soft-delete: hides document from active list; retains evidence and audit."""
    with SessionLocal() as db:
        _record(db, document_id)
        db.add(ArchivedDocument(document_id=document_id))
        db.add(AuditRecord(document_id=document_id, action='document_archived'))
        db.commit()

@router.get('/archived/list')
def list_archived():
    with SessionLocal() as db:
        records = db.execute(select(DocumentRecord).join(ArchivedDocument, DocumentRecord.id == ArchivedDocument.document_id).order_by(ArchivedDocument.archived_at.desc())).scalars().all()
        return [{'document_id': r.id, 'filename': r.filename, 'status': r.status, 'review_status': r.review_status} for r in records]

@router.post('/{document_id}/restore', response_model=DocumentResult)
def restore_document(document_id: str):
    with SessionLocal() as db:
        record = db.get(DocumentRecord, document_id)
        archived = db.get(ArchivedDocument, document_id)
        if record is None or archived is None:
            raise HTTPException(404, 'Archived document not found')
        db.delete(archived)
        db.add(AuditRecord(document_id=document_id, action='document_restored'))
        db.commit()
        return DocumentResult.model_validate_json(record.result_json)
