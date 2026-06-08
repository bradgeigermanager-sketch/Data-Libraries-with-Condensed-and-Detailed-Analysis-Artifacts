"""
MODULE: category_harvester.py
LOCATION: backend/harvest/category_harvester.py
NOTATION: Wikipedia Category Harvester
USE: Fetches category members and ingests them into the logic graph.
"""

from typing import Optional, List
from uuid import UUID

from backend.harvest.wikipedia_client import WikipediaClient
from backend.ingestion.engine import LogicIngestionEngine
from backend.ingestion.state_tracker import IngestionStateTracker
from backend.ingestion.normalize import normalize_source
from backend.ingestion.extract import extract_artifact_fields


class CategoryHarvester:
    """
    NOTATION: Category Harvester.
    USE: Bridges WikipediaClient → Normalization → Extraction → Ingestion.
    """

    def __init__(
        self,
        wiki: WikipediaClient,
        ingestion_engine: LogicIngestionEngine,
    ):
        self.wiki = wiki
        self.ingest = ingestion_engine

    # ------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------

    def harvest_category(
        self,
        category_name: str,
        max_pages: int = 50,
    ) -> IngestionStateTracker:
        """
        NOTATION: Category Harvest Entrypoint.
        USE: Fetches category members and ingests each page.

        RETURNS:
            IngestionStateTracker with full audit trail.
        """

        tracker = IngestionStateTracker()

        # Fetch category members
        titles = self.wiki.get_category_members(category_name, limit=max_pages)
        tracker.state.record_event("category_members_fetched", {"titles": titles})

        for title in titles:
            self._process_single_page(title, tracker)

        tracker.finalize()
        return tracker

    # ------------------------------------------------------------
    # INTERNAL PAGE PROCESSING
    # ------------------------------------------------------------

    def _process_single_page(self, title: str, tracker: IngestionStateTracker):
        """
        NOTATION: Page Processor.
        USE: Fetches summary + infobox, normalizes, extracts, ingests.
        """

        # Fetch summary + infobox
        page_data = self.wiki.get_page_summary_and_infobox(title)
        summary = page_data["summary"]
        infobox = page_data["infobox"]

        tracker.state.record_event(
            "page_fetched",
            {"title": title, "summary_len": len(summary), "infobox_keys": list(infobox.keys())},
        )

        # Normalize
        normalized = normalize_source(
            raw_text=summary,
            source_meta={
                "page_title": title,
                "infobox": infobox,
                "source_type": "wikipedia",
            },
        )
        tracker.log_normalization(normalized)

        # Extract canonical fields
        extracted = extract_artifact_fields(normalized)
        tracker.log_extraction(extracted)

        # Ingest
        artifact_id = self.ingest.process_source(
            raw_text=extracted["verbose_desc"],
            source_meta={
                "page_title": extracted["title"],
                "infobox": infobox,
                "source_type": "wikipedia",
                "artifact_category": extracted["artifact_category"],
                "syntax_language": extracted["syntax_language"],
            },
        )

        tracker.log_artifact_created(artifact_id)
