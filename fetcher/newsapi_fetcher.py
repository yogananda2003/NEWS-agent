import os
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict

from utils.ssl_helper import get_ca_bundle


def fetch_newsapi(query: str, hours: int = 24) -> List[Dict]:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        print("  NEWSAPI_KEY not set, skipping NewsAPI fetch")
        return []

    from_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    params = {
        "q": query,
        "from": from_time,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 30,
        "apiKey": api_key,
    }

    try:
        response = requests.get(
            "https://newsapi.org/v2/everything", params=params, timeout=15,
            verify=get_ca_bundle()
        )
        response.raise_for_status()
        data = response.json()

        stories = []
        for article in data.get("articles", []):
            headline = (article.get("title") or "").strip()
            if not headline or headline == "[Removed]":
                continue

            stories.append({
                "headline": headline,
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", ""),
                "published_at": article.get("publishedAt", ""),
                "summary": (article.get("description") or "")[:500],
            })

        return stories

    except Exception as e:
        print(f"  NewsAPI fetch error: {e}")
        return []
