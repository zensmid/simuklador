"""Escaneo continuo del universo: filtro técnico rápido en lote -> análisis completo del top -> reporte."""
from __future__ import annotations
import csv, json, os, datetime as dt
import pandas as pd
from . import contest
from .analysis.technical import analyze_technical
from .analysis.engine import analyze
from .portfolio import rebalance, format_rebalance
from .providers import get_provider
from .providers.yf import to_yahoo


def load_universe(path: str) -> list[str]:
    return [l.split("#")[0].strip() for l in open(path, encoding="utf-8") if l.split("#")[0].strip()]


def _batch(tickers: list[str], days: int, chunk: int = 80) -> dict[str, pd.DataFrame]:
    import yfinance as yf
    out = {}
    for i in range(0, len(tickers), chunk):
        part = {to_yahoo(t): t for t in tickers[i:i + chunk]}
        try:
            d = yf.download(list(part), period=f"{days}d", auto_adjust=True, group_by="ticker", threads=True, progress=False)
        except Exception as e:  # noqa: BLE001
            print(f"lote {i}: {e}"); continue
        for y, t in part.items():
            try:
                df = (d[y] if len(part) > 1 else d).dropna(subset=["Close"])
                df.columns = [c.lower() for c in df.columns]
                if len(df) >= 120 and df["volume"].tail(20).mean() > 0:
                    out[t] = df[["open", "high", "low", "close", "volume"]]
            except Exception:  # noqa: BLE001
                pass
    return out


class CachedProvider:
    """Sirve el historial ya descargado en lote y delega fundamentales/noticias (con reintentos) al proveedor real."""

    def __init__(self, base, cache: dict):
        self.base, self.cache = base, cache

    def history(self, ticker, days=365):
        df = self.cache.get(ticker)
        return df.tail(days) if df is not None else self.base.history(ticker, days)

    def fundamentals(self, ticker):
        return self.base.fundamentals(ticker)

    def news(self, ticker, limit=15):
        return self.base.news(ticker, limit)


def screen(universe: list[str], days: int = 300, min_dollar_vol: float = 1e6, cache: dict | None = None) -> pd.DataFrame:
    rows = []
    data = _batch(universe, days)
    if cache is not None:
        cache.update(data)
    for t, df in data.items():
        try:
            tech = analyze_technical(df)
        except Exception:  # noqa: BLE001
            continue
        if tech["price"] * df["volume"].tail(20).mean() < min_dollar_vol:   # liquidez (moneda local, filtro grueso)
            continue
        rows.append({"ticker": t, "tech_score": tech["score"], "ret_3m": tech["ret_3m"], "ret_1y": tech["ret_1y"],
                     "vol": tech["volatility_ann"], "rsi": tech["rsi"]})
    return pd.DataFrame(rows).sort_values("tech_score", ascending=False)


def run(universe_path: str, holdings_path: str | None = None, top: int = 40, outdir: str = "reports", docs_dir: str = "docs") -> str:
    os.makedirs(outdir, exist_ok=True)
    uni = load_universe(universe_path)
    hold = {}
    if holdings_path and os.path.exists(holdings_path):
        hold = {r[0].strip(): float(r[1]) for r in csv.reader(l for l in open(holdings_path) if l.strip() and not l.startswith("#"))}
    cash = hold.pop("CASH", None)   # efectivo disponible (Terminal: "Efectivo disponible")
    cache: dict = {}
    scr = screen(uni, cache=cache)
    held = [t for t in hold if t != "OTHER"]
    missing = [t for t in held if t not in cache]
    if missing:
        cache.update(_batch(missing, 300))
    now = dt.datetime.now(dt.timezone.utc)
    prov = CachedProvider(get_provider(), cache)
    deep = []
    for t in scr.head(top).ticker:
        try:
            a = analyze(t, prov); deep.append((a["score"], t, a))
        except Exception as e:  # noqa: BLE001
            print(f"{t}: {e}")
    deep.sort(reverse=True, key=lambda x: x[0])
    L = [f"# Scan {now:%Y-%m-%d %H:%M} UTC", f"Universo: {len(uni)} | con datos y liquidez: {len(scr)} | análisis completo: {len(deep)}", "",
         "| # | Ticker | Rec | Score | Téc | Fund | Noticias | 3M | 1A |", "|---|---|---|---|---|---|---|---|---|"]
    for i, (s, t, a) in enumerate(deep[:25], 1):
        tc = a["technical"]
        L.append(f"| {i} | {t} | {a['recommendation']} | {s:+.2f} | {tc['score']:+.2f} | {a['fundamental']['score']:+.2f} | "
                 f"{a['sentiment']['score']:+.2f} | {tc['ret_3m']:+.0%} | {(tc['ret_1y'] or 0):+.0%} |")
    if hold:
        reb = rebalance(hold, [t for _, t, _ in deep[:15]], prov, contest.CAPITAL, n_new=5, cash=cash)
        L += ["", "## Rebalanceo sugerido", "```", format_rebalance(reb), "```"]
    # Contexto: resultados Q3, mercado, noticias, briefing de Claude y export para el dashboard
    focus = list(dict.fromkeys(held + [t for _, t, _ in deep[:10]]))
    data, rep = None, "_Sin briefing_"
    try:
        from .brief import brief, gather
        data = gather(focus)
        ctx, rep = brief(focus, data)
        open(os.path.join(outdir, "events.md"), "w", encoding="utf-8").write(f"# Contexto {now:%Y-%m-%d %H:%M} UTC\n\n{ctx}\n")
        open(os.path.join(outdir, "brief.md"), "w", encoding="utf-8").write(f"# Briefing {now:%Y-%m-%d %H:%M} UTC\n\n{rep}\n")
        L += ["", "Ver también: `events.md` (mercado, resultados Q3, titulares) y `brief.md` (escenarios con Claude)."]
    except Exception as e:  # noqa: BLE001
        L += ["", f"_Briefing no disponible: {e}_"]
    try:
        from .export import export_dashboard
        export_dashboard(now, uni, scr, deep, hold, reb if hold else None, data, rep, prov, docs_dir, cash)
    except Exception as e:  # noqa: BLE001
        L += ["", f"_Export del dashboard falló: {e}_"]
    L += ["", "_Herramienta educativa; no es asesoría financiera._"]
    md = "\n".join(L)
    open(os.path.join(outdir, "latest.md"), "w", encoding="utf-8").write(md)
    hist = os.path.join(outdir, "history.csv")
    new = not os.path.exists(hist)
    with open(hist, "a", newline="") as f:
        w = csv.writer(f)
        if new: w.writerow(["utc", "ticker", "score", "recommendation"])
        for s, t, a in deep: w.writerow([now.isoformat(timespec="minutes"), t, round(s, 3), a["recommendation"]])
    return md
