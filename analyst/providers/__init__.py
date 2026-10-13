import os
from .base import DataProvider


def get_provider(name: str | None = None) -> DataProvider:
    name = (name or os.environ.get("DATA_PROVIDER", "yfinance")).lower()
    if name == "synthetic":
        from .synthetic import SyntheticProvider
        return SyntheticProvider()
    if name == "alphavantage":
        from .alphavantage import AlphaVantageProvider
        return AlphaVantageProvider()
    if name == "bloomberg":
        from .bloomberg import BloombergProvider
        return BloombergProvider()
    from .yf import YFinanceProvider
    return YFinanceProvider()
