from __future__ import annotations


def pct(v): return "n/d" if v is None else f"{v:+.1%}"


def to_markdown(a: dict) -> str:
    t, f, s = a["technical"], a["fundamental"], a["sentiment"]
    L = [f"# {a['ticker']} — {a['recommendation']} (score {a['score']:+.2f})", "",
         f"Precio: {t['price']:.2f} | Stop sugerido (2×ATR): {t['stop_suggested']:.2f} | Volatilidad anual: {t['volatility_ann']:.1%}", "",
         f"## Técnico ({t['score']:+.2f})", *[f"- {x}" for x in t["notes"]],
         f"- Rendimientos: 1M {pct(t['ret_1m'])}, 3M {pct(t['ret_3m'])}, 1A {pct(t['ret_1y'])}", "",
         f"## Fundamental ({f['score']:+.2f})", *[f"- {x}" for x in f["notes"]], "",
         f"## Sentimiento de noticias ({s['score']:+.2f}, {s['count']} titulares)",
         *[f"- [{i['sentiment']:+d}] {i['title']}" for i in s["items"][:8]]]
    return "\n".join(L)
