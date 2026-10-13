from __future__ import annotations
import re

POS = {"beat", "beats", "upgrade", "upgrades", "growth", "surge", "record", "strong", "buyback", "raises", "profit",
       "outperform", "rally", "gains", "bullish", "expands", "wins", "approval", "dividend"}
NEG = {"miss", "misses", "downgrade", "downgrades", "lawsuit", "probe", "decline", "falls", "plunge", "weak", "cuts",
       "loss", "losses", "recall", "fraud", "bearish", "concerns", "risk", "layoffs", "investigation", "warning"}


def analyze_sentiment(items: list[dict]) -> dict:
    """Léxico simple y transparente; el agente de Claude puede refinarlo."""
    tot, scored = 0.0, []
    for it in items:
        w = set(re.findall(r"[a-z]+", it.get("title", "").lower()))
        s = len(w & POS) - len(w & NEG)
        s = max(-1, min(1, s))
        tot += s
        scored.append({**it, "sentiment": s})
    n = len(scored)
    return {"score": (tot / n) if n else 0.0, "count": n, "items": scored}
