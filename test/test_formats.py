from pathlib import Path
import hashlib
import pytest
import fitz
from docx import Document
from PIL import Image, ImageDraw, ImageFont
from app.services.detection import detect_type
from app.services.pipeline import process_document

@pytest.fixture
def examples(tmp_path):
    result = {}
    text = 'Hemoglobin: 13.5 g/dL'
    result['txt'] = tmp_path / 'sample.txt'
    result['txt'].write_text('Clinical report\n\n' + text + '\n', encoding='utf-8')
    result['html'] = tmp_path / 'sample.html'
    result['html'].write_text('<html><head><title>Lab</title></head><body><h1>Clinical report</h1><p>' + text + '</p><script>secret</script></body></html>', encoding='utf-8')
    doc = Document()
    doc.add_heading('Clinical report', 1)
    doc.add_paragraph(text)
    doc.add_table(rows=1, cols=2).cell(0,0).text = 'Glucose'
    doc.core_properties.title = 'Clinical report'
    result['docx'] = tmp_path / 'sample.docx'
    doc.save(result['docx'])
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), text)
    result['pdf'] = tmp_path / 'sample.pdf'
    pdf.save(result['pdf'])
    pdf.close()
    image = Image.new('RGB', (1500, 300), 'white')
    draw = ImageDraw.Draw(image)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font = ImageFont.truetype(font_path, 46) if Path(font_path).exists() else ImageFont.load_default()
    draw.text((40,80), text, fill='black', font=font)
    for key, ext in [('png','png'),('jpeg','jpg'),('tiff','tiff')]:
        result[key] = tmp_path / ('sample.' + ext)
        image.save(result[key])
    scanned = fitz.open()
    p = scanned.new_page(width=750, height=150)
    p.insert_image(p.rect, stream=result['png'].read_bytes())
    result['scanned_pdf'] = tmp_path / 'scanned.pdf'
    scanned.save(result['scanned_pdf'])
    scanned.close()
    return result

@pytest.mark.parametrize('kind', ['txt','html','docx','pdf','png','jpeg','tiff','scanned_pdf'])
def test_pipeline_all_formats(examples, kind):
    path = examples[kind]
    data = path.read_bytes()
    detected, mime = detect_type(data)
    assert detected == ('pdf' if kind == 'scanned_pdf' else kind)
    result = process_document('test-id', path.name, mime, hashlib.sha256(data).hexdigest(), len(data), detected, path)
    assert result.status in ('completed', 'review_required')
    assert result.pages and result.pages[0].blocks
    assert result.metadata['detected_format'] == detected
    assert result.metadata['extraction_methods']
    assert all(block.block_id and block.source_method for page in result.pages for block in page.blocks)
    assert 'Hemoglobin' in ' '.join(b.text for p in result.pages for b in p.blocks)
    assert result.model_validate_json(result.model_dump_json()).document_id == 'test-id'


def test_html_script_removed(examples):
    from app.extractors.text import TextExtractor
    pages, metadata, _ = TextExtractor(html=True).extract(examples['html'])
    assert 'secret' not in ' '.join(b.text for b in pages[0].blocks)
    assert metadata['title'] == 'Lab'


def test_txt_block_ids_contiguous(examples):
    from app.extractors.text import TextExtractor
    pages, _, _ = TextExtractor().extract(examples['txt'])
    assert [b.block_id for b in pages[0].blocks] == ['p1-b1','p1-b2']
    assert pages[0].blocks[-1].source_location['line'] == 3


def test_docx_table_location(examples):
    from app.extractors.docx import DocxExtractor
    pages, _, _ = DocxExtractor().extract(examples['docx'])
    cells = [b for b in pages[0].blocks if b.type == 'table_cell']
    assert cells[0].source_location == {'row': 1, 'column': 1}


def test_reject_unsupported_binary():
    with pytest.raises(ValueError):
        detect_type(b'\x00\x01\x02\xff')

def test_scanned_pdf_coordinate_system(examples):
    from app.extractors.pdf import PdfExtractor
    pages, _, _ = PdfExtractor().extract(examples['scanned_pdf'])
    assert pages[0].blocks
    assert all(b.coordinate_system == 'pdf_points' for b in pages[0].blocks)
    assert all(len(b.bbox) == 4 for b in pages[0].blocks)


def test_pdf_native_coordinate_system(examples):
    from app.extractors.pdf import PdfExtractor
    pages, _, _ = PdfExtractor().extract(examples['pdf'])
    assert pages[0].blocks[0].coordinate_system == 'pdf_points'
    assert pages[0].blocks[0].source_method == 'pymupdf'
