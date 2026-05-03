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
│   Pulls from RSS feeds + NewsAPI + GNews API            │
│   Time window: last 24 hours only                       │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
           ▼                          ▼
    RSS Feed Parser            NewsAPI / GNews
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
│              CLAUDE — FILTER & RANK                     │
│   Removes: clickbait, sponsored, opinion, off-topic     │
│   Ranks: Breaking / Major / Moderate / Quick Hit        │
│   Selects top 8-12 stories for the briefing             │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             CLAUDE — SUMMARIZE & CONTEXTUALIZE          │
│   Writes 2-line summary per story                       │
│   Adds "Why it matters to you" based on user profile    │
│   Groups into sections: Top Stories + Quick Hits        │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              WHATSAPP DELIVERY ENGINE                   │
│   Formats message for WhatsApp (text + emoji sections)  │
│   Sends via WhatsApp Business API (Twilio / Meta)       │
│   Delivery confirmation + retry on failure              │
└─────────────────────────────────────────────────────────┘
```

---

## WhatsApp Message Format

```
━━━━━━━━━━━━━━━━━━━━━━━━
📰 YOUR AI BRIEFING
📅 Friday, May 2, 2026
⏱ 3 min read · 9 stories
━━━━━━━━━━━━━━━━━━━━━━━━

🔴 BREAKING
1. *OpenAI releases GPT-5 with 2M token context*
   Launched publicly today with multimodal reasoning and a 2M context window — largest ever in a commercial model.
   💼 For you: Direct competition to tools you use. Test it this week before clients ask you about it.
   🔗 Read more

━━━━━━━━━━━━━━━━━━━━━━

🟠 MAJOR
2. *Mistral raises $600M Series C at $6B valuation*
   French AI startup secures funding led by a16z. Plans to release open-weight frontier model by Q3.
   💼 For you: A stronger open-source competitor to GPT-4o — worth watching for cost-efficient deployments.
   🔗 Read more

3. *EU AI Act enforcement begins for high-risk systems*
   Regulators begin auditing AI products in healthcare, hiring, and credit scoring under the new EU AI Act.
   💼 For you: If you build or advise on AI products in Europe, compliance deadlines are now active.
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
• Anthropic raises Claude API rate limits for free tier
• GitHub Copilot adds voice coding in VS Code

━━━━━━━━━━━━━━━━━━━━━━
💬 Reply *more* for any story number
📌 Reply *stop* to pause briefings
⚙️ Reply *settings* to change domain/time
━━━━━━━━━━━━━━━━━━━━━━
```

---

## User Onboarding Flow (WhatsApp Conversation)

```
Agent:  Hi! I'm your personal news briefing agent.
        I'll send you a daily digest of everything 
        important in your professional domain.
        
        What is your profession?

User:   I'm a software engineer focused on AI

Agent:  Got it. Which topics should I cover?
        Reply with numbers (you can pick multiple):
        
        1. Artificial Intelligence & ML
        2. Developer Tools & Open Source  
        3. Cloud & Infrastructure
        4. Cybersecurity
        5. Startups & Funding
        6. Big Tech (Google, Meta, OpenAI, etc.)
        7. Programming Languages & Frameworks

User:   1, 2, 5, 6

Agent:  Perfect. What time should I send your briefing?
        (Reply in your local time, e.g. "7am" or "8:30am")

User:   7:30am

Agent:  Last question — your timezone?

User:   IST

Agent:  All set! Your first briefing arrives tomorrow 
        at 7:30 AM IST. 
        
        You can reply anytime:
        *more [number]* → deep dive on a story
        *stop*          → pause briefings
        *settings*      → update preferences
```

---

## Interactive Commands (Mid-Chat)

| User Reply | Agent Action |
|---|---|
| `more 3` | Fetches and sends full article summary for story #3 |
| `stop` | Pauses daily briefings (can resume anytime) |
| `resume` | Restarts daily briefings |
| `settings` | Shows current domain, time, timezone — allows editing |
| `weekly` | Sends a summary of the week's top stories |
| `now` | Triggers an on-demand briefing immediately |
| `add topic [topic]` | Adds a new topic to the user's profile |
| `remove topic [topic]` | Removes a topic from the user's profile |

---

## News Sources by Domain

### AI / Tech
- TechCrunch RSS
- The Verge RSS
- Wired RSS
- ArXiv (cs.AI, cs.LG, cs.CL — research papers)
- Hacker News Top Stories API
- VentureBeat AI RSS
- NewsAPI — query: `AI OR "machine learning" OR LLM`

### Finance
- Reuters Business RSS
- Bloomberg Technology RSS
- Financial Times RSS
- NewsAPI — query: `stocks OR "interest rates" OR earnings OR "M&A"`

### Healthcare
- STAT News RSS
- Fierce Healthcare RSS
- MedPage Today RSS
- NewsAPI — query: `FDA OR "clinical trial" OR "drug approval" OR pharma`

### Legal
- Law360 RSS
- Reuters Legal RSS
- Above the Law RSS
- NewsAPI — query: `legislation OR "supreme court" OR regulation OR compliance`

### Marketing
- Marketing Week RSS
- AdAge RSS
- Digiday RSS
- NewsAPI — query: `"digital marketing" OR advertising OR "brand strategy"`

### Real Estate
- HousingWire RSS
- CoStar News RSS
- Zillow Research Blog RSS
- NewsAPI — query: `"housing market" OR "mortgage rates" OR "real estate"`

---

## Data Models

### User Profile
```json
{
  "user_id": "whatsapp:+91XXXXXXXXXX",
  "name": "Yogananda",
  "profession": "AI Engineer",
  "domains": ["artificial-intelligence", "developer-tools", "startups", "big-tech"],
  "delivery_time": "07:30",
  "timezone": "Asia/Kolkata",
  "active": true,
  "created_at": "2026-05-02T00:00:00Z",
  "last_briefing_sent": "2026-05-02T07:30:00Z"
}
```

### Story Object
```json
{
  "story_id": "uuid",
  "headline": "OpenAI releases GPT-5",
  "source": "TechCrunch",
  "url": "https://...",
  "published_at": "2026-05-02T03:00:00Z",
  "raw_content": "...",
  "summary": "2-line Claude-generated summary",
  "why_it_matters": "Role-specific relevance line",
  "importance": "BREAKING | MAJOR | MODERATE | QUICK_HIT",
  "domains": ["artificial-intelligence", "big-tech"]
}
```

---

## Claude Prompts

### Filter & Rank Prompt
```
You are a professional news editor.

User profile:
- Profession: {profession}
- Domains: {domains}

Below are {n} raw news headlines from the last 24 hours.

Your tasks:
1. Remove any story that is: clickbait, sponsored content, opinion/editorial, 
   a duplicate, or irrelevant to the user's domains.
2. Rank remaining stories by importance:
   - BREAKING: Affects the user's work directly today
   - MAJOR: Industry-wide shift, widely discussed
   - MODERATE: Good to know, not urgent
   - QUICK_HIT: Minor update, one line only
3. Return top 8-12 stories maximum. No more.
4. Output as JSON array with fields: headline, url, source, importance, domain_tags

Headlines:
{headlines_json}
```

### Summarize & Contextualize Prompt
```
You are a professional briefing writer. Be concise, clear, and direct.

User profile:
- Profession: {profession}
- Domains: {domains}

For each story below, write:
1. summary: Exactly 2 sentences. What happened. Key facts only.
2. why_it_matters: 1 sentence. How this directly affects someone with this profession.

Do not use jargon. Do not be vague. Do not repeat the headline.
Write like you're texting a smart colleague.

Stories:
{filtered_stories_json}
```

---

## WhatsApp Delivery

### Option A — Twilio WhatsApp API (Recommended for Development)
- Easy setup with Twilio Sandbox
- Free for testing (up to 20 messages)
- Production: requires WhatsApp Business approval
- Cost: ~$0.005 per message

### Option B — Meta WhatsApp Business API (Production)
- Official Meta Cloud API
- Requires Facebook Business verification
- Free for first 1000 conversations/month
- Best for scaling to many users

### Message Constraints
- Max message length: 4096 characters
- Use `*bold*` for headlines
- Use `_italic_` for source names
- Keep Quick Hits section under 5 items to avoid truncation
- Split into 2 messages if total length exceeds 3500 characters

---

## API Keys Required

| Key | Service | Purpose | Free Tier |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic | AI filtering + summarization | $5 credit |
| `NEWSAPI_KEY` | newsapi.org | Fetch domain news | 100 req/day |
| `GNEWS_API_KEY` | gnews.io | Additional news source | 100 req/day |
| `TWILIO_ACCOUNT_SID` | Twilio | WhatsApp delivery | Sandbox free |
| `TWILIO_AUTH_TOKEN` | Twilio | WhatsApp delivery | Sandbox free |
| `TWILIO_WHATSAPP_FROM` | Twilio | Sender number | Sandbox free |

### Minimum to Launch
```
ANTHROPIC_API_KEY
NEWSAPI_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_WHATSAPP_FROM
```

---

## Environment Variables

```env
# AI
ANTHROPIC_API_KEY=sk-ant-...

# News Sources
NEWSAPI_KEY=...
GNEWS_API_KEY=...

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# App Config
DELIVERY_HOUR_DEFAULT=7
DELIVERY_MINUTE_DEFAULT=0
TIMEZONE_DEFAULT=UTC
MAX_STORIES=12
MAX_QUICK_HITS=5
```

---

## File Structure

```
news-briefing-agent/
├── main.py                  # Entry point, scheduler
├── spec.md                  # This document
├── .env                     # API keys (not committed)
├── requirements.txt
│
├── fetcher/
│   ├── rss_fetcher.py       # Pulls from RSS feeds
│   ├── newsapi_fetcher.py   # Pulls from NewsAPI
│   └── deduplicator.py      # Removes duplicate stories
│
├── processor/
│   ├── filter_agent.py      # Claude: filter + rank stories
│   └── summarizer.py        # Claude: summarize + contextualize
│
├── delivery/
│   ├── whatsapp.py          # Twilio WhatsApp sender
│   └── formatter.py         # Formats message for WhatsApp
│
├── onboarding/
│   └── flow.py              # User setup conversation flow
│
├── commands/
│   └── handler.py           # Handles: more, stop, settings, now, etc.
│
├── storage/
│   ├── users.json           # User profiles (use SQLite in production)
│   └── db.py                # Read/write user profiles
│
└── sources/
    └── domain_sources.json  # RSS feeds + NewsAPI queries per domain
```

---

## Scheduler Logic

```python
# Runs every minute, checks if any user is due for a briefing

for user in get_all_active_users():
    user_now = current_time_in_timezone(user.timezone)
    
    if user_now.hour == user.delivery_hour \
       and user_now.minute == user.delivery_minute \
       and not already_sent_today(user.user_id):
        
        trigger_briefing(user)
```

---

## Error Handling

| Scenario | Handling |
|---|---|
| NewsAPI rate limit hit | Fall back to RSS feeds only |
| Claude API timeout | Retry once, then send raw headlines |
| WhatsApp delivery failure | Retry after 5 minutes, max 3 attempts |
| No news found for domain | Send message: "Nothing major in your domain today" |
| User sends unknown command | Reply with command list |

---

## Phases

### Phase 1 — Core (Build First)
- [ ] NewsAPI + RSS fetcher
- [ ] Claude filter + summarize pipeline
- [ ] WhatsApp delivery via Twilio
- [ ] Hardcoded user profile (single user)
- [ ] Daily scheduler (cron job)

### Phase 2 — Multi-User + Onboarding
- [ ] WhatsApp onboarding conversation flow
- [ ] User profile storage (SQLite)
- [ ] Per-user domain + time + timezone settings
- [ ] Interactive commands (more, stop, settings)

### Phase 3 — Polish
- [ ] Weekly digest mode
- [ ] On-demand briefing (`now` command)
- [ ] Multiple domain support per user
- [ ] More news sources (GNews, Reddit, HackerNews)
- [ ] Fake/sponsored content detection

---

## Success Metrics

- User reads briefing within 1 hour of delivery
- Briefing takes under 3 minutes to read
- Zero important stories missed in the user's domain
- Zero irrelevant stories included
- Delivery success rate > 99%

---

## Constraints & Assumptions

- v1 supports WhatsApp delivery only
- News window is exactly 24 hours (not real-time)
- Users must have WhatsApp and opt in
- Twilio sandbox used for development; Meta Business API for production
- Claude claude-sonnet-4-6 used for all AI processing
- Storage is flat JSON in Phase 1, SQLite in Phase 2

---

*Spec version: 1.0 — Created May 2, 2026*
