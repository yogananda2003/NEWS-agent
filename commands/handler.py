import re
import threading


_HELP = (
    "Commands I understand:\n\n"
    "*now* - get briefing immediately\n"
    "*stop* - pause daily briefings\n"
    "*resume* - restart briefings\n"
    "*settings* - view your profile\n"
    "*more [#]* - full details on story #\n"
    "*restart* - redo setup"
)


def handle_command(user_id: str, user: dict, text: str, story_cache: dict) -> str:
    cmd = text.lower().strip()

    if cmd == "stop":
        return _stop(user_id)

    if cmd in ("resume", "start"):
        return _resume(user_id)

    if cmd == "now":
        return _now(user_id, user)

    if cmd == "settings":
        return _settings(user)

    if cmd.startswith("more"):
        return _more(user_id, text, story_cache)

    if cmd in ("restart", "reset"):
        return _restart(user_id)

    return _HELP


def _stop(user_id: str) -> str:
    from storage.db import upsert_user
    upsert_user(user_id, active=False)
    return "Briefings paused. Reply *resume* anytime to restart."


def _resume(user_id: str) -> str:
    from storage.db import upsert_user, get_user
    upsert_user(user_id, active=True)
    user = get_user(user_id)
    return f"Briefings resumed! Next one at {user.get('delivery_time', '07:00')}."


def _settings(user: dict) -> str:
    from onboarding.flow import domain_labels, tz_short
    labels = domain_labels(user.get("domains", []))
    status = "Active" if user.get("active") else "Paused"
    return (
        "*Your Briefing Profile*\n\n"
        f"Profession: {user.get('profession', 'Not set')}\n"
        f"Topics: {', '.join(labels) or 'None'}\n"
        f"Delivery: {user.get('delivery_time', '07:00')} {tz_short(user.get('timezone', 'UTC'))}\n"
        f"Status: {status}\n\n"
        "Reply *restart* to change your setup."
    )


def _more(user_id: str, text: str, story_cache: dict) -> str:
    match = re.search(r"\d+", text)
    if not match:
        return "Please specify a story number, e.g. *more 2*"

    n = int(match.group()) - 1
    stories = story_cache.get(user_id, [])

    if not stories:
        return "No recent briefing found. Reply *now* to get a fresh one."

    if n < 0 or n >= len(stories):
        return f"Story #{n+1} not found. Your last briefing had {len(stories)} stories."

    s = stories[n]
    parts = [f"*{s.get('headline', '')}*"]
    if s.get("source"):
        parts.append(f"_{s['source']}_")
    if s.get("summary"):
        parts.append(s["summary"])
    if s.get("why_it_matters"):
        parts.append(f"Why it matters: {s['why_it_matters']}")
    if s.get("url"):
        parts.append(f"Full article: {s['url']}")

    return "\n".join(parts)


def _now(user_id: str, user: dict) -> str:
    from briefing import run_briefing
    threading.Thread(target=run_briefing, args=(user,), daemon=True).start()
    return "Generating your briefing... hang on! Sending in a moment."


def _restart(user_id: str) -> str:
    from storage.db import upsert_user
    upsert_user(user_id, onboarding_step="START")
    from onboarding.flow import _WELCOME
    return _WELCOME
