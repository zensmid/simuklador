from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd


class DataProvider(ABC):
    """Interfaz común. Para cambiar a Bloomberg solo se cambia DATA_PROVIDER."""

    @abstractmethod
    def history(self, ticker: str, days: int = 365) -> pd.DataFrame:
        """DataFrame indexado por fecha con columnas open, high, low, close, volume."""

    @abstractmethod
    def fundamentals(self, ticker: str) -> dict:
        """Claves opcionales: pe, forward_pe, peg, roe, profit_margin, debt_to_equity,
        revenue_growth, dividend_yield, market_cap, name, sector."""

    @abstractmethod
    def news(self, ticker: str, limit: int = 15) -> list[dict]:
        """Lista de {title, publisher, link, published}."""
