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
    pf = sub.add_parser("portfolio", help="Cartera del concurso (long-only, ≤20%%, 100%% invertida)")
    pf.add_argument("tickers", nargs="*"); pf.add_argument("--file", help="archivo con un ticker por línea")
    pf.add_argument("--holdings", help="CSV ticker,usd con tus posiciones actuales: recorta >20%% y reparte el resto")
    pf.add_argument("-n", type=int, default=12, help="número de posiciones (o nuevas con --holdings)"); pf.add_argument("--capital", type=float, default=1_000_000)
    sc = sub.add_parser("scan", help="Escanea todo el universo y genera reports/latest.md")
    sc.add_argument("--universe", default="universo.txt"); sc.add_argument("--holdings", default="holdings.csv"); sc.add_argument("--top", type=int, default=40)
    ev = sub.add_parser("events", help="Fechas de resultados, consenso y reacciones pasadas"); ev.add_argument("tickers", nargs="+")
    br = sub.add_parser("brief", help="Briefing: mercado + resultados + noticias + escenarios (Claude)"); br.add_argument("tickers", nargs="+")
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
    if args.cmd == "events":
        from .events import earnings_info, format_events
        print(format_events([earnings_info(t) for t in args.tickers])); return
    if args.cmd == "brief":
        from .brief import brief
        ctx, rep = brief(args.tickers); print(ctx, "\n\n", rep); return
    if args.cmd == "scan":
        from .scan import run
        print(run(args.universe, args.holdings, args.top)); return
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
    elif args.cmd == "portfolio":
        from .portfolio import build_portfolio, format_portfolio
        ts = list(args.tickers)
        if args.file: ts += [l.split("#")[0].strip() for l in open(args.file) if l.split("#")[0].strip()]
        if not ts: p.error("da tickers o --file")
        if args.holdings:
            import csv
            from .portfolio import rebalance, format_rebalance
            hold = {r[0].strip(): float(r[1]) for r in csv.reader(l for l in open(args.holdings) if l.strip() and not l.startswith("#"))}
            print(format_rebalance(rebalance(hold, ts, prov, args.capital, args.n), args.capital)); return
        print(format_portfolio(build_portfolio(ts, prov, args.capital, args.n)))
    elif args.cmd == "backtest":
        print(json.dumps(backtest(prov.history(args.ticker, 1500), args.fast, args.slow), indent=2))


if __name__ == "__main__":
    main()
