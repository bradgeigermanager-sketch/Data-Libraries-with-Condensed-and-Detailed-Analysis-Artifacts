"""
MODULE: infobox_mapper.py
LOCATION: backend/harvest/infobox_mapper.py
NOTATION: Structured Infobox Mapper
USE: Converts Wikipedia infobox dictionaries into normalized foundational_data.
"""

from typing import Dict, Any


# ------------------------------------------------------------
# NORMALIZATION UTILITIES
# ------------------------------------------------------------

def _normalize_key(key: str) -> str:
    """
    NOTATION: Key Normalizer.
    USE: Converts infobox keys to lowercase snake_case.
    """
    return (
        key.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("(", "")
        .replace(")", "")
    )


def _normalize_value(value: Any) -> Any:
    """
    NOTATION: Value Normalizer.
    USE: Cleans common Wikipedia formatting artifacts.
    """
    if isinstance(value, str):
        return value.strip()
    return value


# ------------------------------------------------------------
# DOMAIN-SPECIFIC MAPPERS
# ------------------------------------------------------------

def _map_person_infobox(infobox: Dict[str, Any]) -> Dict[str, Any]:
    """
    NOTATION: Person Infobox Mapper.
    USE: Extracts structured fields for biographies.
    """
    fields = {}

    for key, value in infobox.items():
        nk = _normalize_key(key)
        nv = _normalize_value(value)

        if nk in {"birth_date", "birth_place", "death_date", "death_place"}:
            fields[nk] = nv

        if nk in {"occupation", "known_for", "alma_mater"}:
            fields[nk] = nv

    return fields


def _map_organization_infobox(infobox: Dict[str, Any]) -> Dict[str, Any]:
    """
    NOTATION: Organization Infobox Mapper.
    USE: Extracts structured fields for companies, institutions, etc.
    """
    fields = {}

    for key, value in infobox.items():
        nk = _normalize_key(key)
        nv = _normalize_value(value)

        if nk in {"founded", "founder", "headquarters", "industry"}:
            fields[nk] = nv

    return fields


def _map_taxonomy_infobox(infobox: Dict[str, Any]) -> Dict[str, Any]:
    """
    NOTATION: Taxonomy Mapper.
    USE: Extracts structured fields for species, genera, families, etc.
    """
    fields = {}

    for key, value in infobox.items():
        nk = _normalize_key(key)
        nv = _normalize_value(value)

        if nk in {"kingdom", "phylum", "classis", "ordo", "familia", "genus", "species"}:
            fields[nk] = nv

    return fields


# ------------------------------------------------------------
# INFERRING INFOBOX TYPE
# ------------------------------------------------------------

def _infer_infobox_type(infobox: Dict[str, Any]) -> str:
    """
    NOTATION: Infobox Type Inference.
    USE: Determines which domain mapper to apply.
    """
    keys = {_normalize_key(k) for k in infobox.keys()}

    if "birth_date" in keys or "occupation" in keys:
        return "person"

    if "industry" in keys or "founded" in keys:
        return "organization"

    if "genus" in keys or "species" in keys:
        return "taxonomy"

    return "generic"


# ------------------------------------------------------------
# MAIN ENTRYPOINT
# ------------------------------------------------------------

def map_infobox(infobox: Dict[str, Any]) -> Dict[str, Any]:
    """
    NOTATION: Infobox Mapper Entrypoint.
    USE: Produces a structured foundational_data block from raw infobox dict.
    """

    if not infobox:
        return {}

    infobox_type = _infer_infobox_type(infobox)

    # Domain-specific mapping
    if infobox_type == "person":
        structured = _map_person_infobox(infobox)
    elif infobox_type == "organization":
        structured = _map_organization_infobox(infobox)
    elif infobox_type == "taxonomy":
        structured = _map_taxonomy_infobox(infobox)
    else:
        structured = {}

    # Always include normalized raw infobox
    normalized_raw = {
        _normalize_key(k): _normalize_value(v)
        for k, v in infobox.items()
    }

    return {
        "infobox_type": infobox_type,
        "structured_fields": structured,
        "raw_infobox": normalized_raw,
    }
