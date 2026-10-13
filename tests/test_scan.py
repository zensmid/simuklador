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
