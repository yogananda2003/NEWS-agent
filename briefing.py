import json
from datetime import datetime

from fetcher.rss_fetcher import fetch_rss
from fetcher.newsapi_fetcher import fetch_newsapi
from fetcher.deduplicator import deduplicate
from processor.filter_agent import filter_and_rank
from processor.summarizer import summarize_stories
from delivery.formatter import format_briefing
from delivery.whatsapp import send_whatsapp

# Shared in-memory story cache — keyed by user_id, used by "more N" command
story_cache: dict = {}


def _load_sources() -> dict:
    with open("sources/domain_sources.json") as f:
        return json.load(f)


def run_briefing(user: dict):
    label = user.get("name") or user.get("user_id", "unknown")
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Briefing for {label}")

    domains = user.get("domains", [])
    profession = user.get("profession", "Professional")
    sources = _load_sources()

    raw = []
    for domain in domains:
        config = sources.get(domain, {})
        for url in config.get("rss_feeds", []):
            print(f"  RSS: {url}")
            raw.extend(fetch_rss(url))
        query = config.get("newsapi_query", "")
        if query:
            print(f"  NewsAPI: {domain}")
            raw.extend(fetch_newsapi(query))

    print(f"  Fetched: {len(raw)}  →  ", end="")
    deduped = deduplicate(raw)
    print(f"after dedup: {len(deduped)}")

    if not deduped:
        send_whatsapp(user["user_id"], "Nothing major in your domains today. Check back tomorrow!")
        _mark_briefed(user)
        return

    print("  Filtering with Grok...")
    ranked = filter_and_rank(deduped, profession, domains)
    print(f"  Ranked: {len(ranked)}")

    print("  Summarizing with Grok...")
    summarized = summarize_stories(ranked, profession, domains)

    story_cache[user["user_id"]] = summarized

    message = format_briefing(summarized, user.get("name", ""))
    success = send_whatsapp(user["user_id"], message)
    print(f"  {'Delivered' if success else 'Failed'}")

    if success:
        _mark_briefed(user)


def _mark_briefed(user: dict):
    try:
        from storage.db import mark_briefed_today
        mark_briefed_today(user["user_id"])
    except Exception:
        pass
