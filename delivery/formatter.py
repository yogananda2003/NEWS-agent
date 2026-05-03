from datetime import datetime
from typing import List, Dict

IMPORTANCE_CONFIG = {
    "BREAKING": {"emoji": "🔴", "label": "BREAKING"},
    "MAJOR":    {"emoji": "🟠", "label": "MAJOR"},
    "MODERATE": {"emoji": "🟡", "label": "MODERATE"},
}


def format_briefing(stories: List[Dict], user_name: str) -> str:
    today = datetime.now().strftime("%A, %B %d, %Y").replace(" 0", " ")
    non_quick = [s for s in stories if s.get("importance") != "QUICK_HIT"]
    quick_hits = [s for s in stories if s.get("importance") == "QUICK_HIT"]

    total = len(stories)
    read_time = max(1, round(total * 0.35))

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "📰 *YOUR DAILY BRIEFING*",
        f"📅 {today}",
        f"⏱ ~{read_time} min read · {total} stories",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    current_importance = None
    story_num = 1

    for story in non_quick:
        imp = story.get("importance", "MODERATE")
        config = IMPORTANCE_CONFIG.get(imp, IMPORTANCE_CONFIG["MODERATE"])

        if imp != current_importance:
            if current_importance is not None:
                lines.append("")
                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
                lines.append("")
            lines.append(f"{config['emoji']} *{config['label']}*")
            lines.append("")
            current_importance = imp

        headline = story.get("headline", "")
        source = story.get("source", "")
        summary = story.get("summary", "")
        why = story.get("why_it_matters", "")
        url = story.get("url", "")

        lines.append(f"*{story_num}. {headline}*")
        if source:
            lines.append(f"_{source}_")
        if summary:
            lines.append(summary)
        if why:
            lines.append(f"💼 _{why}_")
        if url:
            lines.append(f"🔗 {url}")
        lines.append("")
        story_num += 1

    if quick_hits:
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("⚡ *QUICK HITS*")
        for qh in quick_hits[:5]:
            src = f" _{qh.get('source', '')}_" if qh.get("source") else ""
            lines.append(f"• {qh.get('headline', '')}{src}")
        lines.append("")

    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "💬 Reply *more [#]* for full story",
        "⚙️ Reply *stop* to pause  |  *now* for instant briefing",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ])

    return "\n".join(lines)
