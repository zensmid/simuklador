from __future__ import annotations
import json, os
import anthropic
from .providers import get_provider
from .analysis.engine import analyze
from .backtest import backtest

MODEL = os.environ.get("ANALYST_MODEL", "claude-sonnet-5-5")
SYSTEM = ("Eres un analista de trading para un concurso de inversión. Usa siempre las herramientas para obtener datos "
          "reales; nunca inventes cifras. Entrega: recomendación, tesis (técnica, fundamental, catalizadores), riesgos, "
          "stop-loss y tamaño de posición sugerido. Sé claro sobre la incertidumbre; no es asesoría financiera.")
TOOLS = [
    {"name": "analyze_ticker", "description": "Análisis técnico+fundamental+sentimiento con score y recomendación.",
     "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}},
    {"name": "backtest_ma_cross", "description": "Backtest de cruce de medias vs buy&hold.",
     "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}, "fast": {"type": "integer"}, "slow": {"type": "integer"}}, "required": ["ticker"]}},
]


def run_tool(name, args):
    prov = get_provider()
    if name == "analyze_ticker":
        a = analyze(args["ticker"], prov); a.pop("chart", None)
        a["sentiment"]["items"] = a["sentiment"]["items"][:8]
        return a
    if name == "backtest_ma_cross":
        return backtest(prov.history(args["ticker"], 1500), args.get("fast", 50), args.get("slow", 200))
    raise ValueError(name)


def ask(client, messages):
    while True:
        r = client.messages.create(model=MODEL, max_tokens=2000, system=SYSTEM, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            return "".join(b.text for b in r.content if b.type == "text")
        results = []
        for b in r.content:
            if b.type == "tool_use":
                try: out = json.dumps(run_tool(b.name, b.input), default=str)
                except Exception as e: out = f"error: {e}"
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": results})


def chat(question=None):
    client = anthropic.Anthropic()
    messages = []
    if question:
        messages.append({"role": "user", "content": question}); print(ask(client, messages)); return
    print("Analista (Ctrl+C para salir)")
    while True:
        q = input("> ")
        messages.append({"role": "user", "content": q}); print(ask(client, messages), "\n")
