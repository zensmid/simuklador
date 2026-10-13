from __future__ import annotations
import hashlib
import numpy as np
import pandas as pd
from .base import DataProvider


class SyntheticProvider(DataProvider):
    """Datos deterministas para pruebas y demos sin red."""

    def _rng(self, ticker):
        return np.random.default_rng(int(hashlib.md5(ticker.encode()).hexdigest()[:8], 16))

    def history(self, ticker, days=365):
        rng = self._rng(ticker)
        n = max(days, 60)
        ret = rng.normal(0.0004, 0.015, n)
        close = 100 * np.exp(np.cumsum(ret))
        idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
        high = close * (1 + rng.uniform(0, 0.01, n))
        low = close * (1 - rng.uniform(0, 0.01, n))
        open_ = np.r_[close[0], close[:-1]]
        vol = rng.integers(1_000_000, 5_000_000, n)
        return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol}, index=idx)

    def fundamentals(self, ticker):
        r = self._rng(ticker)
        return {"name": ticker, "sector": "Demo", "pe": float(r.uniform(8, 40)), "forward_pe": float(r.uniform(8, 35)),
                "peg": float(r.uniform(0.5, 3)), "roe": float(r.uniform(0, 0.35)), "profit_margin": float(r.uniform(0, 0.3)),
                "debt_to_equity": float(r.uniform(10, 200)), "revenue_growth": float(r.uniform(-0.05, 0.3)),
                "dividend_yield": float(r.uniform(0, 0.04)), "market_cap": float(r.uniform(1e9, 5e11))}

    def news(self, ticker, limit=15):
        t = ["{t} beats earnings expectations, raises guidance", "Analysts upgrade {t} on strong growth",
             "{t} faces regulatory probe and lawsuit risk", "{t} announces share buyback", "Concerns grow over {t} margin decline"]
        return [{"title": x.format(t=ticker), "publisher": "demo", "link": "", "published": ""} for x in t][:limit]
