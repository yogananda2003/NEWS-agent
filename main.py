import io
import json
import sys
import time
from datetime import datetime

import pytz
import schedule
from dotenv import load_dotenv

load_dotenv()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from briefing import run_briefing


def _load_user() -> dict:
    with open("storage/users.json") as f:
        return json.load(f)


def _check_schedule():
    user = _load_user()
    if not user.get("active"):
        return
    tz = pytz.timezone(user.get("timezone", "UTC"))
    now = datetime.now(tz)
    h, m = map(int, user.get("delivery_time", "07:00").split(":"))
    if now.hour == h and now.minute == m:
        run_briefing(user)


def main():
    if "--now" in sys.argv:
        run_briefing(_load_user())
        return

    user = _load_user()
    print("News Briefing Agent — Phase 1 (Single User)")
    print(f"Scheduled at {user.get('delivery_time')} {user.get('timezone')}")
    print("Press Ctrl+C to stop.\n")

    schedule.every(1).minutes.do(_check_schedule)
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
