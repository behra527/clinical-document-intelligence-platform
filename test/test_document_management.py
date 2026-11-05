import os
os.environ.setdefault('CLINICAL_API_KEY', 'test-key-only')
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
from app.api.archive_model import ArchivedDocument

def test_management_routes_registered():
    paths = app.openapi()['paths']
    assert '/api/v1/documents/{document_id}/metadata' in paths
    assert '/api/v1/documents/{document_id}/review-status' in paths
    assert 'delete' in paths['/api/v1/documents/{document_id}']
    assert '/api/v1/documents/archived/list' in paths
    assert '/api/v1/documents/{document_id}/restore' in paths
