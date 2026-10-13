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
