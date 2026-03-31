from __future__ import annotations

import re
from typing import List, Sequence


def normalize_text(text: str) -> str:
    return text.strip().lower()


def parse_list(value: object) -> List[str]:
    if isinstance(value, str):
        return [item.strip().lower() for item in value.split(",") if item.strip()]
    if isinstance(value, Sequence):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    return []


def parse_symptoms(text: str) -> List[str]:
    cleaned = normalize_text(text)
    if not cleaned:
        return []

    # Break by commas and coordinating words to preserve symptom phrases.
    parts = [p.strip() for p in re.split(r",|\band\b|\bwith\b|\bplus\b", cleaned) if p.strip()]

    expanded: List[str] = []
    for part in parts:
        expanded.append(part)
        tokens = [token for token in re.split(r"\s+", part) if token]
        if len(tokens) <= 3:
            expanded.extend(tokens)

    seen = set()
    deduped: List[str] = []
    for symptom in expanded:
        if symptom not in seen:
            seen.add(symptom)
            deduped.append(symptom)
    return deduped
