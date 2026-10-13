from analyst.providers.synthetic import SyntheticProvider
from analyst.portfolio import build_portfolio, cap_weights
import pytest


def test_cap_weights():
    w = cap_weights({"A": 10, "B": 1, "C": 1, "D": 1, "E": 1, "F": 1})
    assert abs(sum(w.values()) - 1) < 1e-9 and max(w.values()) <= 0.2 + 1e-9
    with pytest.raises(ValueError):
        cap_weights({"A": 1, "B": 1, "C": 1})


def test_portfolio_rules():
    p = build_portfolio(list("ABCDEFGHIJKLMNOP"), SyntheticProvider(), n=10)
    assert p["max_weight"] <= 0.20 + 1e-9
    assert p["invested"] > 0.995 and p["cash"] >= 0
    assert all(r["shares"] >= 0 for r in p["positions"])
