from __future__ import annotations
import os
import pandas as pd
import requests
from .base import DataProvider

URL = "https://www.alphavantage.co/query"


class AlphaVantageProvider(DataProvider):
    def __init__(self, key: str | None = None):
        self.key = key or os.environ.get("ALPHAVANTAGE_API_KEY")
        if not self.key:
            raise RuntimeError("Falta ALPHAVANTAGE_API_KEY")

    def _get(self, **p):
        r = requests.get(URL, params={**p, "apikey": self.key}, timeout=30)
        r.raise_for_status()
        return r.json()

    def history(self, ticker, days=365):
        d = self._get(function="TIME_SERIES_DAILY", symbol=ticker, outputsize="full")
        ts = d.get("Time Series (Daily)")
        if not ts:
            raise ValueError(f"Sin datos para {ticker}: {d}")
        df = pd.DataFrame(ts).T.astype(float)
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index = pd.to_datetime(df.index)
        return df.sort_index().tail(days)

    def fundamentals(self, ticker):
        o = self._get(function="OVERVIEW", symbol=ticker)
        f = lambda k: float(o[k]) if o.get(k) not in (None, "None", "-", "") else None
        return {"name": o.get("Name", ticker), "sector": o.get("Sector"), "pe": f("TrailingPE"), "forward_pe": f("ForwardPE"),
                "peg": f("PEGRatio"), "roe": f("ReturnOnEquityTTM"), "profit_margin": f("ProfitMargin"),
                "debt_to_equity": None, "revenue_growth": f("QuarterlyRevenueGrowthYOY"),
                "dividend_yield": f("DividendYield"), "market_cap": f("MarketCapitalization")}

    def news(self, ticker, limit=15):
        d = self._get(function="NEWS_SENTIMENT", tickers=ticker, limit=limit)
        return [{"title": x.get("title", ""), "publisher": x.get("source", ""), "link": x.get("url", ""),
                 "published": x.get("time_published", "")} for x in d.get("feed", [])[:limit]]
