import { useEffect, useState } from "react"

const MACRO_DATA = [
  // Waluty
  {
    symbol: "EUR/PLN",
    name: "Euro / Polski złoty",
    category: "Waluty",
    value: 4.27,
    change: 0.18,
    unit: "PLN",
    description: "Kurs euro względem polskiego złotego.",
  },
  {
    symbol: "USD/PLN",
    name: "Dolar amerykański / Polski złoty",
    category: "Waluty",
    value: 3.92,
    change: -0.24,
    unit: "PLN",
    description: "Kurs dolara amerykańskiego względem polskiego złotego.",
  },
  {
    symbol: "CHF/PLN",
    name: "Frank szwajcarski / Polski złoty",
    category: "Waluty",
    value: 4.55,
    change: 0.31,
    unit: "PLN",
    description: "Kurs franka szwajcarskiego względem polskiego złotego.",
  },
  {
    symbol: "GBP/PLN",
    name: "Funt brytyjski / Polski złoty",
    category: "Waluty",
    value: 5.02,
    change: -0.12,
    unit: "PLN",
    description: "Kurs funta brytyjskiego względem polskiego złotego.",
  },
  {
    symbol: "EUR/USD",
    name: "Euro / Dolar amerykański",
    category: "Waluty",
    value: 1.09,
    change: 0.07,
    unit: "USD",
    description: "Relacja euro do dolara amerykańskiego.",
  },

  // Inflacja
  {
    symbol: "CPI PL",
    name: "Inflacja CPI Polska",
    category: "Inflacja",
    value: 4.2,
    change: -0.3,
    unit: "%",
    description: "Wskaźnik wzrostu cen towarów i usług konsumpcyjnych w Polsce.",
  },
  {
    symbol: "CPI USA",
    name: "Inflacja CPI USA",
    category: "Inflacja",
    value: 3.1,
    change: 0.2,
    unit: "%",
    description: "Wskaźnik inflacji konsumenckiej w Stanach Zjednoczonych.",
  },
  {
    symbol: "CPI EU",
    name: "Inflacja CPI Strefa Euro",
    category: "Inflacja",
    value: 2.6,
    change: -0.1,
    unit: "%",
    description: "Inflacja konsumencka w krajach strefy euro.",
  },

  // Stopy procentowe
  {
    symbol: "NBP RATE",
    name: "Stopa referencyjna NBP",
    category: "Stopy procentowe",
    value: 5.75,
    change: 0,
    unit: "%",
    description: "Główna stopa procentowa Narodowego Banku Polskiego.",
  },
  {
    symbol: "FED RATE",
    name: "Stopa procentowa FED",
    category: "Stopy procentowe",
    value: 5.25,
    change: 0,
    unit: "%",
    description: "Przedział głównej stopy procentowej Rezerwy Federalnej USA.",
  },
  {
    symbol: "ECB RATE",
    name: "Stopa procentowa EBC",
    category: "Stopy procentowe",
    value: 4.5,
    change: -0.25,
    unit: "%",
    description: "Główna stopa procentowa Europejskiego Banku Centralnego.",
  },

  // PKB
  {
    symbol: "GDP PL",
    name: "PKB Polska",
    category: "PKB",
    value: 2.9,
    change: 0.4,
    unit: "%",
    description: "Tempo wzrostu produktu krajowego brutto Polski.",
  },
  {
    symbol: "GDP USA",
    name: "PKB USA",
    category: "PKB",
    value: 2.5,
    change: -0.1,
    unit: "%",
    description: "Tempo wzrostu produktu krajowego brutto Stanów Zjednoczonych.",
  },
  {
    symbol: "GDP EU",
    name: "PKB Strefa Euro",
    category: "PKB",
    value: 0.9,
    change: 0.2,
    unit: "%",
    description: "Tempo wzrostu gospodarki strefy euro.",
  },

  // Surowce
  {
    symbol: "OIL",
    name: "Ropa Brent",
    category: "Surowce",
    value: 82.4,
    change: 1.36,
    unit: "USD",
    description: "Cena ropy Brent, istotna dla inflacji i kosztów energii.",
  },
  {
    symbol: "GOLD",
    name: "Złoto",
    category: "Surowce",
    value: 2385,
    change: -0.44,
    unit: "USD",
    description: "Cena złota jako aktywa defensywnego.",
  },
  {
    symbol: "GAS",
    name: "Gaz ziemny",
    category: "Surowce",
    value: 2.31,
    change: 2.18,
    unit: "USD",
    description: "Cena gazu ziemnego wpływająca na koszty energii.",
  },
]

function generateHistory(baseValue, change) {
  const points = []
  const direction = change >= 0 ? 1 : -1

  for (let index = 0; index < 48; index++) {
    const wave = Math.sin(index / 5) * baseValue * 0.015
    const trend = direction * index * baseValue * 0.0007
    const noise = Math.cos(index / 3) * baseValue * 0.005

    points.push({
      time: `${index + 1}`,
      value: Math.max(baseValue + wave + trend + noise, 0.01),
    })
  }

  return points
}

function Macro() {
  const [items, setItems] = useState([])
  const [selectedItem, setSelectedItem] = useState(null)
  const [chartRange, setChartRange] = useState("1M")
  const [hoveredPoint, setHoveredPoint] = useState(null)

  useEffect(() => {
    const preparedItems = MACRO_DATA.map((item) => ({
      ...item,
      history: generateHistory(item.value, item.change),
    }))

    setItems(preparedItems)
    setSelectedItem(preparedItems[0])
  }, [])

  useEffect(() => {
    setHoveredPoint(null)
  }, [selectedItem, chartRange])

  const formatValue = (value, unit) => {
    if (value === null || value === undefined) return "-"

    if (unit === "%") {
      return `${value.toFixed(2)}%`
    }

    if (unit === "PLN") {
      return new Intl.NumberFormat("pl-PL", {
        style: "currency",
        currency: "PLN",
        maximumFractionDigits: 4,
      }).format(value)
    }

    if (unit === "USD") {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: value > 100 ? 2 : 4,
      }).format(value)
    }

    return value.toFixed(2)
  }

  const formatPercent = (value) => {
    if (value === null || value === undefined) return "-"

    const prefix = value > 0 ? "+" : ""
    return `${prefix}${value.toFixed(2)}%`
  }

  const getChangeClass = (value) => {
    if (value > 0) return "text-emerald-400"
    if (value < 0) return "text-red-400"
    return "text-slate-400"
  }

  const ChangeValue = ({ value }) => {
    const isPositive = value > 0
    const isNegative = value < 0

    return (
      <span className={`inline-flex items-center justify-end gap-1 ${getChangeClass(value)}`}>
        {isPositive && <span>▲</span>}
        {isNegative && <span>▼</span>}
        {!isPositive && !isNegative && <span>●</span>}
        {formatPercent(value)}
      </span>
    )
  }

  const getVisibleHistory = () => {
    const history = selectedItem?.history || []

    if (chartRange === "1D") return history.slice(-12)
    if (chartRange === "1W") return history.slice(-24)
    return history
  }

  const historyPoints = getVisibleHistory()

  const minValue =
    historyPoints.length > 0
      ? Math.min(...historyPoints.map((point) => point.value))
      : 0

  const maxValue =
    historyPoints.length > 0
      ? Math.max(...historyPoints.map((point) => point.value))
      : 0

  const chartPoints = historyPoints.map((point, index) => {
    const x = (index / Math.max(historyPoints.length - 1, 1)) * 100
    const y =
      100 -
      ((point.value - minValue) / Math.max(maxValue - minValue, 1)) * 100

    return {
      x,
      y,
      value: point.value,
      timeLabel: point.time,
    }
  })

  const chartLine = chartPoints.map((point) => `${point.x},${point.y}`).join(" ")
  const chartFill = chartPoints.length > 0 ? `0,100 ${chartLine} 100,100` : ""

  const handleChartMouseMove = (event) => {
    if (chartPoints.length === 0) return

    const rect = event.currentTarget.getBoundingClientRect()
    const mouseX = ((event.clientX - rect.left) / rect.width) * 100

    const closestPoint = chartPoints.reduce((closest, point) => {
      return Math.abs(point.x - mouseX) < Math.abs(closest.x - mouseX)
        ? point
        : closest
    }, chartPoints[0])

    setHoveredPoint(closestPoint)
  }

  return (
    <main className="px-8 py-8">
      <section className="relative overflow-hidden rounded-3xl border border-violet-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-violet-500/10 blur-3xl"></div>

        <div className="relative">
          <p className="mb-4 inline-flex rounded-full border border-violet-500/40 bg-violet-500/10 px-4 py-1 text-sm text-violet-400">
            Macroeconomic data
          </p>

          <h2 className="text-4xl font-bold">
            Makro
          </h2>

          <p className="mt-4 max-w-4xl text-slate-400">
            Zakładka Makro prezentuje najważniejsze dane makroekonomiczne:
            kursy walut, inflację, stopy procentowe, PKB oraz wybrane surowce.
            Dane są obecnie przykładowe, ale struktura została przygotowana tak,
            aby później można było łatwo podmienić je na dane przygotowane przez Sebastiana.
          </p>

          <div className="mt-6 grid max-w-5xl grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-violet-400">Waluty</p>
              <p className="mt-2 text-sm text-slate-400">
                EUR/PLN, USD/PLN, CHF/PLN, GBP/PLN oraz EUR/USD.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-violet-400">Inflacja i stopy</p>
              <p className="mt-2 text-sm text-slate-400">
                CPI, stopa NBP, stopa FED oraz stopa EBC.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-violet-400">PKB i surowce</p>
              <p className="mt-2 text-sm text-slate-400">
                Dane gospodarcze oraz ceny ropy, złota i gazu.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8">
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.45fr_1fr]">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h3 className="text-2xl font-bold">
                  Dane makroekonomiczne
                </h3>

                <p className="mt-1 text-sm text-slate-400">
                  Waluty, inflacja, stopy procentowe, PKB i surowce w jednej tabeli.
                </p>
              </div>

              <span className="rounded-full bg-violet-500/10 px-4 py-1 text-sm text-violet-400">
                Mock macro data
              </span>
            </div>

            <div className="overflow-x-auto rounded-2xl border border-slate-800">
              <table className="w-full min-w-[950px] border-collapse text-sm">
                <thead className="bg-slate-950 text-slate-400">
                  <tr>
                    <th className="px-4 py-4 text-left">#</th>
                    <th className="px-4 py-4 text-left">Wskaźnik</th>
                    <th className="px-4 py-4 text-left">Kategoria</th>
                    <th className="px-4 py-4 text-right">Wartość</th>
                    <th className="px-4 py-4 text-right">Zmiana</th>
                    <th className="px-4 py-4 text-left">Opis</th>
                  </tr>
                </thead>

                <tbody>
                  {items.map((item, index) => {
                    const isSelected = selectedItem?.symbol === item.symbol

                    return (
                      <tr
                        key={item.symbol}
                        onClick={() => setSelectedItem(item)}
                        className={`cursor-pointer border-t border-slate-800 transition hover:bg-slate-800/70 ${
                          isSelected ? "bg-violet-500/10" : "bg-slate-950/40"
                        }`}
                      >
                        <td className="px-4 py-4 text-slate-400">
                          {index + 1}
                        </td>

                        <td className="px-4 py-4">
                          <div>
                            <p className="font-semibold text-white">
                              {item.name}
                            </p>

                            <p className="text-xs uppercase text-slate-500">
                              {item.symbol}
                            </p>
                          </div>
                        </td>

                        <td className="px-4 py-4">
                          <span className="rounded-full bg-violet-500/10 px-3 py-1 text-xs text-violet-300">
                            {item.category}
                          </span>
                        </td>

                        <td className="px-4 py-4 text-right font-medium text-white">
                          {formatValue(item.value, item.unit)}
                        </td>

                        <td className="px-4 py-4 text-right">
                          <ChangeValue value={item.change} />
                        </td>

                        <td className="max-w-[320px] px-4 py-4 text-slate-400">
                          {item.description}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="sticky top-24 max-h-[calc(100vh-7rem)] self-start overflow-y-auto rounded-3xl border border-violet-500/30 bg-slate-900/90 p-6">
            {selectedItem && (
              <>
                <div>
                  <p className="text-sm text-violet-400">
                    Wybrany wskaźnik
                  </p>

                  <h3 className="mt-1 text-2xl font-bold">
                    {selectedItem.name}
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    {selectedItem.symbol} · {selectedItem.category}
                  </p>
                </div>

                <p className="mt-5 rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm leading-6 text-slate-400">
                  {selectedItem.description}
                </p>

                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-500">Wartość</p>
                    <p className="mt-2 text-xl font-bold text-white">
                      {formatValue(selectedItem.value, selectedItem.unit)}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-500">Zmiana</p>
                    <p className="mt-2 text-xl font-bold">
                      <ChangeValue value={selectedItem.change} />
                    </p>
                  </div>
                </div>

                <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                  <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <h4 className="font-semibold">
                        Wykres wskaźnika
                      </h4>

                      <p className="text-sm text-slate-500">
                        Przykładowy wykres pokazujący zmianę wybranego wskaźnika.
                      </p>
                    </div>

                    <div className="flex rounded-full border border-slate-800 bg-slate-900 p-1">
                      {["1D", "1W", "1M"].map((range) => (
                        <button
                          key={range}
                          onClick={() => setChartRange(range)}
                          className={`rounded-full px-4 py-1 text-sm transition ${
                            chartRange === range
                              ? "bg-violet-400 text-slate-950"
                              : "text-slate-400 hover:text-violet-400"
                          }`}
                        >
                          {range}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="mb-4 grid grid-cols-3 gap-3">
                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                      <p className="text-xs text-slate-500">Minimum</p>
                      <p className="mt-1 font-semibold text-white">
                        {formatValue(minValue, selectedItem.unit)}
                      </p>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                      <p className="text-xs text-slate-500">Aktualnie</p>
                      <p className="mt-1 font-semibold text-white">
                        {formatValue(selectedItem.value, selectedItem.unit)}
                      </p>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                      <p className="text-xs text-slate-500">Maksimum</p>
                      <p className="mt-1 font-semibold text-white">
                        {formatValue(maxValue, selectedItem.unit)}
                      </p>
                    </div>
                  </div>

                  <div
                    className="relative h-[420px] rounded-xl border border-violet-500/20 bg-slate-950 p-4 pr-14"
                    onMouseMove={handleChartMouseMove}
                    onMouseLeave={() => setHoveredPoint(null)}
                  >
                    {historyPoints.length > 0 ? (
                      <>
                        <svg
                          viewBox="0 0 100 100"
                          preserveAspectRatio="none"
                          className="h-full w-full"
                        >
                          <defs>
                            <linearGradient id="macroChartFill" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stopColor="currentColor" stopOpacity="0.28" />
                              <stop offset="100%" stopColor="currentColor" stopOpacity="0.02" />
                            </linearGradient>
                          </defs>

                          {[20, 40, 60, 80].map((line) => (
                            <line
                              key={`h-${line}`}
                              x1="0"
                              y1={line}
                              x2="100"
                              y2={line}
                              stroke="currentColor"
                              strokeWidth="0.25"
                              className="text-slate-700"
                            />
                          ))}

                          {[20, 40, 60, 80].map((line) => (
                            <line
                              key={`v-${line}`}
                              x1={line}
                              y1="0"
                              x2={line}
                              y2="100"
                              stroke="currentColor"
                              strokeWidth="0.15"
                              className="text-slate-800"
                            />
                          ))}

                          <polygon
                            points={chartFill}
                            fill="url(#macroChartFill)"
                            className={
                              selectedItem.change >= 0
                                ? "text-emerald-400"
                                : "text-red-400"
                            }
                          />

                          <polyline
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.6"
                            points={chartLine}
                            className={
                              selectedItem.change >= 0
                                ? "text-emerald-400"
                                : "text-red-400"
                            }
                          />

                          {hoveredPoint && (
                            <>
                              <line
                                x1={hoveredPoint.x}
                                y1="0"
                                x2={hoveredPoint.x}
                                y2="100"
                                stroke="currentColor"
                                strokeWidth="0.35"
                                strokeDasharray="2 2"
                                className="text-violet-300"
                              />

                              <circle
                                cx={hoveredPoint.x}
                                cy={hoveredPoint.y}
                                r="1.7"
                                fill="currentColor"
                                className="text-violet-300"
                              />
                            </>
                          )}
                        </svg>

                        <div className="absolute right-3 top-3 flex h-[calc(100%-24px)] flex-col justify-between text-xs text-slate-500">
                          <span>{formatValue(maxValue, selectedItem.unit)}</span>
                          <span>{formatValue((maxValue + minValue) / 2, selectedItem.unit)}</span>
                          <span>{formatValue(minValue, selectedItem.unit)}</span>
                        </div>

                        {hoveredPoint && (
                          <div
                            className="pointer-events-none absolute z-10 rounded-xl border border-violet-500/30 bg-slate-900 px-4 py-3 text-xs shadow-xl shadow-violet-950/40"
                            style={{
                              left: `${hoveredPoint.x}%`,
                              top: `${hoveredPoint.y}%`,
                              transform: "translate(-50%, -125%)",
                            }}
                          >
                            <p className="font-semibold text-violet-400">
                              {formatValue(hoveredPoint.value, selectedItem.unit)}
                            </p>

                            <p className="mt-1 text-slate-400">
                              Punkt: {hoveredPoint.timeLabel}
                            </p>

                            <p className="mt-1 text-slate-500">
                              Zakres: {chartRange}
                            </p>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="flex h-full items-center justify-center text-slate-500">
                        Brak danych wykresu
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </section>
    </main>
  )
}

export default Macro