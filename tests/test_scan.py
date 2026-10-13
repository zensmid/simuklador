import analyst.scan as scan
from analyst.providers.synthetic import SyntheticProvider


def test_scan_run(tmp_path, monkeypatch):
    prov = SyntheticProvider()
    monkeypatch.setattr(scan, "_batch", lambda tickers, days, chunk=80: {t: prov.history(t, days) for t in tickers})
    monkeypatch.setattr(scan, "get_provider", lambda: prov)
    u = tmp_path / "u.txt"; u.write_text("\n".join(list("ABCDEFGHIJKL")))
    h = tmp_path / "h.csv"; h.write_text("A,250000\nB,150000\nC,150000\nD,150000\nE,150000\nF,150000\n")
    md = scan.run(str(u), str(h), top=8, outdir=str(tmp_path / "r"))
    assert "Rebalanceo sugerido" in md and (tmp_path / "r" / "history.csv").exists()


def test_scan_with_context(tmp_path, monkeypatch):
    import analyst.brief as b
    prov = SyntheticProvider()
    monkeypatch.setattr(scan, "_batch", lambda tk, days, chunk=80: {t: prov.history(t, days) for t in tk})
    monkeypatch.setattr(scan, "get_provider", lambda: prov)
    monkeypatch.setattr(b, "get_provider", lambda: prov)
    monkeypatch.setattr(b, "snapshot", lambda: [{"name": "X", "last": 1.0, "d1": 0.01, "m1": 0.02}])
    monkeypatch.setattr(b, "earnings_info", lambda t: {"ticker": t, "next_date": "2026-10-20", "days_to": 7, "eps_est": 1.2, "history": [], "targets": {}})
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    u = tmp_path / "u.txt"; u.write_text("\n".join("ABCDEFGH"))
    scan.run(str(u), None, top=5, outdir=str(tmp_path / "r"))
    assert "2026-10-20" in (tmp_path / "r" / "events.md").read_text()
    assert (tmp_path / "r" / "brief.md").exists()
