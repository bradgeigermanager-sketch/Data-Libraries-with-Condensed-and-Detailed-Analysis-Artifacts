"""
MODULE: wikipedia_client.py
LOCATION: backend/harvest/wikipedia_client.py
NOTATION: MediaWiki API Client
USE: Fetches category members, page summaries, and infobox metadata.
"""

import requests
from typing import List, Dict, Any, Optional


class WikipediaClient:
    """
    NOTATION: MediaWiki Client.
    USE: Provides typed access to Wikipedia categories and pages.
    """

    API_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self, user_agent: str = "LogicHarvester/1.0"):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    # ------------------------------------------------------------
    # CATEGORY MEMBERS
    # ------------------------------------------------------------

    def get_category_members(self, category: str, limit: int = 100) -> List[str]:
        """
        NOTATION: Category Member Fetcher.
        USE: Returns page titles in a given category.
        """
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": limit,
            "format": "json",
        }

        resp = self.session.get(self.API_URL, params=params)
        data = resp.json()

        members = data.get("query", {}).get("categorymembers", [])
        return [m["title"] for m in members]

    # ------------------------------------------------------------
    # PAGE SUMMARY + INFOBOX
    # ------------------------------------------------------------

    def get_page_summary_and_infobox(self, title: str) -> Dict[str, Any]:
        """
        NOTATION: Page Data Fetcher.
        USE: Retrieves summary text + infobox metadata for a page.
        """
        params = {
            "action": "query",
            "prop": "extracts|pageprops",
            "titles": title,
            "exintro": 1,
            "explaintext": 1,
            "format": "json",
        }

        resp = self.session.get(self.API_URL, params=params)
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})

        return {
            "summary": page.get("extract", "") or "",
            "infobox": page.get("pageprops", {}) or {},
        }

    # ------------------------------------------------------------
    # FULL PAGE FETCH (optional)
    # ------------------------------------------------------------

    def get_full_page_html(self, title: str) -> str:
        """
        NOTATION: Full HTML Fetcher.
        USE: Retrieves the rendered HTML of a Wikipedia page.
        """
        params = {
            "action": "parse",
            "page": title,
            "prop": "text",
            "format": "json",
        }

        resp = self.session.get(self.API_URL, params=params)
        data = resp.json()

        html = data.get("parse", {}).get("text", {}).get("*", "")
        return html
