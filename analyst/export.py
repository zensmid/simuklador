"""Exporta el resultado del escaneo a docs/data/*.json para el dashboard estático (GitHub Pages)."""
from __future__ import annotations
import json, os
from . import contest
from .analysis.engine import analyze


def _clean(o):
    if isinstance(o, dict): return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_clean(v) for v in o]
    if isinstance(o, float): return None if o != o else round(o, 4)
    return o


def _row(a: dict, hist_chart: bool = False) -> dict:
    t, f, s = a["technical"], a["fundamental"], a["sentiment"]
    r = {"ticker": a["ticker"], "rec": a["recommendation"], "score": a["score"], "tech": t["score"], "fund": f["score"], "sent": s["score"],
         "price": t["price"], "rsi": t["rsi"], "ret_1m": t["ret_1m"], "ret_3m": t["ret_3m"], "ret_1y": t["ret_1y"], "vol": t["volatility_ann"],
         "stop": t["stop_suggested"], "tech_notes": t["notes"], "fund_notes": f["notes"], "name": f.get("name"), "sector": f.get("sector"),
         "pe": f.get("pe"), "news": [{"title": i["title"], "s": i["sentiment"], "link": i.get("link", "")} for i in s["items"][:5]]}
    if hist_chart: r["chart"] = a["chart"]
    return r


def export_dashboard(now, universe, screened, deep, hold, reb, data, brief_md, prov, docs_dir="docs"):
    os.makedirs(os.path.join(docs_dir, "data"), exist_ok=True)
    ranking = [_row(a) for _, _, a in deep]
    by = {a["ticker"]: a for _, _, a in deep}
    positions = []
    for t, v in hold.items():
        if t == "OTHER":
            positions.append({"ticker": "OTHER", "value": v, "weight": v / contest.CAPITAL, "unknown": True}); continue
        try:
            a = by.get(t) or analyze(t, prov)
            positions.append({**_row(a, True), "value": v, "weight": v / contest.CAPITAL})
        except Exception as e:  # noqa: BLE001
            positions.append({"ticker": t, "value": v, "weight": v / contest.CAPITAL, "error": str(e)})
    out = {"updated": now.isoformat(timespec="minutes"), "capital": contest.CAPITAL, "max_weight": contest.MAX_WEIGHT,
           "universe": len(universe), "screened": len(screened), "ranking": ranking, "positions": positions,
           "orders": (reb or {}).get("orders", []), "final": (reb or {}).get("final", {}), "cash_after": (reb or {}).get("cash_after"),
           "market": (data or {}).get("snapshot", []), "events": (data or {}).get("infos", []),
           "news": (data or {}).get("news", {}), "brief": brief_md,
           "deadline": contest.INVEST_DEADLINE}
    with open(os.path.join(docs_dir, "data", "latest.json"), "w", encoding="utf-8") as f:
        json.dump(_clean(out), f, ensure_ascii=False)
    hp = os.path.join(docs_dir, "data", "history.json")
    hist = json.load(open(hp)) if os.path.exists(hp) else []
    hist.append({"t": now.isoformat(timespec="minutes"), "scores": {r["ticker"]: round(r["score"], 3) for r in ranking[:25]},
                 "positions": {p["ticker"]: round(p["score"], 3) for p in positions if "score" in p}})
    json.dump(hist[-400:], open(hp, "w"))
