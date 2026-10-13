from __future__ import annotations
import pandas as pd
from .base import DataProvider


class YFinanceProvider(DataProvider):
    def history(self, ticker, days=365):
        import yfinance as yf
        df = yf.Ticker(ticker).history(period=f"{max(days, 30)}d", auto_adjust=True)
        if df.empty:
            raise ValueError(f"Sin datos para {ticker}")
        df.columns = [c.lower() for c in df.columns]
        df.index = df.index.tz_localize(None)
        return df[["open", "high", "low", "close", "volume"]]

    def fundamentals(self, ticker):
        import yfinance as yf
        i = yf.Ticker(ticker).info or {}
        return {"name": i.get("shortName", ticker), "sector": i.get("sector"), "pe": i.get("trailingPE"),
                "forward_pe": i.get("forwardPE"), "peg": i.get("pegRatio") or i.get("trailingPegRatio"),
                "roe": i.get("returnOnEquity"), "profit_margin": i.get("profitMargins"),
                "debt_to_equity": i.get("debtToEquity"), "revenue_growth": i.get("revenueGrowth"),
                "dividend_yield": i.get("dividendYield"), "market_cap": i.get("marketCap")}

    def news(self, ticker, limit=15):
        import yfinance as yf
        out = []
        for n in (yf.Ticker(ticker).news or [])[:limit]:
            c = n.get("content", n)
            out.append({"title": c.get("title", ""), "publisher": (c.get("provider") or {}).get("displayName", ""),
                        "link": (c.get("canonicalUrl") or {}).get("url", ""), "published": c.get("pubDate", "")})
        return out
