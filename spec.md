# Professional News Briefing Agent — Specification

## Overview

A personalized AI-powered news briefing agent that monitors the internet for professional domain-specific news every 24 hours and delivers a short, crisp, complete summary directly to the user via WhatsApp. The agent learns the user's profession and domain, filters noise, ranks importance, and writes summaries that explain not just what happened — but why it matters to that specific professional.

---

## Problem Statement

Professionals across every domain (tech, healthcare, finance, law, marketing, etc.) need to stay updated with their industry. But:

- News is scattered across dozens of sources
- Most headlines are clickbait or duplicate
- Reading everything takes 1-2 hours per day
- Generic news apps don't explain domain relevance
- Busy professionals miss critical updates

This agent solves all of that in a 3-minute daily WhatsApp message.

---

## Goals

- Deliver domain-specific news every 24 hours via WhatsApp
- Cover all major stories — nothing important missed
- Keep each story to 2-3 lines maximum
- Rank stories by importance (Breaking → Major → Moderate → Quick Hit)
- Explain why each story matters to the specific professional
- Remove duplicates, clickbait, sponsored content, and irrelevant noise
- Support any professional domain, not just tech

---

## Non-Goals

- Not a real-time breaking news alert system
- Not a full article reader
- Not a social media aggregator (no likes, comments, shares)
- Not a paid news subscription replacement
- Does not store or archive news history (v1)

---

## Target Users

| Professional | Domain |
|---|---|
| Software Engineer / AI Engineer | AI, ML, Dev tools, open source |
| Doctor / Healthcare Worker | Clinical research, FDA approvals, pharma |
| Lawyer / Legal Professional | Case rulings, legislation, compliance |
| Finance / Trader / Analyst | Markets, earnings, M&A, economic indicators |
| Marketing Professional | Brand news, ad platforms, consumer trends |
| Real Estate Agent | Property prices, mortgage rates, housing policy |
| HR Professional | Labor law, hiring trends, workplace culture |
| Startup Founder / Investor | VC funding, competitor news, market shifts |
| Teacher / Academic | Education policy, edtech, research |
| Journalist | Any beat they cover |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     SCHEDULER                           │
│              Runs daily at user-chosen time             │
│                   (default: 7:00 AM)                    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   NEWS FETCHER                          │
│   Pulls from RSS feeds + NewsAPI                        │
│   Time window: last 24 hours only                       │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
           ▼                          ▼
    RSS Feed Parser              NewsAPI
    (domain-specific           (keyword + category
     curated feeds)             based queries)
           │                          │
           └──────────┬───────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  DEDUPLICATOR                           │
│   Removes duplicate stories from multiple sources       │
│   Groups same event covered by different outlets        │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              GROK (xAI) — FILTER & RANK                 │
│   Removes: clickbait, sponsored, opinion, off-topic     │
│   Ranks: Breaking / Major / Moderate / Quick Hit        │
│   Selects top 8-12 stories for the briefing             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          GROK (xAI) — SUMMARIZE & CONTEXTUALIZE         │
│   Writes 2-line summary per story                       │
│   Adds "Why it matters to you" based on user profile    │
│   Groups into sections: Top Stories + Quick Hits        │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              WHATSAPP DELIVERY ENGINE                   │
│   Formats message for WhatsApp (text + emoji sections)  │
│   Sends via Twilio WhatsApp Sandbox API                 │
│   Delivery confirmation + retry on failure              │
└─────────────────────────────────────────────────────────┘
```

---

## AI Model Decision

> **Originally planned:** Anthropic Claude API (`claude-sonnet-4-6`)
>
> **Switched to:** xAI Grok API (`grok-3`)
>
> **Reason:** Grok offers a free tier with no upfront billing required, making it easier to get started without adding a credit card or purchasing credits. The Grok API is fully OpenAI-compatible, so the switch required minimal code changes — just swapping the client and model name. Performance for filtering and summarization tasks is comparable.

The Grok API is accessed via the OpenAI Python SDK with a custom `base_url`:

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)
```

---

## WhatsApp Message Format

```
━━━━━━━━━━━━━━━━━━━━━━━━
📰 YOUR DAILY BRIEFING
📅 Saturday, May 3, 2026
⏱ ~3 min read · 9 stories
━━━━━━━━━━━━━━━━━━━━━━━━

🔴 BREAKING
1. *OpenAI releases GPT-5 with 2M token context*
   Launched publicly today with multimodal reasoning and a 2M context window.
   💼 Direct competition to tools you use. Test it before clients ask.
   🔗 Read more

━━━━━━━━━━━━━━━━━━━━━━

🟠 MAJOR
2. *Mistral raises $600M Series C at $6B valuation*
   French AI startup secures funding led by a16z. Plans open-weight frontier model by Q3.
   💼 Stronger open-source alternative for cost-efficient deployments.
   🔗 Read more

3. *EU AI Act enforcement begins for high-risk systems*
   Regulators begin auditing AI products in healthcare, hiring, and credit scoring.
   💼 If you build AI products for Europe, compliance deadlines are now active.
   🔗 Read more

━━━━━━━━━━━━━━━━━━━━━━

🟡 MODERATE
4. *Google DeepMind paper beats o3 on math benchmarks*
   ...

5. *Hugging Face launches fine-tuning platform for SMBs*
   ...

━━━━━━━━━━━━━━━━━━━━━━

⚡ QUICK HITS
• Meta open-sources new vision-language model (VLM-2)
• Python 3.14 released with performance improvements
• GitHub Copilot adds voice coding in VS Code

━━━━━━━━━━━━━━━━━━━━━━
💬 Reply *more [#]* for full story
⚙️ Reply *stop* to pause | *now* for instant briefing
━━━━━━━━━━━━━━━━━━━━━━
```

---

## User Onboarding Flow (WhatsApp Conversation)

```
Agent:  Welcome! I'm your personal news briefing agent.
        Every morning I'll send you a short, crisp summary
        of everything important in your domain — right here
        on WhatsApp. Let's set you up in 4 quick steps.

        What is your profession?

User:   AI Engineer

Agent:  Which topics should I cover?
        Reply with numbers separated by commas:

        1. Artificial Intelligence & ML
        2. Developer Tools & Open Source
        3. Startups & Funding
        4. Big Tech (Google, Meta, Apple, etc.)
        5. Finance & Markets
        6. Healthcare & Pharma
        7. Legal & Compliance
        8. Marketing & Advertising
        9. Real Estate
        10. Cybersecurity

        Example: 1,2,5

User:   1, 2, 4

Agent:  Got it! Covering: AI & ML, Developer Tools, Big Tech.
        What time should I send your daily briefing?
        Reply in 24hr format (e.g. 07:30 or 08:00)

User:   07:30

Agent:  Briefing set for 07:30.
        What is your timezone?

        1. India (IST, UTC+5:30)
        2. US East (EST, UTC-5)
        ... (8 options)

User:   1

Agent:  All set! Here's your profile:
        Profession: AI Engineer
        Topics: AI & ML, Developer Tools, Big Tech
        Delivery: 07:30 IST

        Anytime you can reply:
        *now* - get briefing immediately
        *stop* - pause briefings
        *settings* - view your profile
```

---

## Interactive Commands (Mid-Chat)

| User Reply | Agent Action |
|---|---|
| `more 3` | Sends full details for story #3 from last briefing |
| `stop` | Pauses daily briefings |
| `resume` | Restarts daily briefings |
| `settings` | Shows current profile (profession, domains, time, timezone) |
| `now` | Triggers an on-demand briefing immediately |
| `restart` | Restarts onboarding to change all settings |

---

## News Sources by Domain

### AI / Tech
- TechCrunch RSS
- VentureBeat AI RSS
- The Verge RSS
- NewsAPI — query: `artificial intelligence OR machine learning OR LLM OR ChatGPT OR OpenAI OR Anthropic`

### Developer Tools
- GitHub Blog RSS
- Stack Overflow Blog RSS
- NewsAPI — query: `developer tools OR open source OR GitHub OR programming language OR framework`

### Startups & Funding
- TechCrunch Startups RSS
- Crunchbase News RSS
- NewsAPI — query: `startup funding OR venture capital OR series A OR series B OR IPO`

### Big Tech
- TechCrunch RSS
- NewsAPI — query: `Google OR Meta OR Apple OR Microsoft OR Amazon AWS announcement`

### Finance
- Reuters Business RSS
- NewsAPI — query: `stock market OR earnings OR interest rates OR inflation OR Federal Reserve`

### Healthcare
- STAT News RSS
- Fierce Healthcare RSS
- NewsAPI — query: `FDA OR "clinical trial" OR "drug approval" OR pharma`

### Legal
- Reuters Legal RSS
- NewsAPI — query: `legislation OR "supreme court" OR regulation OR compliance`

### Marketing
- Marketing Week RSS
- AdAge RSS
- NewsAPI — query: `"digital marketing" OR advertising OR "brand strategy"`

### Real Estate
- HousingWire RSS
- NewsAPI — query: `"housing market" OR "mortgage rates" OR "real estate"`

### Cybersecurity
- The Hacker News RSS
- Krebs on Security RSS
- NewsAPI — query: `cybersecurity OR data breach OR ransomware OR vulnerability`

---

## Data Models

### User Profile (SQLite)
```json
{
  "user_id": "whatsapp:+91XXXXXXXXXX",
  "name": "Yogananda",
  "profession": "AI Engineer",
  "domains": ["artificial-intelligence", "developer-tools", "big-tech"],
  "delivery_time": "07:30",
  "timezone": "Asia/Kolkata",
  "active": true,
  "onboarding_step": "COMPLETE",
  "last_briefed_date": "2026-05-03",
  "created_at": "2026-05-03T00:00:00Z"
}
```

### Story Object (in-memory)
```json
{
  "headline": "OpenAI releases GPT-5",
  "source": "TechCrunch",
  "url": "https://...",
  "published_at": "2026-05-03T03:00:00Z",
  "summary": "2-line Grok-generated summary",
  "why_it_matters": "Role-specific relevance line",
  "importance": "BREAKING | MAJOR | MODERATE | QUICK_HIT"
}
```

---

## Grok Prompts

### Filter & Rank Prompt
```
You are a professional news editor with deep expertise across all industries.
Your job is to filter and rank news stories for a specific professional.
You always return valid JSON and nothing else.

User profile:
- Profession: {profession}
- Domains: {domains}

1. Remove stories that are: clickbait, sponsored/PR, pure opinion, duplicates,
   or unrelated to the user's domains.
2. Rank each kept story by importance:
   - BREAKING  → directly affects the user's work today
   - MAJOR     → industry-wide shift, widely discussed
   - MODERATE  → good to know, not urgent
   - QUICK_HIT → minor update, one line is enough
3. Keep at most 12 stories.

Return ONLY a valid JSON array:
[{"id": <original_id>, "importance": "BREAKING|MAJOR|MODERATE|QUICK_HIT"}]
```

### Summarize & Contextualize Prompt
```
You are a professional news briefing writer.
Be concise, factual, and direct. Write like you're texting a smart colleague.
You always return valid JSON and nothing else.

User profile:
- Profession: {profession}
- Domains: {domains}

For each story write:
1. "summary": Exactly 2 sentences. What happened. Key facts only. No jargon.
2. "why_it_matters": 1 sentence. How this directly affects someone in this profession.

Return ONLY a valid JSON array:
[{"id": <id>, "summary": "...", "why_it_matters": "..."}]
```

---

## WhatsApp Delivery

### Twilio WhatsApp Sandbox (Development / Current)
- Easy setup, free for testing
- Requires users to join the sandbox once
- Max message length: 1600 characters per message
- Long briefings are split into multiple messages automatically
- Cost: ~$0.005 per message in production

### Meta WhatsApp Business API (Production — Future)
- Official Meta Cloud API
- Requires Facebook Business verification
- Free for first 1000 conversations/month
- Best for scaling to many users

---

## API Keys Required

| Key | Service | Purpose | Free Tier |
|---|---|---|---|
| `XAI_API_KEY` | xAI (Grok) | AI filtering + summarization | Free tier available |
| `NEWSAPI_KEY` | newsapi.org | Fetch domain news | 100 req/day |
| `TWILIO_ACCOUNT_SID` | Twilio | WhatsApp delivery | Sandbox free |
| `TWILIO_AUTH_TOKEN` | Twilio | WhatsApp delivery | Sandbox free |
| `TWILIO_WHATSAPP_FROM` | Twilio | Sender number | Sandbox free |

### Minimum to Launch
```
XAI_API_KEY
NEWSAPI_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_WHATSAPP_FROM
```

---

## Environment Variables

```env
# xAI (Grok) — get from console.x.ai
XAI_API_KEY=xai-...

# News Sources
NEWSAPI_KEY=...

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

---

## File Structure

```
agent-2/
├── main.py                  # Phase 1 entry point (single user, --now flag)
├── server.py                # Phase 2 entry point (Flask webhook + scheduler)
├── briefing.py              # Shared run_briefing() logic + story cache
├── spec.md                  # This document
├── render.yaml              # Render.com deployment config
├── requirements.txt
├── .env                     # API keys (not committed)
├── .gitignore
│
├── fetcher/
│   ├── rss_fetcher.py       # Pulls from RSS feeds
│   ├── newsapi_fetcher.py   # Pulls from NewsAPI
│   └── deduplicator.py      # Removes duplicate stories
│
├── processor/
│   ├── filter_agent.py      # Grok: filter + rank stories
│   └── summarizer.py        # Grok: summarize + contextualize
│
├── delivery/
│   ├── whatsapp.py          # Twilio WhatsApp sender
│   └── formatter.py         # Formats message for WhatsApp
│
├── onboarding/
│   └── flow.py              # 5-step WhatsApp conversation state machine
│
├── commands/
│   └── handler.py           # Handles: more N, stop, resume, settings, now, restart
│
├── storage/
│   ├── db.py                # SQLite operations (multi-user)
│   └── users.json           # Phase 1 single-user profile
│
├── sources/
│   └── domain_sources.json  # RSS feeds + NewsAPI queries per domain
│
└── utils/
    └── ssl_helper.py        # Corporate proxy CA bundle fallback
```

---

## Deployment

### Local (Phase 1 — Single User)
```bash
python main.py --now        # run immediately
python main.py              # run on schedule (reads delivery_time from users.json)
```

### Cloud (Phase 2 — Multi-User)
Deployed on **Render.com** free tier.

```
URL: https://news-agent-g8ws.onrender.com
Webhook: https://news-agent-g8ws.onrender.com/webhook
Start command: gunicorn server:app --workers 2 --timeout 120
```

Render auto-deploys on every push to the `master` branch of:
`https://github.com/yogananda2003/NEWS-agent`

---

## Scheduler Logic

```python
# Runs every minute inside a background thread
# Checks if any active user's delivery time matches current time

for user in get_all_active_users():
    if already_briefed_today(user):
        continue
    tz = pytz.timezone(user["timezone"])
    now = datetime.now(tz)
    h, m = map(int, user["delivery_time"].split(":"))
    if now.hour == h and now.minute == m:
        threading.Thread(target=run_briefing, args=(user,)).start()
```

---

## Error Handling

| Scenario | Handling |
|---|---|
| NewsAPI rate limit hit | Falls back to RSS feeds only |
| Grok API error | Falls back to returning raw headlines without summaries |
| WhatsApp delivery failure (1600 char limit) | Automatically splits into multiple messages |
| No news found for domain | Sends "Nothing major today" message |
| User sends unknown command | Replies with full command list |
| New user messages bot | Starts onboarding flow automatically |

---

## Phases

### Phase 1 — Core ✅ COMPLETE
- [x] RSS + NewsAPI fetcher
- [x] Grok filter + summarize pipeline
- [x] WhatsApp delivery via Twilio
- [x] Single user hardcoded profile
- [x] Daily scheduler

### Phase 2 — Multi-User + Onboarding ✅ COMPLETE
- [x] WhatsApp onboarding conversation flow (4-step)
- [x] SQLite multi-user storage
- [x] Per-user domain + time + timezone settings
- [x] Interactive commands (more N, stop, resume, settings, now, restart)
- [x] Flask webhook server deployed on Render.com
- [x] Auto-deploy via GitHub

### Phase 3 — Polish (Upcoming)
- [ ] Weekly digest mode (`weekly` command)
- [ ] More news sources (Reddit, HackerNews, GNews)
- [ ] Fake/sponsored content detection
- [ ] Swap SQLite for PostgreSQL (persistent across deploys)
- [ ] Meta WhatsApp Business API (for production scale)

---

## Success Metrics

- User reads briefing within 1 hour of delivery
- Briefing takes under 3 minutes to read
- Zero important stories missed in the user's domain
- Zero irrelevant stories included
- Delivery success rate > 99%

---

## Constraints & Assumptions

- WhatsApp delivery only (v1 + v2)
- News window is exactly last 24 hours
- Users must have WhatsApp and join the Twilio sandbox once
- Free tier on Render may have ~50s cold start after inactivity
- SQLite resets on Render redeploy — upgrade to PostgreSQL for persistence
- Grok `grok-3` model used for all AI processing

---

*Spec version: 2.0 — Updated May 3, 2026*
*AI model changed from Anthropic Claude to xAI Grok (free tier)*
