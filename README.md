# Analista de Trading (concurso Bloomberg)

Combina análisis **técnico** (45%), **fundamental** (35%) y **sentimiento de noticias** (20%) en un score de -1 a +1 y una recomendación. Tres interfaces sobre el mismo núcleo:

```bash
pip install -e .
cp .env.example .env            # y exporta las variables
analyst analyze AAPL MSFT       # CLI
analyst rank AAPL MSFT NVDA AMD
analyst backtest AAPL
analyst web                     # dashboard en http://localhost:8000
analyst agent "¿Compro NVDA o AMD?"   # agente Claude (ANTHROPIC_API_KEY)
```

## Proveedores de datos (`DATA_PROVIDER` o `--provider`)
| nombre | notas |
|---|---|
| `yfinance` | por defecto, gratis |
| `alphavantage` | requiere `ALPHAVANTAGE_API_KEY` |
| `bloomberg` | `pip install blpapi`, terminal/API de la escuela activa (`BLP_HOST`, `BLP_PORT`) |
| `synthetic` | datos falsos deterministas, sin red (pruebas) |

Para añadir otro proveedor, implementa `analyst/providers/base.py`.

> Herramienta educativa; no es asesoría financiera. Los umbrales de `analysis/` son un punto de partida a calibrar con backtests.

## Bloomberg Trading Challenge 2026
Reglas codificadas en `analyst/contest.py`: US$1M nocional, **solo largos**, sin apalancamiento, **máx 20% por posición** (≥5 posiciones), solo acciones del índice `WLS <Index><GO>` (**sin ETFs**), 100% invertido antes del **16-oct-2026 23:59 ET**, ganador por **Relative P&L** (`TMSG<GO>`). Las operaciones las envía el Capitán manualmente en la Terminal.

```bash
analyst portfolio --file universo.txt -n 12     # propone acciones enteras y pesos
```
`universo.txt`: un ticker por línea (acciones de WLS; exporta la lista desde la Terminal). Con `--provider bloomberg` o yfinance (tickers de EE. UU.; para otros mercados usa el formato Bloomberg, p. ej. `7203 JT`).

## Escaneo 24/7
`analyst scan` filtra todo `universo.txt` (técnico, en lote), analiza a fondo el top 40 y escribe `reports/latest.md` + `reports/history.csv`, con rebalanceo sugerido sobre `holdings.csv`. `.github/workflows/scan.yml` lo corre cada 2 h en GitHub Actions y commitea el reporte (el cron solo corre desde la rama por defecto).
`universo.txt` salió de OCR del PDF de EQS (~88% de filas): complétalo/verifícalo contra la Terminal.
