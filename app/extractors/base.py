from abc import ABC, abstractmethod
from pathlib import Path
from app.core.models import PageResult

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, path: Path) -> tuple[list[PageResult], dict, list[str]]:
        """Extract pages, document metadata, and warnings."""
