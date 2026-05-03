# 📰 Professional News Briefing Agent

> An AI-powered WhatsApp agent that delivers a personalized, role-aware daily news briefing for professionals — in under 3 minutes.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![Grok](https://img.shields.io/badge/AI-Grok%20(xAI)-orange)](https://console.x.ai)
[![Twilio](https://img.shields.io/badge/WhatsApp-Twilio-red?logo=twilio)](https://twilio.com)
[![Render](https://img.shields.io/badge/Deployed-Render.com-purple)](https://render.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What It Does

Most professionals spend 1–2 hours every morning reading headlines across 10+ websites. This agent does it for you.

Every morning at your chosen time, it:
1. Fetches news from 30+ RSS feeds and NewsAPI across your domains
2. Removes duplicates, clickbait, and sponsored content
3. Uses **Grok AI** to rank stories by importance (BREAKING → MAJOR → MODERATE → QUICK HIT)
4. Writes 2-line summaries that explain **why each story matters to your specific profession**
5. Delivers everything to your **WhatsApp** — crisp, clean, 3 minutes to read

---

## Sample Briefing

```
━━━━━━━━━━━━━━━━━━━━━━━━
📰 YOUR DAILY BRIEFING
📅 Saturday, May 3, 2026
⏱ ~3 min read · 9 stories
━━━━━━━━━━━━━━━━━━━━━━━━

🔴 BREAKING
1. *OpenAI releases GPT-5 with 2M token context*
   TechCrunch
   Launched publicly today with multimodal reasoning — largest context window in any commercial model.
   💼 Direct competition to your current stack. Test it before your clients ask you about it.
   🔗 https://techcrunch.com/...

━━━━━━━━━━━━━━━━━━━━━━━━

🟠 MAJOR
2. *Mistral raises $600M Series C at $6B valuation*
   VentureBeat
   French AI startup secures funding led by a16z, plans open-weight frontier model by Q3.
   💼 Stronger open-source alternative for cost-efficient deployments — worth evaluating.
   🔗 https://venturebeat.com/...

━━━━━━━━━━━━━━━━━━━━━━━━

⚡ QUICK HITS
• Meta open-sources new vision-language model (VLM-2)
• Python 3.14 released with performance improvements
• GitHub Copilot adds voice coding in VS Code

━━━━━━━━━━━━━━━━━━━━━━━━
💬 Reply *more [#]* for full story
⚙️ Reply *stop* to pause | *now* for instant briefing
━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Supported Domains

| # | Domain | Example Sources |
|---|---|---|
| 1 | Artificial Intelligence & ML | TechCrunch AI, VentureBeat, The Verge |
| 2 | Developer Tools & Open Source | GitHub Blog, Stack Overflow Blog |
| 3 | Startups & Funding | TechCrunch, Crunchbase News |
| 4 | Big Tech | TechCrunch, NewsAPI |
| 5 | Finance & Markets | Reuters Business, NewsAPI |
| 6 | Healthcare & Pharma | STAT News, Fierce Healthcare |
| 7 | Legal & Compliance | Reuters Legal, NewsAPI |
| 8 | Marketing & Advertising | Marketing Week, AdAge |
| 9 | Real Estate | HousingWire, NewsAPI |
| 10 | Cybersecurity | The Hacker News, Krebs on Security |

---

## Architecture

```
User texts WhatsApp
        │
        ▼
┌───────────────────┐
│  Twilio Webhook   │  POST /webhook
│  (Render.com)     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐     New user?
│  Onboarding Flow  │──────────────► 4-step setup conversation
│  (State Machine)  │
└────────┬──────────┘
         │ Existing user
         ▼
┌───────────────────┐
│  Command Handler  │  stop / resume / now / more N / settings
└────────┬──────────┘
         │ "now" or scheduled
         ▼
┌───────────────────┐
│   News Fetcher    │  RSS + NewsAPI (30+ sources)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Deduplicator     │  Removes same story from multiple outlets
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Grok — Filter   │  Removes noise, ranks importance
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Grok — Summarize │  2-line summaries + "why it matters"
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ WhatsApp Delivery │  Via Twilio (auto-split at 1600 chars)
└───────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Brain | [Grok `grok-3`](https://console.x.ai) via OpenAI-compatible API |
| News Sources | RSS Feeds + [NewsAPI](https://newsapi.org) |
| WhatsApp | [Twilio WhatsApp Sandbox](https://twilio.com) |
| Web Server | Flask + Gunicorn |
| Storage | SQLite (multi-user profiles) |
| Deployment | [Render.com](https://render.com) (free tier) |
| Language | Python 3.10+ |

---

## Onboarding Flow

New users are set up through a 4-message WhatsApp conversation:

```
Bot → "What is your profession?"
You → "AI Engineer"

Bot → "Pick your topics (1-10)"
You → "1, 2, 4"

Bot → "What time? (e.g. 07:30)"
You → "07:30"

Bot → "Timezone?"
You → "1"  (IST)

Bot → "All set! First briefing arrives at 07:30 IST."
```

---

## Commands

Once onboarded, users can reply with:

| Command | Action |
|---|---|
| `now` | Get an instant briefing right now |
| `more 2` | Full details on story #2 from last briefing |
| `stop` | Pause daily briefings |
| `resume` | Restart daily briefings |
| `settings` | View your current profile |
| `restart` | Redo onboarding to change settings |

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Twilio account](https://twilio.com) (free sandbox)
- A [NewsAPI key](https://newsapi.org) (free tier)
- An [xAI API key](https://console.x.ai) (Grok, free tier)

### 1. Clone the repo

```bash
git clone https://github.com/yogananda2003/NEWS-agent.git
cd NEWS-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
XAI_API_KEY=xai-...
NEWSAPI_KEY=...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### 4. Configure your user profile (Phase 1 — single user)

Edit `storage/users.json`:

```json
{
  "user_id": "whatsapp:+91XXXXXXXXXX",
  "name": "Your Name",
  "profession": "AI Engineer",
  "domains": ["artificial-intelligence", "developer-tools", "big-tech"],
  "delivery_time": "07:30",
  "timezone": "Asia/Kolkata",
  "active": true
}
```

### 5. Run

```bash
# Test immediately
python main.py --now

# Run on schedule (delivers at your set time daily)
python main.py
```

---

## Deploying to Render.com (Phase 2 — Multi-User)

### 1. Push to GitHub

```bash
git remote add origin https://github.com/your-username/NEWS-agent.git
git push -u origin master
```

### 2. Deploy on Render

1. Sign up at [render.com](https://render.com)
2. New → Web Service → Connect your GitHub repo
3. Render auto-detects `render.yaml` (build + start commands pre-configured)
4. Add environment variables in the **Environment** tab:

| Key | Value |
|---|---|
| `XAI_API_KEY` | your xAI key |
| `NEWSAPI_KEY` | your NewsAPI key |
| `TWILIO_ACCOUNT_SID` | your Twilio SID |
| `TWILIO_AUTH_TOKEN` | your Twilio token |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+14155238886` |

5. Click **Deploy**

### 3. Connect Twilio

1. Go to `twilio.com/console` → Messaging → Try it out → Send a WhatsApp message
2. Set **"When a message comes in"** to:
   ```
   https://your-app.onrender.com/webhook
   ```
3. On your phone, send `join <sandbox-word>` to `+1 415 523 8886`
4. Text anything to your Twilio number — onboarding starts automatically

---

## Project Structure

```
NEWS-agent/
├── main.py                  # Phase 1: single-user scheduler + --now flag
├── server.py                # Phase 2: Flask webhook + background scheduler
├── briefing.py              # Shared: run_briefing() + story cache
├── render.yaml              # Render.com deployment config
├── requirements.txt
├── .env.example
│
├── fetcher/
│   ├── rss_fetcher.py       # Fetches from RSS feeds
│   ├── newsapi_fetcher.py   # Fetches from NewsAPI
│   └── deduplicator.py      # Removes duplicate stories (Jaccard similarity)
│
├── processor/
│   ├── filter_agent.py      # Grok: filter + rank by importance
│   └── summarizer.py        # Grok: 2-line summaries + "why it matters"
│
├── delivery/
│   ├── formatter.py         # Builds WhatsApp-formatted message
│   └── whatsapp.py          # Sends via Twilio (auto-splits long messages)
│
├── onboarding/
│   └── flow.py              # 4-step WhatsApp state machine
│
├── commands/
│   └── handler.py           # Routes: now, stop, resume, settings, more N
│
├── storage/
│   ├── db.py                # SQLite: multi-user CRUD
│   └── users.json           # Phase 1 single-user profile
│
├── sources/
│   └── domain_sources.json  # RSS feeds + NewsAPI queries per domain
│
└── utils/
    └── ssl_helper.py        # Corporate proxy CA bundle fallback
```

---

## Roadmap

- [x] Phase 1 — Single user, RSS + NewsAPI, Grok AI, WhatsApp delivery
- [x] Phase 2 — Multi-user, onboarding flow, SQLite, commands, Render deployment
- [ ] Phase 3 — Weekly digest, Reddit/HackerNews sources, PostgreSQL, Meta Business API

---

## Contributing

Pull requests are welcome. For major changes, open an issue first.

1. Fork the repo
2. Create a branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push and open a PR

---

## License

MIT — free to use, modify, and distribute.

---

## Author

Built by [Yogananda](https://github.com/yogananda2003) using Claude Code + Python.

> *"One agent. Every profession."*
