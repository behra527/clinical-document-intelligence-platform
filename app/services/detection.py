from io import BytesIO
from zipfile import ZipFile, BadZipFile

SUPPORTED = {
    'pdf': 'application/pdf', 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt': 'text/plain', 'html': 'text/html', 'png': 'image/png',
    'jpeg': 'image/jpeg', 'tiff': 'image/tiff'
}

def detect_type(data: bytes) -> tuple[str, str]:
    if data.startswith(b'%PDF-'): return 'pdf', SUPPORTED['pdf']
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return 'png', SUPPORTED['png']
    if data.startswith(b'\xff\xd8\xff'): return 'jpeg', SUPPORTED['jpeg']
    if data.startswith((b'II*\x00', b'MM\x00*')): return 'tiff', SUPPORTED['tiff']
    if data.startswith(b'PK\x03\x04'):
        try:
            with ZipFile(BytesIO(data)) as archive:
                if 'word/document.xml' in archive.namelist(): return 'docx', SUPPORTED['docx']
        except BadZipFile: pass
        raise ValueError('Unsupported ZIP or Office file')
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('Unsupported binary file or non-UTF-8 text') from exc
    if '\x00' in text: raise ValueError('Binary content is not supported')
    import re
    if re.search(r'<!doctype\s+html|<html\b|<head\b|<body\b|<(?:h[1-6]|p|table|div)\b[^>]*>', text[:4096], re.I): return 'html', SUPPORTED['html']
    return 'txt', SUPPORTED['txt']
