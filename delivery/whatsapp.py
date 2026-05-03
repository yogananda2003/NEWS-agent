import os
from typing import List
from twilio.rest import Client

from utils.ssl_helper import get_ca_bundle


def send_whatsapp(to: str, message: str) -> bool:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

    if not account_sid or not auth_token:
        print("  Twilio credentials missing — printing message to console instead:\n")
        print(message)
        return False

    # Twilio uses requests internally — point it to the correct CA bundle
    os.environ["REQUESTS_CA_BUNDLE"] = get_ca_bundle()

    to_number = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
    client = Client(account_sid, auth_token)

    try:
        for chunk in _split(message, max_len=1550):
            client.messages.create(from_=from_number, to=to_number, body=chunk)
        return True
    except Exception as e:
        print(f"  WhatsApp delivery error: {e}")
        return False


def _split(message: str, max_len: int) -> List[str]:
    if len(message) <= max_len:
        return [message]

    parts = []
    while message:
        if len(message) <= max_len:
            parts.append(message)
            break
        split_at = message.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        parts.append(message[:split_at])
        message = message[split_at:].lstrip("\n")
    return parts
