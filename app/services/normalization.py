"""Conservative, rule-based normalization of OCR/NLP candidate text."""
import re
from typing import Any

LAB_VITAL = re.compile(r'^\s*(?P<name>[^:=]+?)\s*[:=]\s*(?P<value>\d+(?:/\d+)?(?:\.\d+)?)\s*(?P<unit>g/dL|mg/dL|mmol/L|cells/uL|/uL|mmHg|bpm|°C|C)?\s*$', re.I)
MED = re.compile(r'^\s*medication\s*[:=]\s*(?P<drug>.+?)\s+(?P<dose>\d+(?:\.\d+)?)\s*(?P<unit>mg|mcg|g|mL)\s*$', re.I)
FREQUENCY = re.compile(r'^\s*frequency\s*[:=]\s*(?P<frequency>.+?)\s*$', re.I)


def normalize_candidate(label: str, text: str) -> dict[str, Any]:
    if label in ('lab_value', 'vital_sign'):
        m = LAB_VITAL.fullmatch(text)
        if not m:
            return {}
        raw_value = m['value']
        value = raw_value if '/' in raw_value else float(raw_value)
        return {'name': m['name'].strip(), 'value': value, 'unit': m['unit']}
    if label == 'diagnosis':
        return {'name': text.split(':', 1)[-1].strip()} if ':' in text else {}
    if label == 'medication':
        m = MED.fullmatch(text)
        if m:
            return {'name': m['drug'].strip(), 'dose': float(m['dose']), 'dose_unit': m['unit']}
        return {'name': text.split(':', 1)[-1].strip()} if ':' in text else {}
    return {}


def find_frequency(pages) -> str | None:
    """Extract explicit frequency text only; do not infer dosage schedules."""
    for page in pages:
        for block in page.blocks:
            match = FREQUENCY.fullmatch(block.text)
            if match:
                return match['frequency'].strip()
    return None
