"""
MODULE: extract.py
LOCATION: backend/ingestion/extract.py
NOTATION: Extraction utilities for ingestion.
USE: Converts normalized text into LogicArtifact-ready fields.
"""

from typing import Dict, Any


def extract_artifact_fields(normalized: Dict[str, Any]) -> Dict[str, Any]:
    """
    NOTATION: Artifact Extractor.
    USE: Produces the canonical fields required to build a LogicArtifact.

    EXPECTED RETURN:
        {
            "title": str,
            "condensed_logic": str,
            "verbose_desc": str,
            "foundational_data": dict,
            "artifact_category": str,
            "syntax_language": str
        }
    """

    text = normalized["clean_text"]
    title = normalized["title"]
    meta = normalized["metadata"]

    return {
        "title": title,
        "condensed_logic": text[:280],
        "verbose_desc": text,
        "foundational_data": {"source": meta},
        "artifact_category": meta.get("artifact_category", "logic_node"),
        "syntax_language": meta.get("syntax_language", "text"),
    }
