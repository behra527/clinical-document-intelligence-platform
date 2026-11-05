from fastapi.testclient import TestClient
from app.main import app
from app.services.normalization import normalize_candidate

HEADERS = {'X-API-Key': 'test-key-only'}


def test_normalization():
    assert normalize_candidate('lab_value', 'Hemoglobin: 13.5 g/dL') == {'name': 'Hemoglobin', 'value': 13.5, 'unit': 'g/dL'}
    assert normalize_candidate('vital_sign', 'Blood Pressure: 120/80 mmHg')['value'] == '120/80'
    assert normalize_candidate('medication', 'Medication: Amlodipine 5 mg')['dose'] == 5.0


def test_review_entity_preserves_source():
    with TestClient(app) as client:
        response = client.post('/api/v1/documents', files={'file': ('r.txt', b'Hemoglobin: 13.5 g/dL\nMedication: Amlodipine 5 mg\nFrequency: Once daily', 'text/plain')}, headers=HEADERS)
        assert response.status_code == 201, response.text
        doc = response.json()
        assert len(doc['clinical_entities']) == 2
        assert doc['clinical_entities'][1]['normalized']['frequency'] == 'Once daily'
        doc_id = doc['document_id']
        updated = client.patch(f'/api/v1/documents/{doc_id}/entities/0', json={'decision': 'verified', 'corrected_text': 'Hemoglobin: 13.6 g/dL', 'note': 'Compared with source'}, headers=HEADERS)
        assert updated.status_code == 200, updated.text
        ent = updated.json()['clinical_entities'][0]
        assert ent['text'] == 'Hemoglobin: 13.5 g/dL'
        assert ent['corrected_text'] == 'Hemoglobin: 13.6 g/dL'
        assert ent['normalized']['value'] == 13.6
        assert ent['status'] == 'verified'
        assert updated.json()['review_status'] == 'pending'
        duplicate = client.patch(f'/api/v1/documents/{doc_id}/entities/0', json={'decision': 'rejected'}, headers=HEADERS)
        assert duplicate.status_code == 409
        missing = client.patch(f'/api/v1/documents/{doc_id}/entities/99', json={'decision': 'rejected'}, headers=HEADERS)
        assert missing.status_code == 404
