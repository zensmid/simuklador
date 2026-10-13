from __future__ import annotations
import os
import pandas as pd
from .base import DataProvider


class BloombergProvider(DataProvider):
    """Adaptador blpapi (Desktop API / B-PIPE). Requiere `pip install blpapi` y terminal activa.
    Tickers: se convierte 'AAPL' -> 'AAPL US Equity' si no trae sufijo."""

    def __init__(self):
        import blpapi  # noqa
        self.blpapi = blpapi
        o = blpapi.SessionOptions()
        o.setServerHost(os.environ.get("BLP_HOST", "localhost"))
        o.setServerPort(int(os.environ.get("BLP_PORT", "8194")))
        self.session = blpapi.Session(o)
        if not self.session.start() or not self.session.openService("//blp/refdata"):
            raise RuntimeError("No se pudo conectar a Bloomberg (¿terminal abierta?)")
        self.svc = self.session.getService("//blp/refdata")

    @staticmethod
    def _sec(t):
        return t if " " in t else f"{t} US Equity"

    def _send(self, req):
        self.session.sendRequest(req)
        out = []
        while True:
            ev = self.session.nextEvent(5000)
            out += list(ev)
            if ev.eventType() == self.blpapi.Event.RESPONSE:
                return out

    def history(self, ticker, days=365):
        req = self.svc.createRequest("HistoricalDataRequest")
        req.getElement("securities").appendValue(self._sec(ticker))
        for f in ["PX_OPEN", "PX_HIGH", "PX_LOW", "PX_LAST", "PX_VOLUME"]:
            req.getElement("fields").appendValue(f)
        end = pd.Timestamp.today()
        req.set("startDate", (end - pd.Timedelta(days=int(days * 1.5))).strftime("%Y%m%d"))
        req.set("endDate", end.strftime("%Y%m%d"))
        rows = []
        for msg in self._send(req):
            if not msg.hasElement("securityData"):
                continue
            for p in msg.getElement("securityData").getElement("fieldData").values():
                g = lambda k: p.getElementAsFloat(k) if p.hasElement(k) else None
                rows.append((p.getElementAsDatetime("date"), g("PX_OPEN"), g("PX_HIGH"), g("PX_LOW"), g("PX_LAST"), g("PX_VOLUME")))
        if not rows:
            raise ValueError(f"Sin datos Bloomberg para {ticker}")
        df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])
        df["date"] = pd.to_datetime(df["date"])
        return df.set_index("date").tail(days)

    def fundamentals(self, ticker):
        fields = {"NAME": "name", "GICS_SECTOR_NAME": "sector", "PE_RATIO": "pe", "BEST_PE_RATIO": "forward_pe",
                  "PEG_RATIO": "peg", "RETURN_COM_EQY": "roe", "PROF_MARGIN": "profit_margin",
                  "TOT_DEBT_TO_TOT_EQY": "debt_to_equity", "SALES_GROWTH": "revenue_growth",
                  "EQY_DVD_YLD_IND": "dividend_yield", "CUR_MKT_CAP": "market_cap"}
        req = self.svc.createRequest("ReferenceDataRequest")
        req.getElement("securities").appendValue(self._sec(ticker))
        for f in fields:
            req.getElement("fields").appendValue(f)
        out = {}
        for msg in self._send(req):
            if not msg.hasElement("securityData"):
                continue
            for sd in msg.getElement("securityData").values():
                fd = sd.getElement("fieldData")
                for bf, k in fields.items():
                    if fd.hasElement(bf):
                        v = fd.getElementValue(bf)
                        # Bloomberg da porcentajes (15.2); se normalizan a fracción
                        if k in ("roe", "profit_margin", "revenue_growth", "dividend_yield") and isinstance(v, float):
                            v /= 100
                        out[k] = v
        return out

    def news(self, ticker, limit=15):
        return []  # Las noticias requieren //blp/mktdata o NEWS<GO>; ampliar según licencia.
