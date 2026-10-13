from __future__ import annotations
from ..providers.base import DataProvider
from .technical import analyze_technical
from .fundamental import analyze_fundamental
from .sentiment import analyze_sentiment

WEIGHTS = {"technical": 0.45, "fundamental": 0.35, "sentiment": 0.20}


def recommendation(score: float) -> str:
    if score >= 0.5: return "COMPRA FUERTE"
    if score >= 0.2: return "COMPRA"
    if score > -0.2: return "MANTENER"
    if score > -0.5: return "VENTA"
    return "VENTA FUERTE"


def analyze(ticker: str, provider: DataProvider, days: int = 365) -> dict:
    ticker = ticker.upper()
    df = provider.history(ticker, days)
    tech = analyze_technical(df)
    try:
        fund = analyze_fundamental(provider.fundamentals(ticker))
    except Exception as e:  # noqa: BLE001
        fund = {"score": 0.0, "notes": [f"Fundamentales no disponibles: {e}"]}
    try:
        sent = analyze_sentiment(provider.news(ticker))
    except Exception as e:  # noqa: BLE001
        sent = {"score": 0.0, "count": 0, "items": [], "error": str(e)}
    total = sum(WEIGHTS[k] * v["score"] for k, v in
                (("technical", tech), ("fundamental", fund), ("sentiment", sent)))
    return {"ticker": ticker, "score": total, "recommendation": recommendation(total), "weights": WEIGHTS,
            "technical": tech, "fundamental": fund, "sentiment": sent,
            "chart": {"dates": [d.strftime("%Y-%m-%d") for d in df.index[-180:]],
                      "close": [round(float(x), 2) for x in df["close"].iloc[-180:]]}}
