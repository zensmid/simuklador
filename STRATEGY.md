# Estrategia para ganar — Bloomberg Trading Challenge 2026 (actualizado 14-oct)

> No hay forma de garantizar un primer lugar. Este documento fija **cómo decidimos** para meter posiciones bien pensadas, no sacarlas por nervios, y
> apostar donde de verdad hay ventaja. Herramienta educativa; no es asesoría financiera.

## 1. Qué se gana y qué implica
- Gana **un solo equipo**: el mayor **Relative P&L** frente al WLS Index al 13-nov (desempate: retorno absoluto).
- Premio de ganador único ⇒ el objetivo es **maximizar la probabilidad de quedar #1**, no minimizar pérdidas. Eso pide **riesgo activo real**,
  pero solo en apuestas con ventaja; apostar fuerte sin ventaja solo sube la varianza.
- Reglas: solo largos, ≤20% por posición (contra US$1M), sin ETFs ni apalancamiento, 100% invertidos antes del **16-oct 23:59 ET**.
- Estado (14-oct 12:56): P&L -16.7k, relativo -6.9k. Simulación: ≈42% de recuperar el relativo; σ mensual de la cartera ≈ 8-9%.

## 2. Diagnóstico de la cartera actual
1. **Dos tercios es una sola apuesta (ciclo de materias primas/volatilidad):** DVN 20.4% + Zijin 19.9% + MRX 16.5% (bróker de commodities) +
   1138 HK 8.3% (por su ticker, tanqueros) + PetroChina 1.7% ≈ **67%**. Si el petróleo/metales caen, caen casi todas a la vez.
2. **Tecnología 24%** (AAPL 10, ANET 9, ASML 4.8) con tasas en máximos y Fed restrictiva: sensible a tasas y a las cifras de CPI/FOMC.
3. **Posiciones demasiado chicas para importar:** cuatro órdenes de ~US$17k (1.7%). Una subida del 10% mueve la cartera solo 0.17%. En un concurso de rank
   no aportan: o se agrandan hasta ≥3-4% o se descartan.
4. **DVN en 20.4% incumple el tope** (por movimiento de precio). Recortar a ≤19.5%.
5. Las órdenes de Asia siguen en **"Apertura" (pendientes)**: aún se pueden modificar o cancelar antes de que se ejecuten.

## 3. Régimen de mercado (datos al 14-oct; verificar en la Terminal)
- Hoy: S&P -1.1%, Nasdaq -1.7%, VIX 16.5 (+8%), Kospi -5.5%, Taiwán -2.0%, EEM -1.9%; 10Y 5.23%; WTI 95.9; oro 4,102 (-1.8%).
- Según fuentes (con conflictos, verificar): Fed restrictiva tras un alza en septiembre; **CPI de septiembre sale hoy 14-oct 8:30 ET** (previo 3.4%);
  **FOMC 27-28 oct** (decisión el 28; confirmar que exista reunión).
- Implicación: favorece calidad, flujo de caja y energía/commodities sobre crecimiento de larga duración; castiga apalancamiento y valuaciones altas.
  El riesgo: que justo ese sesgo ya esté en nuestra cartera (punto 2.1).

## 4. Fuentes de ventaja realistas (y cómo las verificamos)
| Fuente | Por qué podría funcionar | Cómo la validamos |
|---|---|---|
| Momentum / tendencia | Documentado a 3-12 meses, débil a 1 mes | `analyst study` (backtest de factores en el universo; corre domingos) |
| Reacción a resultados (Q3) | Gran dispersión de retornos en la ventana del concurso | Historial de reacciones por acción + estimaciones de analistas |
| Evitar perdedores obvios | Reducir lo que más puede caer bajo tasas altas | Filtros del checklist (§5) |
Si el estudio muestra que un factor **no** predice (|t|<2), se baja su peso o se elimina del puntaje. Sin ventaja demostrada, no se concentra más.

## 5. Checklist para meter una posición (todas deben cumplirse)
1. Está en WLS y no es ETF; liquidez suficiente (volumen diario × precio ≥ 10× el monto).
2. Puntaje del escaneo ≥ 0.5 **y** el factor que lo sostiene pasó el estudio.
3. Tiene un **catalizador con fecha dentro de la ventana** (resultados antes del 13-nov) y una razón escrita (1 línea) para esperar sorpresa positiva.
4. No duplica una apuesta ya existente (petróleo, metales, tecnología de EE. UU., China).
5. Volatilidad anual > 40% ⇒ peso máximo 5%. Tamaño mínimo 3%.
6. Tiene **nivel de invalidación** (cierre bajo 2×ATR o -12%) y **objetivo** definidos antes de comprar.

## 6. Reglas anti-vaivén (pre-comprometidas)
- Una posición solo se vende si: (a) cierra bajo su nivel de invalidación, (b) la tesis se rompe con hechos (reporte malo + guía recortada), (c) supera el 20%,
  (d) cumple su objetivo y su relación riesgo/recompensa ya no compensa.
- Fechas de revisión (no antes): **16-oct** (cartera completa), **30-oct** (tras MSFT/GOOGL/META/AMZN, XOM/CVX y FOMC), **6-nov** (tras AAPL, ANET, DVN, MRX),
  **11-nov** (decisión final de riesgo).
- Máximo 2 cambios por semana fuera de esas fechas. Todo cambio se registra con su razón en `holdings.csv`/commit.
- **Regla de cierre (semana del 9-nov):** si vamos primeros o segundos, reducir varianza hacia el índice; si estamos lejos, concentrar en las mejores 3-4 ideas.
  Requiere ver la tabla de clasificación (portal Bloomberg for Education).

## 7. Calendario de catalizadores
| Fecha | Evento |
|---|---|
| 14-oct | CPI EE. UU. (8:30 ET); ASML reportó (ventas €11.7 mil M, sobre su guía) |
| 15-oct | TSM (resultados) |
| 16-oct | Plazo: 100% invertidos (23:59 ET) |
| 23-oct | Zijin 2899 HK (fecha según escaneo, sin confirmar) |
| 27-28 oct | FOMC (verificar) |
| 28-29 oct | MSFT, GOOGL, META, AMZN, INTC |
| 29-oct | PetroChina 857 HK y Japan Tobacco 2914 JP (según escaneo) |
| 30-oct | XOM, CVX (lectura para DVN) |
| 2-nov | AAPL |
| 3-nov | ANET (después del cierre, confirmado por la empresa) |
| 5-nov | DVN y MRX (fechas estimadas) |
| 13-nov | Cierre del concurso 17:00 ET |

## 8. Acciones inmediatas
1. Recortar DVN a ≤19.5% (≈US$9.5k).
2. Reemplazar las 4 órdenes de ~US$17k por **menos órdenes, más grandes** (≥3% cada una) y **fuera de petróleo/commodities** para bajar la concentración del punto 2.1.
3. Decidir con el Capitán si AAPL (10%, resultados 2-nov) es una apuesta con tesis o un relleno.
4. Correr el workflow **study** (Actions) y actualizar esta estrategia con sus resultados.
5. Abrir la tabla de clasificación y anotar nuestra posición.
