import feedparser
from datetime import datetime, timezone, timedelta
from typing import List, Dict


def fetch_rss(feed_url: str, hours: int = 24) -> List[Dict]:
    stories = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    try:
        feed = feedparser.parse(feed_url)
        source_name = feed.feed.get("title", feed_url)

        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

            if published and published < cutoff:
                continue

            headline = entry.get("title", "").strip()
            if not headline:
                continue

            stories.append({
                "headline": headline,
                "url": entry.get("link", ""),
                "source": source_name,
                "published_at": published.isoformat() if published else None,
                "summary": (entry.get("summary") or "")[:500],
            })

    except Exception as e:
        print(f"  RSS fetch error [{feed_url}]: {e}")

    return stories
