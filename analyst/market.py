"""Panorama de mercado: índices, volatilidad, tasas, dólar, materias primas."""
from __future__ import annotations
import pandas as pd

SYMBOLS = {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "VIX": "^VIX", "10Y UST": "^TNX", "Dólar (DXY)": "DX-Y.NYB",
           "Petróleo WTI": "CL=F", "Oro": "GC=F", "Cobre": "HG=F", "Bitcoin": "BTC-USD", "USD/JPY": "JPY=X", "USD/KRW": "KRW=X",
           "USD/INR": "INR=X", "Nikkei": "^N225", "Kospi": "^KS11", "Hang Seng": "^HSI", "Nifty": "^NSEI", "Taiwan": "^TWII",
           "Jakarta": "^JKSE", "MSCI EM (EEM)": "EEM"}


def snapshot() -> list[dict]:
    import yfinance as yf
    d = yf.download(list(SYMBOLS.values()), period="3mo", auto_adjust=True, group_by="ticker", progress=False, threads=True)
    rows = []
    for name, sym in SYMBOLS.items():
        try:
            c = d[sym]["Close"].dropna()
            rows.append({"name": name, "last": float(c.iloc[-1]), "d1": float(c.iloc[-1] / c.iloc[-2] - 1),
                         "m1": float(c.iloc[-1] / c.iloc[-22] - 1) if len(c) > 22 else None})
        except Exception:  # noqa: BLE001
            pass
    return rows


def format_snapshot(rows: list[dict]) -> str:
    L = ["| Mercado | Último | 1D | 1M |", "|---|---|---|---|"]
    for r in rows:
        m1 = f"{r['m1']:+.1%}" if r["m1"] is not None else "n/d"
        L.append(f"| {r['name']} | {r['last']:,.2f} | {r['d1']:+.2%} | {m1} |")
    return "\n".join(L)
