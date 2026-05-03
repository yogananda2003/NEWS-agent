import io
import sys
import threading
import time
from datetime import datetime

import pytz
import schedule
from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from storage.db import init_db, get_user, get_all_active_users, already_briefed_today, upsert_user
from onboarding.flow import handle_onboarding, COMPLETE
from commands.handler import handle_command
from briefing import run_briefing, story_cache

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    from_number = request.form.get("From", "").strip()
    body = request.form.get("Body", "").strip()
    profile_name = request.form.get("ProfileName", "").strip()

    resp = MessagingResponse()
    if not from_number:
        return str(resp)

    user = get_user(from_number)

    if profile_name and (not user or not user.get("name")):
        upsert_user(from_number, name=profile_name)
        user = get_user(from_number)

    step = user.get("onboarding_step", "START") if user else "START"

    if step != COMPLETE:
        reply = handle_onboarding(from_number, user, body)
    else:
        reply = handle_command(from_number, user, body, story_cache)

    if reply:
        resp.message(reply)

    return str(resp)


@app.route("/", methods=["GET"])
def health():
    return "News Briefing Agent is running.", 200


def _scheduler_loop():
    def check():
        for user in get_all_active_users():
            if already_briefed_today(user):
                continue
            tz = pytz.timezone(user.get("timezone", "UTC"))
            now = datetime.now(tz)
            h, m = map(int, user.get("delivery_time", "07:00").split(":"))
            if now.hour == h and now.minute == m:
                threading.Thread(target=run_briefing, args=(user,), daemon=True).start()

    schedule.every(1).minutes.do(check)
    while True:
        schedule.run_pending()
        time.sleep(30)


# Called at import time so gunicorn (which skips __main__) still initializes everything
init_db()
threading.Thread(target=_scheduler_loop, daemon=True).start()
print("DB initialized. Scheduler started.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
