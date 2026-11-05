from app.core.models import PageResult, TextBlock
from app.services.nlp import extract_candidates
from app.services.pipeline import process_document


def test_candidate_offsets_and_provenance():
    lines = ['Hemoglobin: 13.5 g/dL', 'Blood Pressure: 120/80 mmHg',
             'Diagnosis: Hypertension', 'Medication: Amlodipine 5 mg']
    page = PageResult(page_number=1, blocks=[TextBlock(block_id=f'p1-b{i}',
        page_number=1, text=line, source_method='tesseract', confidence=.96,
        bbox=[10, i*30, 200, i*30+20]) for i, line in enumerate(lines, 1)])
    entities = extract_candidates([page])
    assert {e.label for e in entities} == {'lab_value', 'vital_sign', 'diagnosis', 'medication'}
    for entity in entities:
        block = next(b for b in page.blocks if b.block_id == entity.block_id)
        assert block.text[entity.start:entity.end] == entity.text


def test_nonclinical_text_has_no_entities():
    page = PageResult(page_number=1, blocks=[TextBlock(block_id='p1-b1',
        page_number=1, text='Bug report: HTTP 401 unauthorized', source_method='pymupdf')])
    assert extract_candidates([page]) == []
