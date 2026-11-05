from fastapi.testclient import TestClient
from app.main import app


def test_upload_txt_and_provenance():
    with TestClient(app) as client:
        headers = {'X-API-Key': 'test-key-only'}
        response = client.post('/api/v1/documents', files={'file': ('report.txt', b'Hemoglobin: 13.5 g/dL\nBlood pressure: 120/80', 'text/plain')}, headers=headers)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data['status'] == 'completed'
        assert data['pages'][0]['blocks'][0]['source_method'] == 'txt'
        assert len(data['clinical_entities']) == 2
        retrieved = client.get(f"/api/v1/documents/{data['document_id']}", headers=headers)
        assert retrieved.status_code == 200


def test_auth_required():
    with TestClient(app) as client:
        response = client.get('/api/v1/documents')
        assert response.status_code == 401


def test_binary_rejected():
    with TestClient(app) as client:
        response = client.post('/api/v1/documents', files={'file': ('x.bin', b'\x00\x01\x02', 'application/octet-stream')}, headers={'X-API-Key': 'test-key-only'})
        assert response.status_code == 415
