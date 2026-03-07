# GeoPulse 🌍

### Geopolitical Market Intelligence — powered by GDELT, yfinance & Llama 3

> *How does geopolitics move the markets?*

GeoPulse is a full-stack intelligence tool that takes any geopolitical event — war, sanctions, election, trade deal — and instantly maps it to sector-level market impact with an AI-generated consulting brief.

**[Live Demo →](https://ambitchious.github.io/geopulse)**

---

## What it does

Type any geopolitical event and GeoPulse returns:

- **Event classification** — war, sanctions, election, trade, or diplomacy
- **Affected sectors** — which ETFs are bullish/bearish and why
- **90-day price chart** — real sector performance correlated to the event
- **AI Impact Brief** — consulting-style analysis with winners, losers, historical parallels, and key risk triggers

---

## Example queries

| Query | Event Type | Key Insight |
|-------|-----------|-------------|
| Russia Ukraine war energy | War | XLE +18%, EWG -12% |
| US China semiconductor sanctions | Trade | QQQ bearish, GLD bullish |
| Iran Israel conflict oil | War | XLE spike, EEM selloff |
| OPEC oil production cuts | Diplomacy | Energy sector repricing |
| India Pakistan border tensions | War | EEM volatility, GLD safe haven |

---

## Architecture

```
User Query
    ↓
Flask REST API (backend/)
    ├── GDELT Project     → real-time geopolitical event database
    ├── yfinance          → sector ETF price history (90 days)
    └── Groq + Llama 3   → consulting-style AI impact brief
    ↓
React-style Dashboard (frontend/)
    ├── Event classification banner
    ├── Sentiment stats (tone, trend, signal)
    ├── Bullish / Bearish sector cards
    ├── 90-day price performance chart
    ├── AI Impact Brief
    └── GDELT news feed with tone scores
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask, Flask-CORS |
| AI Analysis | Groq API, Llama 3.3 70B |
| Geopolitical Data | GDELT Project (1979–present) |
| Market Data | yfinance (Yahoo Finance) |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Deployment | Render (backend), GitHub Pages (frontend) |

---

## Project Structure

```
geopulse/
├── backend/
│   ├── app.py          ← Flask REST API
│   ├── gdelt.py        ← GDELT event fetcher + classifier
│   ├── market.py       ← yfinance price data
│   ├── analyzer.py     ← Groq AI analysis engine
│   └── .env            ← (local only, never committed)
├── frontend/
│   └── index.html      ← full dashboard UI
├── requirements.txt
└── README.md
```

---

## Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/Ambitchious/geopulse.git
cd geopulse
```

**2. Set up virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create `backend/.env`:
```
GROQ_API_KEY=your_groq_key_here
```
Get a free key at [console.groq.com](https://console.groq.com) — no credit card needed.

**5. Run the backend**
```bash
python backend/app.py
```

**6. Run the frontend**
```bash
cd frontend
python -m http.server 3000
```

Open `http://localhost:3000` in your browser.

---

## Deploy on Render

1. Go to [render.com](https://render.com) → New → Web Service
2. Connect this GitHub repo
3. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r ../requirements.txt`
   - Start Command: `gunicorn app:app`
4. Environment Variables → add `GROQ_API_KEY`
5. Deploy → copy your URL → update `API_BASE` in `frontend/index.html`

---

## API Reference

### `POST /api/analyze`
```json
// Request
{ "query": "US China semiconductor sanctions" }

// Response
{
  "query": "US China semiconductor sanctions",
  "event_type": "trade",
  "context": "One-line geopolitical summary",
  "tone": { "avg_tone": -2.4, "sentiment": "negative", "trend": "escalating", "n_events": 12 },
  "sectors": {
    "bullish": [{ "ticker": "GLD", "name": "Gold ETF" }],
    "bearish": [{ "ticker": "QQQ", "name": "Nasdaq-100 ETF" }]
  },
  "prices": { "GLD": [{ "date": "2024-01-01", "close": 185.2, "pct_change": 0.0 }] },
  "events": [{ "date": "20241201", "title": "...", "tone": -3.1, "source": "reuters.com" }],
  "analysis": { "brief": "## SITUATION SUMMARY\n..." }
}
```

### `GET /api/health`
```json
{ "status": "ok", "service": "GeoPulse API" }
```

---

## Design Decisions

**Why GDELT?** Most market tools use financial data only. GDELT tracks every geopolitical event on earth since 1979, updated every 15 minutes — the same database used by the UN and World Bank. Using it as a signal source is genuinely novel.

**Why Llama 3 via Groq?** Groq's inference hardware runs Llama 3 70B at ~500 tokens/second — fast enough for real-time analysis. The model produces structured consulting-style briefs that are specific and actionable, not generic summaries.

**Why ETF proxies instead of individual stocks?** Sector ETFs (SPY, XLE, GLD, EEM) are more stable signals for geopolitical impact than individual stocks, which have company-specific noise. They also make the analysis more generalizable.

**Graceful degradation** — if GDELT or yfinance is unavailable, the AI brief still generates. The app never crashes on external API failures.

---

## What I learned

- GDELT's tone scoring uses a comma-separated format — the overall tone is just the first value
- yfinance's `.history()` method is more reliable than `.download()` for single tickers
- Geopolitical classification via keyword matching works surprisingly well for the 5 major event types
- Consulting-style prompting (specific sections, word limits, historical parallels) produces dramatically better AI output than open-ended prompts

---

*Built as Project 3 of 6 in a portfolio targeting consulting and SWE internships.*
*Other projects: [Sorting Visualizer](https://github.com/Ambitchious/Sorting-Visualizer-) · [Higgs Boson Classifier](https://github.com/Ambitchious/particle-classifier)*
