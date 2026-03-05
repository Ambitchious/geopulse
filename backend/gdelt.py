# ============================================================
#  gdelt.py  —  GDELT Project Event Fetcher
#
#  GDELT (Global Database of Events, Language and Tone) tracks
#  every geopolitical event on earth since 1979, updated every
#  15 minutes. Used by the UN, World Bank, and researchers.
#  Completely free, no API key needed.
# ============================================================

import requests
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse


# GDELT event type codes mapped to readable names
EVENT_CATEGORIES = {
    "war":       ["190", "195", "196"],   # Use of force, conflict
    "sanctions": ["163", "1631"],          # Sanctions, boycotts
    "election":  ["120", "121", "122"],    # Political transitions
    "trade":     ["162", "1621", "1622"],  # Economic cooperation/conflict
    "diplomacy": ["030", "031", "032"],    # Diplomatic contact
}

# Sectors affected by each event type
EVENT_TO_SECTORS = {
    "war": {
        "bullish": ["ITA", "XLE", "GLD"],        # Defence, Energy, Gold
        "bearish": ["EWJ", "EWG", "SPY"],         # Regional markets, broad
        "description": "Military conflicts typically boost defence contractors and energy prices while hurting regional equities."
    },
    "sanctions": {
        "bullish": ["GLD", "SLV", "XLE"],         # Safe havens, Energy
        "bearish": ["EEM", "FXI", "ERUS"],        # Emerging markets, China, Russia
        "description": "Sanctions create supply disruptions boosting commodities while crushing targeted country equities."
    },
    "election": {
        "bullish": ["SPY", "QQQ"],                # Broad market (stability)
        "bearish": ["EEM"],                        # Emerging markets (uncertainty)
        "description": "Elections create short-term volatility; outcome determines sector winners."
    },
    "trade": {
        "bullish": ["XLI", "XLB"],               # Industrials, Materials
        "bearish": ["SMH", "XLK"],               # Semiconductors, Tech
        "description": "Trade disputes hit export-dependent tech and manufacturing sectors hardest."
    },
    "diplomacy": {
        "bullish": ["EEM", "FXI", "SPY"],        # Risk-on assets
        "bearish": ["GLD"],                       # Safe havens (less needed)
        "description": "Diplomatic breakthroughs reduce risk premiums, boosting equities and hurting safe havens."
    }
}

TICKER_NAMES = {
    "ITA": "Aerospace & Defence ETF",
    "XLE": "Energy Sector ETF",
    "GLD": "Gold ETF",
    "SLV": "Silver ETF",
    "EWJ": "Japan ETF",
    "EWG": "Germany ETF",
    "SPY": "S&P 500 ETF",
    "EEM": "Emerging Markets ETF",
    "FXI": "China Large-Cap ETF",
    "ERUS": "Russia ETF",
    "QQQ": "Nasdaq-100 ETF",
    "XLI": "Industrials ETF",
    "XLB": "Materials ETF",
    "SMH": "Semiconductor ETF",
    "XLK": "Technology ETF",
}


def fetch_gdelt_events(query: str, days_back: int = 90, max_results: int = 20) -> list:
    """
    Search GDELT for geopolitical events matching the query.
    Returns list of event dicts with date, headline, tone, url.
    """
    end_date   = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    # GDELT DOC 2.0 API
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query":      query,
        "mode":       "ArtList",
        "maxrecords": max_results,
        "startdatetime": start_date.strftime("%Y%m%d%H%M%S"),
        "enddatetime":   end_date.strftime("%Y%m%d%H%M%S"),
        "format":     "json",
        "sort":       "DateDesc",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])

        events = []
        for art in articles:
            # GDELT tone is a comma-separated string: "overall,pos,neg,polarity,..."
            raw_tone = art.get("tone", "0")
            try:
                tone_val = float(str(raw_tone).split(",")[0])
            except (ValueError, IndexError):
                tone_val = 0.0

            events.append({
                "date":    art.get("seendate", "")[:8],
                "title":   art.get("title", "No title"),
                "url":     art.get("url", ""),
                "source":  art.get("domain", ""),
                "tone":    round(tone_val, 2),
                "country": art.get("sourcecountry", ""),
            })
        return events

    except Exception as e:
        print(f"[gdelt] Error fetching events: {e}")
        return []


def classify_event_type(query: str) -> str:
    """Classify query into event category based on keywords."""
    q = query.lower()
    if any(w in q for w in ["war", "attack", "military", "invasion", "conflict", "missile", "troops"]):
        return "war"
    if any(w in q for w in ["sanction", "ban", "embargo", "restrict", "blockade"]):
        return "sanctions"
    if any(w in q for w in ["election", "vote", "president", "prime minister", "coup", "government"]):
        return "election"
    if any(w in q for w in ["trade", "tariff", "deal", "wto", "export", "import", "supply chain"]):
        return "trade"
    return "diplomacy"


def get_affected_sectors(event_type: str) -> dict:
    """Return sectors affected by this event type."""
    return EVENT_TO_SECTORS.get(event_type, EVENT_TO_SECTORS["diplomacy"])


def summarize_tone(events: list) -> dict:
    """Compute average tone and trend from events list."""
    if not events:
        return {"avg_tone": 0, "trend": "neutral", "n_events": 0}

    tones = [e["tone"] for e in events]
    avg   = sum(tones) / len(tones)
    recent_avg = sum(tones[:5]) / max(len(tones[:5]), 1)

    trend = "escalating" if recent_avg < avg else "de-escalating"
    sentiment = "negative" if avg < -2 else "positive" if avg > 2 else "neutral"

    return {
        "avg_tone":   round(avg, 2),
        "trend":      trend,
        "sentiment":  sentiment,
        "n_events":   len(events),
    }
