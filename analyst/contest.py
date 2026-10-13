"""Reglas del Bloomberg Trading Challenge 2026 (T&C, 12-oct a 13-nov-2026)."""
CAPITAL = 1_000_000          # nocional USD
MAX_WEIGHT = 0.20            # máx 20% por posición
MIN_POSITIONS = 5            # consecuencia de 20% * 5 = 100%
LONG_ONLY = True             # sin cortos
LEVERAGE = False             # sin apalancamiento
ETFS_ALLOWED = False         # solo acciones del índice WLS <Index><GO>
INVEST_DEADLINE = "2026-10-16 23:59 America/New_York"  # 100% invertido
SCORING = "Relative P&L (ver TMSG<GO>); desempate: Absolute Return"
