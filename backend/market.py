# ============================================================
#  market.py  —  Market Data via yfinance (robust version)
# ============================================================

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_price_history(tickers: list, days_back: int = 90) -> dict:
    end   = datetime.now()
    start = end - timedelta(days=days_back)
    result = {}

    for ticker in tickers:
        try:
            # Use .history() instead of .download() — avoids MultiIndex issues
            t    = yf.Ticker(ticker)
            data = t.history(start=start, end=end, auto_adjust=True)

            if data is None or data.empty:
                print(f"[market] No data for {ticker}")
                continue

            closes = data["Close"].dropna()
            if closes.empty:
                continue

            base = float(closes.iloc[0])
            if base == 0:
                continue

            result[ticker] = [
                {
                    "date":       str(idx.date()),
                    "close":      round(float(val), 2),
                    "pct_change": round(((float(val) - base) / base) * 100, 2),
                }
                for idx, val in closes.items()
            ]
            print(f"[market] {ticker}: {len(result[ticker])} data points OK")

        except Exception as e:
            print(f"[market] Error fetching {ticker}: {e}")

    return result


def get_current_prices(tickers: list) -> dict:
    result = {}
    for ticker in tickers:
        try:
            t    = yf.Ticker(ticker)
            info = t.fast_info
            result[ticker] = {
                "price":      round(float(info.last_price), 2),
                "pct_change": round(float(info.three_month_return or 0) * 100, 2),
            }
        except Exception as e:
            print(f"[market] Price error for {ticker}: {e}")
    return result
