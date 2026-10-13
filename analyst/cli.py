from __future__ import annotations
import argparse, json, os
from .providers import get_provider
from .analysis.engine import analyze
from .report import to_markdown
from .backtest import backtest


def main(argv=None):
    p = argparse.ArgumentParser(prog="analyst", description="Analista de trading")
    p.add_argument("--provider", help="yfinance|alphavantage|bloomberg|synthetic")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="Analiza uno o más tickers"); a.add_argument("tickers", nargs="+"); a.add_argument("--json", action="store_true")
    r = sub.add_parser("rank", help="Rankea tickers por score"); r.add_argument("tickers", nargs="+")
    b = sub.add_parser("backtest", help="Backtest cruce de medias"); b.add_argument("ticker"); b.add_argument("--fast", type=int, default=50); b.add_argument("--slow", type=int, default=200)
    g = sub.add_parser("agent", help="Agente conversacional con Claude"); g.add_argument("question", nargs="?")
    w = sub.add_parser("web", help="Dashboard web"); w.add_argument("--port", type=int, default=8000)
    args = p.parse_args(argv)
    if args.provider: os.environ["DATA_PROVIDER"] = args.provider

    if args.cmd == "web":
        import uvicorn
        uvicorn.run("analyst.web.app:app", host="0.0.0.0", port=args.port); return
    if args.cmd == "agent":
        from .agent import chat
        chat(args.question); return
    prov = get_provider()
    if args.cmd == "analyze":
        for t in args.tickers:
            res = analyze(t, prov)
            print(json.dumps(res, indent=2, default=str) if args.json else to_markdown(res), "\n")
    elif args.cmd == "rank":
        rows = []
        for t in args.tickers:
            try: res = analyze(t, prov); rows.append((res["score"], t.upper(), res["recommendation"]))
            except Exception as e: print(f"{t}: error {e}")
        for s, t, rec in sorted(rows, reverse=True): print(f"{t:8} {s:+.2f}  {rec}")
    elif args.cmd == "backtest":
        print(json.dumps(backtest(prov.history(args.ticker, 1500), args.fast, args.slow), indent=2))


if __name__ == "__main__":
    main()
