"""Calendario de resultados (Q3), estimaciones/objetivos de analistas y reacción histórica del precio."""
from __future__ import annotations
import datetime as dt
import pandas as pd
from .providers.yf import to_yahoo, _call


def earnings_info(ticker: str, window_days: int = 30) -> dict:
    """Próxima fecha de resultados, EPS estimado, reacciones pasadas y consenso. Todo opcional (Yahoo puede fallar)."""
    import yfinance as yf
    y = to_yahoo(ticker)
    t = yf.Ticker(y)
    out: dict = {"ticker": ticker, "next_date": None, "days_to": None, "eps_est": None, "history": [], "targets": {}}
    try:
        ed = _call(lambda: t.get_earnings_dates(limit=12))
        if ed is not None and not ed.empty:
            ed = ed.copy(); ed.index = ed.index.tz_localize(None) if ed.index.tz is None else ed.index.tz_convert(None)
            now = pd.Timestamp.now()
            fut = ed[ed.index >= now.normalize()]
            if not fut.empty:
                nxt = fut.index.min()
                out["next_date"] = nxt.strftime("%Y-%m-%d"); out["days_to"] = int((nxt - now).days)
                est = fut.loc[nxt].get("EPS Estimate")
                out["eps_est"] = None if pd.isna(est) else float(est)
            px = _call(lambda: t.history(period="2y", auto_adjust=True))["Close"]; px.index = px.index.tz_localize(None)
            for d, r in ed[ed.index < now.normalize()].head(4).iterrows():
                after = px[px.index >= d.normalize()]; before = px[px.index < d.normalize()]
                if len(after) >= 2 and len(before):
                    out["history"].append({"date": d.strftime("%Y-%m-%d"), "surprise_pct": None if pd.isna(r.get("Surprise(%)")) else float(r["Surprise(%)"]),
                                           "move_1d": float(after.iloc[1] / before.iloc[-1] - 1)})
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)
    try:
        i = _call(lambda: t.info) or {}
        out["targets"] = {k: i.get(k) for k in ("targetMeanPrice", "targetHighPrice", "targetLowPrice", "recommendationMean",
                                                 "numberOfAnalystOpinions", "currentPrice")}
    except Exception:  # noqa: BLE001
        pass
    return out


def format_events(infos: list[dict]) -> str:
    L = ["| Ticker | Resultados | Días | EPS est. | Últimas reacciones (1d) | Obj. analistas |", "|---|---|---|---|---|---|"]
    for i in sorted(infos, key=lambda x: (x["days_to"] is None, x["days_to"] or 0)):
        h = ", ".join(f"{x['move_1d']:+.1%}" for x in i["history"]) or "n/d"
        tg = i["targets"]; tm, cp = tg.get("targetMeanPrice"), tg.get("currentPrice")
        up = f"{tm:.2f} ({tm / cp - 1:+.0%})" if tm and cp else "n/d"
        eps = f"{i['eps_est']:.2f}" if i["eps_est"] is not None else "n/d"
        L.append(f"| {i['ticker']} | {i['next_date'] or 'n/d'} | {i['days_to'] if i['days_to'] is not None else '-'} | {eps} | {h} | {up} |")
    return "\n".join(L)
