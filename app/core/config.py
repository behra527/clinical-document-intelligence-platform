import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv('CLINICAL_DATA_DIR', str(BASE_DIR / 'data'))).resolve()
MAX_UPLOAD_BYTES = int(os.getenv('MAX_UPLOAD_BYTES', str(20 * 1024 * 1024)))
API_KEY = os.getenv('CLINICAL_API_KEY', '')
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATA_DIR / "clinical.db"}')
DATA_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
