from __future__ import annotations
import pandas as pd
from .base import DataProvider


SUFFIX = {"HK": ".HK", "KS": ".KS", "KQ": ".KQ", "IJ": ".JK", "JP": ".T", "TT": ".TW", "NA": ".AS", "LN": ".L",
          "GR": ".DE", "FP": ".PA", "IM": ".MI", "SM": ".MC", "SW": ".SW", "AU": ".AX", "CN": ".TO", "SS": ".ST",
          "DC": ".CO", "FH": ".HE", "NO": ".OL", "BB": ".BR", "ID": ".IR", "PL": ".LS", "SP": ".SI", "MK": ".KL",
          "TB": ".BK", "IN": ".NS", "CH": ".SS", "CS": ".SZ", "BZ": ".SA", "MM": ".MX", "SJ": ".JO"}


def to_yahoo(t: str) -> str:
    """Ticker Bloomberg ('2899 HK', 'AAPL US Equity') -> Yahoo ('2899.HK', 'AAPL')."""
    parts = t.strip().split()
    if len(parts) >= 2 and parts[1].upper() in ("US", "UN", "UW", "UQ", "UA"):
        return parts[0].replace("/", "-")
    if len(parts) >= 2 and parts[1].upper() in SUFFIX:
        code = parts[0].lstrip("0") or "0" if parts[1].upper() == "HK" else parts[0]
        if parts[1].upper() == "HK":
            code = code.zfill(4)
        return code + SUFFIX[parts[1].upper()]
    return t


_last = [0.0]


def _call(fn, tries: int = 4, gap: float = 1.0):
    """Espacia las llamadas y reintenta con espera creciente ante 'Too Many Requests'."""
    import time
    for i in range(tries):
        wait = _last[0] + gap - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            if i == tries - 1 or not any(k in str(e).lower() for k in ("too many", "rate", "429", "timed out")):
                raise
            time.sleep(5 * 2 ** i)


class YFinanceProvider(DataProvider):
    def history(self, ticker, days=365):
        import yfinance as yf
        ticker = to_yahoo(ticker)
        df = _call(lambda: yf.Ticker(ticker).history(period=f"{max(days, 30)}d", auto_adjust=True))
        if df.empty:
            raise ValueError(f"Sin datos para {ticker}")
        df.columns = [c.lower() for c in df.columns]
        df.index = df.index.tz_localize(None)
        return df[["open", "high", "low", "close", "volume"]]

    def fundamentals(self, ticker):
        import yfinance as yf
        ticker = to_yahoo(ticker)
        i = _call(lambda: yf.Ticker(ticker).info) or {}
        return {"name": i.get("shortName", ticker), "sector": i.get("sector"), "pe": i.get("trailingPE"),
                "forward_pe": i.get("forwardPE"), "peg": i.get("pegRatio") or i.get("trailingPegRatio"),
                "roe": i.get("returnOnEquity"), "profit_margin": i.get("profitMargins"),
                "debt_to_equity": i.get("debtToEquity"), "revenue_growth": i.get("revenueGrowth"),
                "dividend_yield": i.get("dividendYield"), "market_cap": i.get("marketCap")}

    def news(self, ticker, limit=15):
        import yfinance as yf
        ticker = to_yahoo(ticker)
        out = []
        for n in (_call(lambda: yf.Ticker(ticker).news) or [])[:limit]:
            c = n.get("content", n)
            out.append({"title": c.get("title", ""), "publisher": (c.get("provider") or {}).get("displayName", ""),
                        "link": (c.get("canonicalUrl") or {}).get("url", ""), "published": c.get("pubDate", "")})
        return out
