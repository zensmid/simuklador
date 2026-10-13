from analyst.providers.synthetic import SyntheticProvider
from analyst.analysis.engine import analyze
from analyst.backtest import backtest


def test_analyze_synthetic():
    a = analyze("AAPL", SyntheticProvider())
    assert -1 <= a["score"] <= 1
    assert a["recommendation"] in {"COMPRA FUERTE", "COMPRA", "MANTENER", "VENTA", "VENTA FUERTE"}
    assert len(a["chart"]["close"]) == 180


def test_backtest():
    r = backtest(SyntheticProvider().history("MSFT", 1000))
    assert {"strategy", "buy_hold", "trades"} <= r.keys()
