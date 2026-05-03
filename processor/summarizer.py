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
    "You are a professional news briefing writer. "
    "Be concise, factual, and direct. Write like you're texting a smart colleague. "
    "You always return valid JSON and nothing else."
)


def summarize_stories(stories: List[Dict], profession: str, domains: List[str]) -> List[Dict]:
    if not stories:
        return []

    to_summarize = [s for s in stories if s.get("importance") != "QUICK_HIT"]
    quick_hits = [s for s in stories if s.get("importance") == "QUICK_HIT"]

    if not to_summarize:
        return quick_hits

    stories_payload = [
        {
            "id": i,
            "headline": s["headline"],
            "source": s.get("source", ""),
            "raw": s.get("summary", "")[:300],
        }
        for i, s in enumerate(to_summarize)
    ]

    prompt = f"""User profile:
- Profession: {profession}
- Domains: {", ".join(domains)}

For each story below write:
1. "summary": Exactly 2 sentences. What happened. Key facts only. No jargon.
2. "why_it_matters": 1 sentence max. How this directly affects someone in this profession.

Rules:
- Do NOT repeat the headline.
- Do NOT be vague ("this could impact..."). Be specific.
- Write for a busy professional who has 10 seconds per story.

Return ONLY a valid JSON array:
[{{"id": <id>, "summary": "...", "why_it_matters": "..."}}]

Stories:
{json.dumps(stories_payload, indent=2)}"""

    try:
        response = get_client().chat.completions.create(
            model="grok-3",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content.strip()
        start, end = text.find("["), text.rfind("]") + 1
        summaries = json.loads(text[start:end])

        for item in summaries:
            idx = item.get("id")
            if idx is not None and 0 <= idx < len(to_summarize):
                to_summarize[idx]["summary"] = item.get("summary", "")
                to_summarize[idx]["why_it_matters"] = item.get("why_it_matters", "")

        return to_summarize + quick_hits

    except Exception as e:
        print(f"  Summarizer error: {e}")
        return to_summarize + quick_hits
