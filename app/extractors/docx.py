from pathlib import Path
from docx import Document
from app.core.models import PageResult, TextBlock
from .base import BaseExtractor

class DocxExtractor(BaseExtractor):
    def extract(self, path: Path):
        doc = Document(path)
        blocks = []
        for item in doc.element.body.iterchildren():
            if item.tag.endswith('}p'):
                from docx.text.paragraph import Paragraph
                para = Paragraph(item, doc)
                if para.text.strip():
                    blocks.append(TextBlock(block_id=f'p1-b{len(blocks)+1}', type='heading' if para.style and para.style.name.startswith('Heading') else 'paragraph', text=para.text, page_number=1, source_method='docx', source_location={'paragraph_index': len(blocks)+1}))
            elif item.tag.endswith('}tbl'):
                from docx.table import Table
                table = Table(item, doc)
                for row_index, row in enumerate(table.rows):
                    for col_index, cell in enumerate(row.cells):
                        if cell.text.strip():
                            blocks.append(TextBlock(block_id=f'p1-b{len(blocks)+1}', type='table_cell', text=cell.text, page_number=1, source_method='docx', source_location={'row': row_index+1, 'column': col_index+1}))
        props = doc.core_properties
        metadata = {'title': props.title or None, 'author': props.author or None, 'subject': props.subject or None, 'keywords': props.keywords or None, 'created': props.created.isoformat() if props.created else None, 'modified': props.modified.isoformat() if props.modified else None, 'page_count': 1, 'format': 'docx'}
        return [PageResult(page_number=1, blocks=blocks)], metadata, ['DOCX page number is logical (1); exact pagination requires a rendering engine']
