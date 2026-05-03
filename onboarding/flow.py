import re
from typing import Optional

import pytz

COMPLETE = "COMPLETE"

DOMAIN_OPTIONS = {
    "1":  ("artificial-intelligence", "Artificial Intelligence & ML"),
    "2":  ("developer-tools",         "Developer Tools & Open Source"),
    "3":  ("startups-funding",        "Startups & Funding"),
    "4":  ("big-tech",                "Big Tech (Google, Meta, Apple, etc.)"),
    "5":  ("finance",                 "Finance & Markets"),
    "6":  ("healthcare",              "Healthcare & Pharma"),
    "7":  ("legal",                   "Legal & Compliance"),
    "8":  ("marketing",               "Marketing & Advertising"),
    "9":  ("real-estate",             "Real Estate"),
    "10": ("cybersecurity",           "Cybersecurity"),
}

TIMEZONE_OPTIONS = {
    "1": ("Asia/Kolkata",        "IST (UTC+5:30)"),
    "2": ("America/New_York",    "EST (UTC-5)"),
    "3": ("America/Los_Angeles", "PST (UTC-8)"),
    "4": ("Europe/London",       "GMT (UTC+0)"),
    "5": ("Europe/Paris",        "CET (UTC+1)"),
    "6": ("Asia/Singapore",      "SGT (UTC+8)"),
    "7": ("Asia/Tokyo",          "JST (UTC+9)"),
    "8": ("Australia/Sydney",    "AEST (UTC+10)"),
}

_DOMAIN_LIST = (
    "Which topics should I cover?\n"
    "Reply with numbers separated by commas:\n\n"
    "1. Artificial Intelligence & ML\n"
    "2. Developer Tools & Open Source\n"
    "3. Startups & Funding\n"
    "4. Big Tech (Google, Meta, Apple, etc.)\n"
    "5. Finance & Markets\n"
    "6. Healthcare & Pharma\n"
    "7. Legal & Compliance\n"
    "8. Marketing & Advertising\n"
    "9. Real Estate\n"
    "10. Cybersecurity\n\n"
    "Example: 1,2,5"
)

_TZ_LIST = (
    "What is your timezone?\n\n"
    "1. India (IST, UTC+5:30)\n"
    "2. US East (EST, UTC-5)\n"
    "3. US West (PST, UTC-8)\n"
    "4. UK (GMT, UTC+0)\n"
    "5. Europe (CET, UTC+1)\n"
    "6. Singapore (SGT, UTC+8)\n"
    "7. Japan (JST, UTC+9)\n"
    "8. Australia East (AEST, UTC+10)\n\n"
    "Or type your city (e.g. Mumbai, London)"
)

_WELCOME = (
    "Welcome! I'm your personal news briefing agent.\n\n"
    "Every morning I'll send you a short, crisp summary of everything important in your domain — right here on WhatsApp.\n\n"
    "Let's set you up in 4 quick steps.\n\n"
    "What is your profession?\n"
    "(e.g. AI Engineer, Doctor, Lawyer, Marketing Manager)"
)


def handle_onboarding(user_id: str, user: Optional[dict], text: str) -> str:
    from storage.db import upsert_user, get_user

    step = user.get("onboarding_step", "START") if user else "START"

    if step == "START" or not user:
        upsert_user(user_id, onboarding_step="AWAITING_PROFESSION")
        return _WELCOME

    if step == "AWAITING_PROFESSION":
        if len(text.strip()) < 2:
            return "Please enter your profession (e.g. AI Engineer, Doctor, Lawyer)"
        upsert_user(user_id, profession=text.strip(), onboarding_step="AWAITING_DOMAINS")
        return _DOMAIN_LIST

    if step == "AWAITING_DOMAINS":
        selected = _parse_domains(text)
        if not selected:
            return f"Please enter valid numbers (1-10), e.g: 1,2,5\n\n{_DOMAIN_LIST}"
        domain_keys = [DOMAIN_OPTIONS[n][0] for n in selected]
        domain_names = [DOMAIN_OPTIONS[n][1] for n in selected]
        upsert_user(user_id, domains=domain_keys, onboarding_step="AWAITING_TIME")
        return (
            f"Got it! Covering: {', '.join(domain_names)}\n\n"
            "What time should I send your daily briefing?\n"
            "Reply in 24hr format (e.g. 07:30 or 08:00)"
        )

    if step == "AWAITING_TIME":
        t = _parse_time(text)
        if not t:
            return "Please enter a valid time, e.g. 07:30 or 08:00"
        upsert_user(user_id, delivery_time=t, onboarding_step="AWAITING_TIMEZONE")
        return f"Briefing set for {t}.\n\n{_TZ_LIST}"

    if step == "AWAITING_TIMEZONE":
        tz = _parse_timezone(text)
        if not tz:
            return f"Please enter a number 1-8 or a timezone name.\n\n{_TZ_LIST}"
        upsert_user(user_id, timezone=tz, onboarding_step=COMPLETE, active=True)
        user = get_user(user_id)
        labels = domain_labels(user.get("domains", []))
        return (
            "All set! Here's your profile:\n\n"
            f"Profession: {user.get('profession', '')}\n"
            f"Topics: {', '.join(labels)}\n"
            f"Delivery: {user.get('delivery_time')} {tz_short(tz)}\n\n"
            "Your first briefing arrives at your chosen time.\n\n"
            "Anytime you can reply:\n"
            "*now* - get briefing immediately\n"
            "*stop* - pause briefings\n"
            "*settings* - view your profile"
        )

    return "Something went wrong. Reply *restart* to set up again."


def domain_labels(keys: list) -> list:
    lookup = {v[0]: v[1] for v in DOMAIN_OPTIONS.values()}
    return [lookup.get(k, k) for k in keys]


def tz_short(tz: str) -> str:
    lookup = {v[0]: v[1] for v in TIMEZONE_OPTIONS.values()}
    return lookup.get(tz, tz)


def _parse_domains(text: str) -> list:
    nums = [n.strip() for n in re.split(r"[,\s]+", text) if n.strip()]
    return [n for n in nums if n in DOMAIN_OPTIONS]


def _parse_time(text: str) -> Optional[str]:
    m = re.match(r"^(\d{1,2}):(\d{2})\s*(am|pm)?$", text.strip(), re.IGNORECASE)
    if not m:
        return None
    h, mn, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
    if ampm:
        if ampm.lower() == "pm" and h != 12:
            h += 12
        elif ampm.lower() == "am" and h == 12:
            h = 0
    if 0 <= h <= 23 and 0 <= mn <= 59:
        return f"{h:02d}:{mn:02d}"
    return None


def _parse_timezone(text: str) -> Optional[str]:
    text = text.strip()
    if text in TIMEZONE_OPTIONS:
        return TIMEZONE_OPTIONS[text][0]
    try:
        pytz.timezone(text)
        return text
    except Exception:
        return None
