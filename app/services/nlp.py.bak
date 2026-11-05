import re
from app.core.models import ClinicalEntity, PageResult

# Candidate detection only: not a clinical interpretation or medical diagnosis.
LAB = re.compile(r'\b(?P<name>hemoglobin|white blood cells|platelets|blood glucose|glucose|cholesterol|creatinine|sodium|potassium)\s*[:=]\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>g/dL|mg/dL|mmol/L|cells/uL|/uL)?\b', re.I)
VITAL = re.compile(r'\b(?P<name>blood pressure|heart rate|temperature)\s*[:=]\s*(?P<value>\d+(?:/\d+)?(?:\.\d+)?)\s*(?P<unit>mmHg|bpm|C|°C)?\b', re.I)
DIAGNOSIS = re.compile(r'\bdiagnosis\s*[:=]\s*(?P<value>[^\n;]+)', re.I)
MEDICATION = re.compile(r'\bmedication\s*[:=]\s*(?P<value>[^\n;]+)', re.I)
PATTERNS = [('lab_value', LAB), ('vital_sign', VITAL), ('diagnosis', DIAGNOSIS), ('medication', MEDICATION)]


def extract_candidates(pages: list[PageResult]):
    results = []
    for page in pages:
        for block in page.blocks:
            for label, pattern in PATTERNS:
                for match in pattern.finditer(block.text):
                    results.append(ClinicalEntity(label=label, text=match.group(),
                        block_id=block.block_id, start=match.start(), end=match.end()))
    return results
