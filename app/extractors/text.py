from pathlib import Path
from bs4 import BeautifulSoup
from app.core.models import PageResult, TextBlock
from .base import BaseExtractor

class TextExtractor(BaseExtractor):
    def __init__(self, html=False):
        self.html = html

    def extract(self, path: Path):
        raw = path.read_text(encoding='utf-8-sig')
        blocks = []
        if self.html:
            soup = BeautifulSoup(raw, 'html.parser')
            title = soup.title.get_text(' ', strip=True) if soup.title else None
            for tag in soup(['script', 'style', 'noscript', 'template']):
                tag.decompose()
            # Keep semantic boundaries, rather than flattening an entire HTML page.
            root = soup.body or soup
            for node in root.find_all(['h1','h2','h3','h4','h5','h6','p','li','td','th','pre','blockquote']):
                if node.find_parent(['p','li','td','th','pre','blockquote']):
                    continue
                value = node.get_text(' ', strip=True)
                if not value:
                    continue
                kind = 'heading' if node.name.startswith('h') else 'table_cell' if node.name in ('td','th') else 'paragraph'
                blocks.append(TextBlock(block_id=f'p1-b{len(blocks)+1}', type=kind,
                    text=value, page_number=1, source_method='html',
                    source_location={'tag': node.name}))
            if not blocks:
                for line in root.get_text('\n', strip=True).splitlines():
                    if line.strip():
                        blocks.append(TextBlock(block_id=f'p1-b{len(blocks)+1}',
                            text=line.strip(), page_number=1, source_method='html'))
            metadata = {'title': title, 'page_count': 1, 'format': 'html'}
        else:
            for line_number, line in enumerate(raw.splitlines(), 1):
                if line.strip():
                    blocks.append(TextBlock(block_id=f'p1-b{len(blocks)+1}',
                        text=line.strip(), page_number=1, source_method='txt',
                        source_location={'line': line_number}))
            metadata = {'page_count': 1, 'format': 'txt', 'line_count': len(raw.splitlines())}
        return [PageResult(page_number=1, blocks=blocks)], metadata, []
