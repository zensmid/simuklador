from __future__ import annotations


def analyze_fundamental(f: dict) -> dict:
    pts, notes, n = 0.0, [], 0

    def rule(key, good, bad, label, fmt="{:.2f}"):
        nonlocal pts, n
        v = f.get(key)
        if v is None:
            return
        n += 1
        s = fmt.format(v)
        if good(v):
            pts += 1; notes.append(f"{label} {s}: favorable")
        elif bad(v):
            pts -= 1; notes.append(f"{label} {s}: desfavorable")
        else:
            notes.append(f"{label} {s}: neutral")

    rule("pe", lambda v: 0 < v < 20, lambda v: v <= 0 or v > 35, "P/E")
    rule("peg", lambda v: 0 < v < 1.5, lambda v: v <= 0 or v > 2.5, "PEG")
    rule("roe", lambda v: v > 0.15, lambda v: v < 0.05, "ROE", "{:.1%}")
    rule("profit_margin", lambda v: v > 0.15, lambda v: v < 0.03, "Margen neto", "{:.1%}")
    rule("revenue_growth", lambda v: v > 0.10, lambda v: v < 0, "Crec. ingresos", "{:.1%}")
    rule("debt_to_equity", lambda v: v < 80, lambda v: v > 200, "Deuda/Capital", "{:.0f}")
    return {**f, "score": (pts / n) if n else 0.0, "notes": notes or ["Sin datos fundamentales"]}
