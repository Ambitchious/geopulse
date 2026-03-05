# ============================================================
#  analyzer.py  —  AI Analysis Engine (Groq + Llama 3)
#  Generates consulting-style geopolitical impact briefs
# ============================================================

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # load .env BEFORE reading the key

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


def generate_impact_brief(
    query:        str,
    event_type:   str,
    events:       list,
    tone_summary: dict,
    sectors:      dict,
    price_data:   dict,
) -> dict:
    """
    Generate a consulting-style geopolitical impact brief using Llama 3.
    Returns structured analysis with winners, losers, and recommendations.
    """

    # Build context from real data
    recent_headlines = "\n".join(
        f"- [{e['date']}] {e['title']} (tone: {e['tone']:.1f})"
        for e in events[:8]
    )

    bullish_tickers = sectors.get("bullish", [])
    bearish_tickers = sectors.get("bearish", [])

    price_context = ""
    for ticker in bullish_tickers + bearish_tickers:
        if ticker in price_data and price_data[ticker]:
            latest = price_data[ticker][-1]
            price_context += f"\n- {ticker}: {latest['pct_change']:+.1f}% over 90 days"

    prompt = f"""You are a senior geopolitical analyst at a top consulting firm (McKinsey/BCG level).
A client has asked you to analyze the market impact of the following geopolitical situation.

QUERY: {query}
EVENT TYPE: {event_type}
NEWS SENTIMENT: {tone_summary['sentiment']} (avg tone: {tone_summary['avg_tone']}, trend: {tone_summary['trend']})
NUMBER OF RELATED EVENTS: {tone_summary['n_events']} in the past 90 days

RECENT HEADLINES:
{recent_headlines}

SECTOR PRICE PERFORMANCE (90-day):
{price_context}

TYPICALLY AFFECTED SECTORS:
- Bullish: {', '.join(bullish_tickers)}
- Bearish: {', '.join(bearish_tickers)}

Write a concise consulting-style impact brief with EXACTLY these sections:

## SITUATION SUMMARY
2-3 sentences on what's happening geopolitically and why it matters to markets.

## MARKET IMPACT
- **Winners**: Which sectors/assets benefit and why (be specific with mechanisms)
- **Losers**: Which sectors/assets are hurt and why
- **Timeline**: Short-term (1-4 weeks) vs medium-term (3-6 months) outlook

## HISTORICAL PARALLEL
Name ONE specific historical event that is most similar, what happened to markets then, and what that implies now.

## KEY RISKS TO WATCH
3 bullet points of specific triggers that could change the analysis.

## CONSULTING RECOMMENDATION
One clear, actionable recommendation for a portfolio manager in 2 sentences.

Keep the entire brief under 400 words. Be specific, not generic. Use actual numbers where possible."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,    # lower = more factual, less creative
            max_tokens=800,
        )
        brief = response.choices[0].message.content

        return {
            "brief":       brief,
            "model":       MODEL,
            "event_type":  event_type,
            "sentiment":   tone_summary["sentiment"],
            "n_events":    tone_summary["n_events"],
        }

    except Exception as e:
        return {
            "brief":      f"Analysis unavailable: {str(e)}",
            "event_type": event_type,
            "sentiment":  tone_summary.get("sentiment", "unknown"),
            "n_events":   tone_summary.get("n_events", 0),
        }


def generate_quick_summary(query: str) -> str:
    """
    Generate a one-line geopolitical context summary for the search bar.
    Used to validate/enrich the user's query.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # use smaller model for quick tasks
            messages=[{
                "role": "user",
                "content": f"In exactly one sentence, describe the geopolitical significance of: '{query}'. Be factual and concise."
            }],
            temperature=0.1,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"Analyzing geopolitical impact of: {query}"
