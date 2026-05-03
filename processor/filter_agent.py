import json
import os
import httpx
from openai import OpenAI
from typing import List, Dict

from utils.ssl_helper import get_ca_bundle

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
            http_client=httpx.Client(verify=get_ca_bundle()),
        )
    return _client


SYSTEM_PROMPT = (
    "You are a professional news editor with deep expertise across all industries. "
    "Your job is to filter and rank news stories for a specific professional. "
    "You always return valid JSON and nothing else."
)


def filter_and_rank(stories: List[Dict], profession: str, domains: List[str]) -> List[Dict]:
    if not stories:
        return []

    stories_payload = [
        {
            "id": i,
            "headline": s["headline"],
            "source": s.get("source", ""),
            "summary": s.get("summary", "")[:200],
        }
        for i, s in enumerate(stories)
    ]

    prompt = f"""User profile:
- Profession: {profession}
- Domains: {", ".join(domains)}

You have {len(stories)} news stories from the last 24 hours. Do the following:

1. Remove stories that are: clickbait, sponsored/PR, pure opinion, duplicates, or unrelated to the user's domains.
2. Rank each kept story by importance:
   - BREAKING  → directly affects the user's work today
   - MAJOR     → industry-wide shift, widely discussed
   - MODERATE  → good to know, not urgent
   - QUICK_HIT → minor update, one line is enough
3. Keep at most 12 stories (max 2 BREAKING, 4 MAJOR, 4 MODERATE, remaining as QUICK_HIT).
4. Sort by importance: BREAKING first, then MAJOR, MODERATE, QUICK_HIT.

Return ONLY a valid JSON array:
[{{"id": <original_id>, "importance": "BREAKING|MAJOR|MODERATE|QUICK_HIT"}}]

Stories:
{json.dumps(stories_payload, indent=2)}"""

    try:
        response = get_client().chat.completions.create(
            model="grok-3",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content.strip()
        start, end = text.find("["), text.rfind("]") + 1
        ranked = json.loads(text[start:end])

        result = []
        for item in ranked:
            idx = item.get("id")
            if idx is not None and 0 <= idx < len(stories):
                story = stories[idx].copy()
                story["importance"] = item["importance"]
                result.append(story)

        return result

    except Exception as e:
        print(f"  Filter agent error: {e}")
        for s in stories[:12]:
            s.setdefault("importance", "MODERATE")
        return stories[:12]
