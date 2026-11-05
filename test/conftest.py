import os
import tempfile
import atexit

_tmp = tempfile.TemporaryDirectory()

os.environ["CLINICAL_DATA_DIR"] = _tmp.name
os.environ["CLINICAL_API_KEY"] = "test-key-only"


def cleanup_test_resources():
    from app.core.database import engine

    engine.dispose()
    _tmp.cleanup()


atexit.register(cleanup_test_resources)
