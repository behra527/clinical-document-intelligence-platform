from pathlib import Path
import fitz
from PIL import Image
from app.core.models import PageResult, TextBlock
from .base import BaseExtractor
from .ocr import ocr_image

class PdfExtractor(BaseExtractor):
    def extract(self, path: Path):
        pages, warnings = [], []
        with fitz.open(path) as pdf:
            if pdf.needs_pass: raise ValueError('Password-protected PDF not supported')
            if len(pdf) > 100: raise ValueError('PDF exceeds 100-page limit')
            metadata = {k: v for k, v in pdf.metadata.items() if v and k in ('title', 'author', 'subject', 'keywords', 'creator', 'producer', 'creationDate', 'modDate')}
            metadata['page_count'] = len(pdf)
            metadata['format'] = 'pdf'
            for index, page in enumerate(pdf):
                blocks = []
                for block in page.get_text('blocks', sort=True):
                    if len(block) >= 7 and block[6] == 0 and str(block[4]).strip():
                        blocks.append(TextBlock(block_id=f'p{index+1}-b{len(blocks)+1}', text=str(block[4]).strip(), page_number=index+1, source_method='pymupdf', bbox=list(block[:4]), coordinate_system='pdf_points', source_location={'page': index+1}))
                # OCR fallback for pages with negligible native text.
                if sum(len(b.text.strip()) for b in blocks) < 20:
                    try:
                        pix = page.get_pixmap(matrix=fitz.Matrix(2,2), alpha=False)
                        image = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
                        pages.append(ocr_image(image, index+1, scale=2.0))
                    except Exception as exc:
                        warnings.append(f'Page {index+1}: OCR failed ({type(exc).__name__})')
                        pages.append(PageResult(page_number=index+1, blocks=blocks, warnings=['OCR failed']))
                else:
                    pages.append(PageResult(page_number=index+1, blocks=blocks))
        return pages, metadata, warnings
