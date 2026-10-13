"""Briefing con Claude: contexto de mercado + eventos + titulares -> escenarios por posición."""
from __future__ import annotations
import os
from .events import earnings_info, format_events
from .market import snapshot, format_snapshot
from .providers import get_provider
from .analysis.sentiment import analyze_sentiment

SYSTEM = ("Eres analista senior para el Bloomberg Trading Challenge (largo solo, ≤20% por posición, se mide Relative P&L, "
          "horizonte 12-oct a 13-nov-2026). Usa ÚNICAMENTE los datos del contexto; si falta un dato, dilo. No inventes cifras ni fechas. "
          "Entrega en español: 1) Panorama de mercado y qué importa para estas posiciones. 2) Por cada posición con resultados Q3 "
          "próximos o recientes: qué se espera, riesgos, y tres escenarios (alcista/base/bajista) con probabilidades SUBJETIVAS que sumen 100%. "
          "3) Acciones concretas sugeridas (mantener/recortar/añadir) y por qué. 4) Calendario de eventos de los próximos 14 días. "
          "Sé explícito: son estimaciones, no certezas ni asesoría financiera.")


def build_context(tickers: list[str], max_news: int = 6) -> str:
    prov = get_provider()
    parts = ["## Mercado\n" + format_snapshot(snapshot())]
    infos = []
    for t in tickers:
        try: infos.append(earnings_info(t))
        except Exception as e: print(f"{t}: {e}")  # noqa: BLE001,E701
    parts.append("## Resultados y consenso\n" + format_events(infos))
    news = []
    for t in tickers:
        try:
            items = analyze_sentiment(prov.news(t, max_news))["items"]
            if items: news.append(f"### {t}\n" + "\n".join(f"- [{i['sentiment']:+d}] {i['title']}" for i in items))
        except Exception:  # noqa: BLE001
            pass
    parts.append("## Titulares recientes\n" + ("\n".join(news) or "n/d"))
    return "\n\n".join(parts)


def brief(tickers: list[str]) -> tuple[str, str]:
    """Devuelve (contexto, informe). Sin ANTHROPIC_API_KEY solo hay contexto."""
    ctx = build_context(tickers)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return ctx, "_Sin ANTHROPIC_API_KEY: solo contexto de datos._"
    import anthropic
    r = anthropic.Anthropic().messages.create(model=os.environ.get("ANALYST_MODEL", "claude-sonnet-5-5"), max_tokens=3500,
                                              system=SYSTEM, messages=[{"role": "user", "content": ctx}])
    return ctx, "".join(b.text for b in r.content if b.type == "text")
