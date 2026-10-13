from __future__ import annotations
import numpy as np
import pandas as pd
from .analysis.technical import rsi, macd


def backtest(df: pd.DataFrame, fast=50, slow=200) -> dict:
    """Cruce de medias (long/flat) vs buy&hold. Posición con retraso de 1 día para evitar look-ahead."""
    c = df["close"]
    pos = (c.rolling(fast).mean() > c.rolling(slow).mean()).astype(float).shift(1).fillna(0)
    r = c.pct_change().fillna(0)
    strat = pos * r
    def stats(x):
        eq = (1 + x).cumprod()
        dd = (eq / eq.cummax() - 1).min()
        sharpe = x.mean() / x.std() * np.sqrt(252) if x.std() else 0.0
        return {"total_return": float(eq.iloc[-1] - 1), "sharpe": float(sharpe), "max_drawdown": float(dd)}
    return {"strategy": stats(strat), "buy_hold": stats(r), "trades": int((pos.diff().abs() > 0).sum())}
