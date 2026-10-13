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
