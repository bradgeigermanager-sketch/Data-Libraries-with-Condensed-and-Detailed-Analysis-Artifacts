"""
MODULE: normalize.py
LOCATION: backend/ingestion/normalize.py
NOTATION: Normalization utilities for ingestion.
USE: Cleans and standardizes raw text + metadata before extraction.
"""

from typing import Dict, Any


def normalize_source(raw_text: str, source_meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    NOTATION: Source Normalizer.
    USE: Produces a clean, predictable structure for extraction.

    RETURNS:
        {
            "clean_text": str,
            "title": str,
            "metadata": dict
        }
    """

    clean_text = raw_text.strip()

    title = (
        source_meta.get("page_title")
        or source_meta.get("title")
        or "Untitled"
    ).strip()

    return {
        "clean_text": clean_text,
        "title": title,
        "metadata": source_meta,
    }
