from __future__ import annotations
import numpy as np
import pandas as pd


def rsi(c: pd.Series, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def macd(c: pd.Series):
    line = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = line.ewm(span=9, adjust=False).mean()
    return line, sig


def atr(df: pd.DataFrame, n=14):
    pc = df["close"].shift()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def analyze_technical(df: pd.DataFrame) -> dict:
    c = df["close"]
    last = float(c.iloc[-1])
    sma20, sma50 = c.rolling(20).mean(), c.rolling(50).mean()
    sma200 = c.rolling(200).mean()
    r = rsi(c)
    m, s = macd(c)
    bb_mid, bb_sd = sma20, c.rolling(20).std()
    pctb = (last - (bb_mid.iloc[-1] - 2 * bb_sd.iloc[-1])) / (4 * bb_sd.iloc[-1]) if bb_sd.iloc[-1] else 0.5
    a = float(atr(df).iloc[-1])
    ret = lambda n: float(c.iloc[-1] / c.iloc[-n - 1] - 1) if len(c) > n else None

    score, notes = 0.0, []
    if not np.isnan(sma50.iloc[-1]):
        if last > sma50.iloc[-1]:
            score += 1; notes.append("Precio sobre SMA50")
        else:
            score -= 1; notes.append("Precio bajo SMA50")
    if not np.isnan(sma200.iloc[-1]):
        if sma50.iloc[-1] > sma200.iloc[-1]:
            score += 1; notes.append("SMA50 > SMA200 (tendencia alcista)")
        else:
            score -= 1; notes.append("SMA50 < SMA200 (tendencia bajista)")
    rv = float(r.iloc[-1])
    if rv < 30:
        score += 1; notes.append(f"RSI {rv:.0f}: sobreventa")
    elif rv > 70:
        score -= 1; notes.append(f"RSI {rv:.0f}: sobrecompra")
    if m.iloc[-1] > s.iloc[-1]:
        score += 1; notes.append("MACD sobre su señal")
    else:
        score -= 1; notes.append("MACD bajo su señal")
    mom = ret(63)
    if mom is not None:
        score += 1 if mom > 0 else -1
        notes.append(f"Momentum 3M {mom:+.1%}")
    return {
        "price": last, "rsi": rv, "macd": float(m.iloc[-1]), "macd_signal": float(s.iloc[-1]),
        "sma20": _f(sma20), "sma50": _f(sma50), "sma200": _f(sma200), "bollinger_pctb": float(pctb),
        "atr": a, "ret_1m": ret(21), "ret_3m": mom, "ret_1y": ret(252),
        "volatility_ann": float(c.pct_change().std() * np.sqrt(252)),
        "stop_suggested": last - 2 * a,
        "score": float(np.clip(score / 5, -1, 1)), "notes": notes,
    }


def _f(s):
    v = s.iloc[-1]
    return None if np.isnan(v) else float(v)
