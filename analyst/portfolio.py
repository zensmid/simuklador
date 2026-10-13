from __future__ import annotations
import math
import pandas as pd
from . import contest
from .analysis.engine import analyze
from .providers.base import DataProvider


def cap_weights(raw: dict[str, float], cap: float = contest.MAX_WEIGHT) -> dict[str, float]:
    """Normaliza a suma 1 limitando cada peso a `cap` y redistribuyendo el exceso."""
    if len(raw) * cap < 1 - 1e-9:
        raise ValueError(f"Con tope {cap:.0%} se necesitan al menos {math.ceil(1 / cap)} posiciones")
    w, fixed = dict(raw), {}
    while True:
        free = {k: v for k, v in w.items() if k not in fixed}
        budget = 1 - sum(fixed.values())
        tot = sum(free.values())
        scaled = {k: v / tot * budget for k, v in free.items()}
        over = [k for k, v in scaled.items() if v > cap + 1e-12]
        if not over:
            return {**fixed, **scaled}
        for k in over:
            fixed[k] = cap


def build_portfolio(tickers: list[str], provider: DataProvider, capital: float = contest.CAPITAL,
                    n: int = 12, min_score: float = -0.1, benchmark_vol: float | None = None) -> dict:
    """Long-only, ≤20% por posición, 100% invertido, acciones enteras.
    Peso ∝ (score + 1) / volatilidad (tilt por señal con riesgo ajustado)."""
    rows = []
    for t in tickers:
        try:
            a = analyze(t, provider)
            rows.append({"ticker": a["ticker"], "score": a["score"], "rec": a["recommendation"],
                         "price": a["technical"]["price"], "vol": max(a["technical"]["volatility_ann"], 0.05)})
        except Exception as e:  # noqa: BLE001
            print(f"  {t}: omitido ({e})")
    df = pd.DataFrame(rows).sort_values("score", ascending=False)
    pick = df[df.score >= min_score].head(max(n, contest.MIN_POSITIONS))
    if len(pick) < contest.MIN_POSITIONS:
        pick = df.head(contest.MIN_POSITIONS)  # obligatorio: ≥5 posiciones para invertir 100%
    raw = {r.ticker: (r.score + 1) / r.vol for r in pick.itertuples()}
    w = cap_weights(raw)

    px = {r.ticker: r.price for r in pick.itertuples()}
    shares = {t: int(w[t] * capital // px[t]) for t in w}
    cash = capital - sum(shares[t] * px[t] for t in w)
    # Reparte el efectivo sobrante comprando acciones respetando el 20%
    for t in sorted(w, key=lambda k: w[k] - shares[k] * px[k] / capital, reverse=True) * 50:
        if px[t] <= cash and (shares[t] + 1) * px[t] <= contest.MAX_WEIGHT * capital:
            shares[t] += 1; cash -= px[t]
    out = pick.set_index("ticker").copy()
    out["shares"] = pd.Series(shares)
    out["value"] = out.shares * out.price
    out["weight"] = out.value / capital
    return {"positions": out.reset_index().to_dict("records"), "cash": cash, "invested": 1 - cash / capital,
            "max_weight": float(out.weight.max()), "capital": capital}


def format_portfolio(p: dict) -> str:
    L = [f"{'Ticker':8}{'Rec':15}{'Score':>7}{'Precio':>10}{'Acciones':>10}{'Valor':>13}{'Peso':>8}"]
    for r in sorted(p["positions"], key=lambda r: -r["value"]):
        L.append(f"{r['ticker']:8}{r['rec']:15}{r['score']:>+7.2f}{r['price']:>10.2f}{r['shares']:>10,}{r['value']:>13,.0f}{r['weight']:>8.1%}")
    L.append(f"\nInvertido {p['invested']:.2%} | Efectivo ${p['cash']:,.0f} | Peso máx {p['max_weight']:.1%} (límite 20%)")
    return "\n".join(L)


def rebalance(holdings: dict[str, float], candidates: list[str], provider: DataProvider,
              capital: float = contest.CAPITAL, n_new: int = 3, trim_to: float = 0.195,
              new_cap: float = 0.10, min_score: float = -0.1) -> dict:
    """Parte de las posiciones actuales (USD), recorta las que superan el 20% y
    reparte efectivo libre + recortes en nuevas posiciones. Órdenes en dólares
    (la Terminal pide el monto en USD por operación)."""
    orders, hold = [], dict(holdings)
    for t, v in list(hold.items()):
        if v > trim_to * capital:
            orders.append({"ticker": t, "action": "RECORTAR", "usd": v - trim_to * capital, "note": f"{v / capital:.1%} -> {trim_to:.1%}"})
            hold[t] = trim_to * capital
    cash = capital - sum(hold.values())
    ranked = []
    for t in candidates:
        if t in hold:
            continue
        try:
            a = analyze(t, provider)
            ranked.append((a["score"], t, a["recommendation"], max(a["technical"]["volatility_ann"], 0.05)))
        except Exception as e:  # noqa: BLE001
            print(f"  {t}: omitido ({e})")
    ranked.sort(reverse=True)
    pick = [r for r in ranked if r[0] >= min_score][:n_new] or ranked[:n_new]
    if cash > 1 and pick:
        raw = {t: (s + 1) / v for s, t, _, v in pick}
        # tope por posición nueva; si el efectivo es chico, el tope pesa poco
        frac_cap = min(1.0, max(new_cap * capital / cash, 1 / len(raw)))
        w = cap_weights(raw, frac_cap)
        info = {t: (s, r) for s, t, r, _ in pick}
        for t, f in w.items():
            orders.append({"ticker": t, "action": "COMPRAR", "usd": f * cash,
                           "note": f"{info[t][1]}, score {info[t][0]:+.2f}"})
    final = dict(hold)
    for o in orders:
        if o["action"] == "COMPRAR":
            final[o["ticker"]] = final.get(o["ticker"], 0) + o["usd"]
    return {"orders": orders, "final": final, "cash_after": capital - sum(final.values()),
            "max_weight": max(final.values()) / capital if final else 0}


def format_rebalance(r: dict, capital: float = contest.CAPITAL) -> str:
    L = ["ÓRDENES (monto en USD):"]
    for o in r["orders"]:
        L.append(f"  {o['action']:9}{o['ticker']:12}${o['usd']:>12,.0f}   {o['note']}")
    L += ["", "CARTERA RESULTANTE:"]
    for t, v in sorted(r["final"].items(), key=lambda kv: -kv[1]):
        L.append(f"  {t:12}${v:>12,.0f} {v / capital:>7.1%}")
    L.append(f"\nEfectivo sin invertir: ${r['cash_after']:,.0f} | Peso máx {r['max_weight']:.1%} (límite 20%)")
    return "\n".join(L)
