"""Estudio de factores: ¿qué señales de precio han predicho el retorno relativo a 1 mes en este universo?

Para cada fin de mes t: rank-IC (Spearman) de cada factor con el retorno de t a t+21 sesiones, menos la mediana
del universo (proxy del índice). Reporta IC medio, t-stat, diferencia quintil superior-universo y % de meses con IC>0.
Sesgos (documentados en el reporte): universo = constituyentes actuales (supervivencia) y solo factores de precio.
"""
from __future__ import annotations
import json, os, datetime as dt
import numpy as np
import pandas as pd

FACTORS = {
    "mom_12_1": "Momentum 12-1 (excluye último mes)",
    "mom_6_1": "Momentum 6-1",
    "mom_3m": "Momentum 3 meses",
    "rev_1m": "Reversión 1 mes (retorno 1M, signo invertido)",
    "trend": "Tendencia (precio/SMA50 + SMA50/SMA200)",
    "near_high": "Cercanía al máximo de 52 semanas",
    "low_vol": "Baja volatilidad 60d (invertida)",
    "rsi_rev": "RSI 14 (invertido: sobreventa mejor)",
}


def features(px: pd.DataFrame) -> dict[str, pd.DataFrame]:
    r = px.pct_change()
    sma50, sma200 = px.rolling(50).mean(), px.rolling(200).mean()
    d = px.diff()
    up = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    return {
        "mom_12_1": px.shift(21) / px.shift(252) - 1,
        "mom_6_1": px.shift(21) / px.shift(126) - 1,
        "mom_3m": px / px.shift(63) - 1,
        "rev_1m": -(px / px.shift(21) - 1),
        "trend": (px / sma50 - 1) + (sma50 / sma200 - 1),
        "near_high": px / px.rolling(252).max(),
        "low_vol": -r.rolling(60).std(),
        "rsi_rev": -rsi,
    }


def run_study(px: pd.DataFrame, horizon: int = 21, min_names: int = 50) -> dict:
    px = px.dropna(axis=1, thresh=int(len(px) * 0.8)).ffill()
    fwd = px.shift(-horizon) / px - 1
    feats = features(px)
    idx = px.index[252:-horizon:21]                      # fines de "mes" (cada 21 sesiones) con historia suficiente
    res = {k: {"ic": [], "spread": []} for k in feats}
    comp_ic, comp_spread = [], []
    for t in idx:
        y = fwd.loc[t]
        ok = y.notna()
        if ok.sum() < min_names:
            continue
        rel = y[ok] - y[ok].median()
        zs = []
        for k, f in feats.items():
            x = f.loc[t][ok]
            m = x.notna()
            if m.sum() < min_names:
                continue
            ic = x[m].rank().corr(rel[m].rank())
            q = x[m] >= x[m].quantile(0.8)
            res[k]["ic"].append(ic); res[k]["spread"].append(rel[m][q].mean())
            zs.append(((x - x[m].mean()) / x[m].std()).reindex(rel.index))
        if zs:
            comp = pd.concat(zs, axis=1).mean(axis=1)
            m = comp.notna()
            comp_ic.append(comp[m].rank().corr(rel[m].rank()))
            comp_spread.append(rel[m][comp[m] >= comp[m].quantile(0.8)].mean())

    def summ(ic, sp):
        ic, sp = np.array(ic, float), np.array(sp, float)
        n = len(ic)
        return {"months": n, "ic_mean": float(np.nanmean(ic)) if n else None,
                "t_stat": float(np.nanmean(ic) / (np.nanstd(ic, ddof=1) / np.sqrt(n))) if n > 2 and np.nanstd(ic) > 0 else None,
                "hit": float(np.nanmean(ic > 0)) if n else None,
                "top_quintile_rel": float(np.nanmean(sp)) if n else None}

    out = {k: {"name": FACTORS[k], **summ(v["ic"], v["spread"])} for k, v in res.items()}
    out["composite_all"] = {"name": "Compuesto (promedio z de todos)", **summ(comp_ic, comp_spread)}
    return {"factors": out, "names": int(px.shape[1]), "sessions": int(len(px)), "horizon": horizon,
            "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes")}


def to_markdown(s: dict) -> str:
    L = [f"# Estudio de factores ({s['generated']} UTC)", f"{s['names']} acciones, {s['sessions']} sesiones, horizonte {s['horizon']} sesiones.", "",
         "| Factor | Meses | IC medio | t-stat | % meses IC>0 | Quintil sup. vs universo |", "|---|---|---|---|---|---|"]
    for k, v in sorted(s["factors"].items(), key=lambda kv: -(kv[1]["t_stat"] or -99)):
        f = lambda x, p=2: "n/d" if x is None else f"{x:.{p}f}"
        L.append(f"| {v['name']} | {v['months']} | {f(v['ic_mean'], 3)} | {f(v['t_stat'])} | {f(v['hit'], 0) if v['hit'] is None else format(v['hit'], '.0%')} | "
                 f"{'n/d' if v['top_quintile_rel'] is None else format(v['top_quintile_rel'], '+.2%')} |")
    L += ["", "Lectura: |t| > 2 sugiere señal distinta de ruido. IC típico útil: 0.02-0.05. Sesgos: universo = constituyentes actuales (supervivencia) y "
          "solo factores de precio; un buen resultado aquí es necesario pero no suficiente.", ""]
    return "\n".join(L)


def run(universe_path: str, outdir: str = "reports", docs_dir: str = "docs", days: int = 1100) -> str:
    from .scan import load_universe, _batch
    data = _batch(load_universe(universe_path), days)
    px = pd.DataFrame({t: df["close"] for t, df in data.items() if len(df) > 400})
    s = run_study(px)
    os.makedirs(outdir, exist_ok=True); os.makedirs(os.path.join(docs_dir, "data"), exist_ok=True)
    md = to_markdown(s)
    open(os.path.join(outdir, "study.md"), "w", encoding="utf-8").write(md)
    json.dump(s, open(os.path.join(docs_dir, "data", "study.json"), "w"))
    return md
