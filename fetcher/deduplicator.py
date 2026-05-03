from typing import List, Dict
from urllib.parse import urlparse


def deduplicate(stories: List[Dict]) -> List[Dict]:
    seen_urls: set = set()
    seen_headlines: List[set] = []
    unique: List[Dict] = []

    for story in stories:
        url = story.get("url", "")
        headline = story.get("headline", "").lower().strip()

        parsed = urlparse(url)
        norm_url = (parsed.netloc + parsed.path).rstrip("/")

        if norm_url and norm_url in seen_urls:
            continue

        # Jaccard similarity check against all kept headlines
        words = set(headline.split())
        is_duplicate = False
        if len(words) > 3:
            for kept_words in seen_headlines:
                overlap = len(words & kept_words) / len(words | kept_words)
                if overlap > 0.55:
                    is_duplicate = True
                    break

        if is_duplicate:
            continue

        if norm_url:
            seen_urls.add(norm_url)
        seen_headlines.append(words)
        unique.append(story)

    return unique
