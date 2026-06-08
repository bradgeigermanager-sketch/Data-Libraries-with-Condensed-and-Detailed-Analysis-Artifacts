"""
MODULE: wiki_extract.py
LOCATION: backend/harvest/wiki_extract.py
NOTATION: Wikipedia-specific extraction utilities.
USE: Converts Wikipedia summaries + infoboxes into LogicArtifact fields.
"""

from typing import Dict, Any


def extract_from_wikipedia(summary: str, infobox: Dict[str, Any], title: str) -> Dict[str, Any]:
    """
    NOTATION: Wikipedia Extractor.
    USE: Produces canonical LogicArtifact fields from Wikipedia page data.

    RETURNS:
        {
            "title": str,
            "condensed_logic": str,
            "verbose_desc": str,
            "foundational_data": dict,
            "artifact_category": str,
            "syntax_language": str
        }
    """

    clean_summary = summary.strip()

    # Build foundational data block
    foundational = {
        "source_type": "wikipedia",
        "infobox": infobox or {},
        "page_title": title,
    }

    return {
        "title": title,
        "condensed_logic": clean_summary[:280],
        "verbose_desc": clean_summary,
        "foundational_data": foundational,
        "artifact_category": "logic_node",
        "syntax_language": "text",
    }


def extract_infobox_fields(infobox: Dict[str, Any]) -> Dict[str, Any]:
    """
    NOTATION: Infobox Mapper.
    USE: Converts raw infobox dict into a normalized foundational_data block.

    This is intentionally minimal — future versions can map:
        - birth/death dates
        - locations
        - organizations
        - roles
        - taxonomies
        - scientific classifications
    """

    if not infobox:
        return {}

    normalized = {}

    for key, value in infobox.items():
        # Normalize keys to lowercase snake_case
        norm_key = key.lower().replace(" ", "_")
        normalized[norm_key] = value

    return normalized
