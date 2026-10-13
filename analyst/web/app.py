from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from ..providers import get_provider
from ..analysis.engine import analyze
from ..backtest import backtest

app = FastAPI(title="Analista de trading")


@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "index.html").read_text(encoding="utf-8")


@app.get("/api/analyze/{ticker}")
def api_analyze(ticker: str):
    try:
        return analyze(ticker, get_provider())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, str(e))


@app.get("/api/backtest/{ticker}")
def api_backtest(ticker: str, fast: int = 50, slow: int = 200):
    try:
        return backtest(get_provider().history(ticker, 1500), fast, slow)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, str(e))


@app.post("/api/ask")
def api_ask(body: dict):
    import anthropic
    from ..agent import ask
    return {"answer": ask(anthropic.Anthropic(), [{"role": "user", "content": body.get("question", "")}])}
