"""
MODULE: harvester_orchestrator.py
LOCATION: backend/harvest/harvester_orchestrator.py
NOTATION: High-level harvesting orchestrator
USE: Coordinates WikipediaClient → CategoryHarvester → IngestionEngine.
"""

from typing import List, Dict, Any
from uuid import UUID

from backend.harvest.wikipedia_client import WikipediaClient
from backend.harvest.category_harvester import CategoryHarvester
from backend.ingestion.engine import LogicIngestionEngine
from backend.ingestion.resolver import ArtifactResolver
from backend.ingestion.state_tracker import IngestionStateTracker


class HarvesterOrchestrator:
    """
    NOTATION: Harvest Orchestrator.
    USE: Provides a unified interface for multi-category harvesting jobs.
    """

    def __init__(
        self,
        wiki_client: WikipediaClient,
        ingestion_engine: LogicIngestionEngine,
        resolver: ArtifactResolver,
    ):
        self.wiki = wiki_client
        self.ingest = ingestion_engine
        self.resolver = resolver

    # ------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------

    def harvest_categories(
        self,
        categories: List[str],
        max_pages_per_category: int = 50,
    ) -> Dict[str, IngestionStateTracker]:
        """
        NOTATION: Multi-Category Harvest Entrypoint.
        USE: Runs harvesting for each category and returns a tracker per category.
        """

        results = {}

        for category in categories:
            harvester = CategoryHarvester(
                wiki=self.wiki,
                ingestion_engine=self.ingest,
            )

            tracker = harvester.harvest_category(
                category_name=category,
                max_pages=max_pages_per_category,
            )

            results[category] = tracker

        return results

    # ------------------------------------------------------------
    # SINGLE CATEGORY WRAPPER
    # ------------------------------------------------------------

    def harvest_single_category(
        self,
        category: str,
        max_pages: int = 50,
    ) -> IngestionStateTracker:
        """
        NOTATION: Single Category Wrapper.
        USE: Convenience method for admin UI or agentic triggers.
        """

        harvester = CategoryHarvester(
            wiki=self.wiki,
            ingestion_engine=self.ingest,
        )

        return harvester.harvest_category(
            category_name=category,
            max_pages=max_pages,
        )

    # ------------------------------------------------------------
    # SCHEDULED / BATCH JOBS
    # ------------------------------------------------------------

    def run_batch_job(
        self,
        job_name: str,
        categories: List[str],
        max_pages_per_category: int = 50,
    ) -> Dict[str, Any]:
        """
        NOTATION: Batch Job Runner.
        USE: Runs a named harvesting job and returns a structured summary.
        """

        job_results = self.harvest_categories(
            categories=categories,
            max_pages_per_category=max_pages_per_category,
        )

        summary = {
            "job_name": job_name,
            "categories": categories,
            "results": {
                cat: {
                    "created_artifacts": len(tr.state.created_artifacts),
                    "created_relationships": len(tr.state.created_relationships),
                    "resolver_hits": len(tr.state.resolver_hits),
                    "resolver_misses": len(tr.state.resolver_misses),
                    "contradictions": len(tr.state.contradictions_detected),
                }
                for cat, tr in job_results.items()
            },
        }

        return summary
