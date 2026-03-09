from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from gdelt    import fetch_gdelt_events, classify_event_type, get_affected_sectors, summarize_tone, TICKER_NAMES
from market   import fetch_price_history
from analyzer import generate_impact_brief, generate_quick_summary

load_dotenv()

app = Flask(__name__)
CORS(app, origins=[
    "https://ambitchious.github.io",
    "http://localhost:3000",
    "http://localhost:5000",
    "http://127.0.0.1:3000",
])


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "GeoPulse API"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data  = request.get_json()
    query = (data or {}).get("query", "").strip()

    if not query or len(query) < 5:
        return jsonify({"error": "Query too short."}), 400

    print(f"[app] Analyzing: '{query}'")

    # 1. Classify
    event_type = classify_event_type(query)
    print(f"[app] Event type: {event_type}")

    # 2. GDELT — fully optional, never crashes the app
    events = []
    try:
        events = fetch_gdelt_events(query, days_back=90, max_results=15)
        print(f"[app] GDELT: {len(events)} events")
    except Exception as e:
        print(f"[app] GDELT skipped: {e}")

    tone = summarize_tone(events)

    # 3. Sectors
    sectors     = get_affected_sectors(event_type)
    all_tickers = sectors["bullish"] + sectors["bearish"]

    # 4. Prices — fully optional, never crashes the app
    price_data = {}
    try:
        price_data = fetch_price_history(all_tickers, days_back=90)
        print(f"[app] Prices fetched: {list(price_data.keys())}")
    except Exception as e:
        print(f"[app] Prices skipped: {e}")

    # 5. AI brief — always runs
    try:
        brief_data = generate_impact_brief(
            query=query,
            event_type=event_type,
            events=events,
            tone_summary=tone,
            sectors=sectors,
            price_data=price_data,
        )
    except Exception as e:
        print(f"[app] Brief error: {e}")
        brief_data = {"brief": "Analysis temporarily unavailable. Please try again."}

    # 6. Context summary — always runs
    try:
        context = generate_quick_summary(query)
    except Exception as e:
        context = f"Geopolitical analysis: {query}"

    return jsonify({
        "query":      query,
        "context":    context,
        "event_type": event_type,
        "tone":       tone,
        "events":     events[:10],
        "sectors": {
            "bullish":     [{"ticker": t, "name": TICKER_NAMES.get(t, t)} for t in sectors["bullish"]],
            "bearish":     [{"ticker": t, "name": TICKER_NAMES.get(t, t)} for t in sectors["bearish"]],
            "description": sectors["description"],
        },
        "prices":   price_data,
        "analysis": brief_data,
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[app] GeoPulse starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
