import { useEffect, useState } from "react"
import useFavorites from "../hooks/useFavorites"

// Dane makroekonomiczne pochodzą z backendu Sebastiana (Delta Lake / źródła API).
// Nie używamy lokalnych, fikcyjnych wartości ani generowanych wykresów.
const MARKET_API_URL = (
  import.meta.env.VITE_MARKET_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "")

function normalizeMacroItem(item) {
  const history = Array.isArray(item.history)
    ? item.history
        .filter((point) => point && point.value !== null && point.value !== undefined && Number.isFinite(Number(point.value)))
        .map((point) => ({
          time: point.time ?? "",
          value: Number(point.value),
        }))
    : []

  return {
    ...item,
    value: item.value === null || item.value === undefined ? null : Number(item.value),
    change: item.change === null || item.change === undefined ? null : Number(item.change),
    history,
  }
}

function Macro({ user, isLoggedIn, onLoginRequired }) {
  const [items, setItems] = useState([])
  const [selectedItem, setSelectedItem] = useState(null)
  const {
    isFavorite,
    toggleFavorite,
    error: favoritesError,
  } = useFavorites("macro", user?.id)

  const [chartRange, setChartRange] = useState("1M")
  const [hoveredPoint, setHoveredPoint] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [fetchError, setFetchError] = useState("")

  useEffect(() => {
    const controller = new AbortController()
    let active = true

    async function loadMacro() {
      try {
        const response = await fetch(`${MARKET_API_URL}/api/macro`, {
          signal: controller.signal,
        })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)

        const result = await response.json()
        if (!Array.isArray(result)) {
          throw new Error("Nieoczekiwany format odpowiedzi API")
        }

        const fetchedItems = result.map(normalizeMacroItem)
        if (!active) return

        setItems(fetchedItems)
        setSelectedItem((previous) => {
          const symbolFromUrl = new URLSearchParams(window.location.search).get("symbol")
          const symbol = previous?.symbol || symbolFromUrl
          return fetchedItems.find((item) => item.symbol === symbol) || fetchedItems[0] || null
        })
        setFetchError("")
      } catch (error) {
        if (!active || error.name === "AbortError") return
        console.error("Błąd pobierania danych makro z backendu:", error)
        setFetchError("Nie udało się pobrać danych makroekonomicznych z backendu Sebastiana.")
      } finally {
        if (active) setIsLoading(false)
      }
    }

    loadMacro()
    const interval = setInterval(loadMacro, 120_000)

    return () => {
      active = false
      clearInterval(interval)
      controller.abort()
    }
  }, [])

  useEffect(() => {
    setHoveredPoint(null)
  }, [selectedItem, chartRange])

  async function handleAddToFavorites(item) {
    if (!isLoggedIn || user?.id === null || user?.id === undefined) {
      onLoginRequired()
      return
    }

    try {
      await toggleFavorite({
        symbol: item.symbol,
        name: item.name,
        category: item.category,
        value: item.value,
        unit: item.unit,
      })
    } catch (error) {
      console.error("Nie udało się zmienić ulubionych Makro:", error)
    }
  }

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

    if (chartRange === "1D") return history.slice(-24)
    if (chartRange === "1W") return history.slice(-168)

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
      {isLoading && (
        <div className="mb-6 rounded-xl border border-violet-500/30 bg-violet-500/10 px-4 py-3 text-sm text-violet-200">
          Pobieranie rzeczywistych danych makroekonomicznych...
        </div>
      )}
      {fetchError && (
        <div role="alert" className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {fetchError} {items.length > 0 ? "Wyświetlane są ostatnio pobrane dane." : ""}
        </div>
      )}
      {!isLoading && !fetchError && items.length === 0 && (
        <div className="mb-6 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-300">
          Backend nie zwrócił żadnych wskaźników makroekonomicznych.
        </div>
      )}
      {favoritesError && (
        <div role="alert" className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {favoritesError}
        </div>
      )}
      <section className="relative overflow-hidden rounded-3xl border border-violet-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-violet-500/10 blur-3xl"></div>

        <div className="relative">
          <p className="mb-4 inline-flex rounded-full border border-violet-500/40 bg-violet-500/10 px-4 py-1 text-sm text-violet-400">
            Macroeconomic data
          </p>

          <h2 className="text-4xl font-bold">
            Makro
          </h2>

          <p className="mt-4 max-w-4xl leading-7 text-slate-300">
            Zakładka Makro prezentuje najważniejsze dane makroekonomiczne,
            takie jak kursy walut, inflacja, stopy procentowe, PKB oraz
            wybrane surowce. Dane są przedstawione w formie tabeli, kart
            informacyjnych oraz wykresu wybranego wskaźnika.
          </p>

          <div className="mt-6 grid max-w-5xl grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-violet-400">
                Waluty
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Kursy najważniejszych par walutowych, takich jak EUR/PLN,
                USD/PLN, CHF/PLN, GBP/PLN oraz EUR/USD.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-violet-400">
                Inflacja i stopy
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Wskaźniki pokazujące poziom inflacji oraz decyzje banków
                centralnych dotyczące kosztu pieniądza.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-violet-400">
                PKB i surowce
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Dane gospodarcze oraz ceny wybranych surowców, takich jak ropa,
                złoto i gaz.
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
                Macro data
              </span>
            </div>

            <div className="overflow-x-auto rounded-2xl border border-slate-800">
              <table className="w-full min-w-[1050px] border-collapse text-sm">
                <thead className="bg-slate-950 text-slate-400">
                  <tr>
                    <th className="px-4 py-4 text-left">☆</th>
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
                        <td className="px-4 py-4">
                          <button
                            onClick={(event) => {
                              event.stopPropagation()
                              handleAddToFavorites(item)
                            }}
                            className={`text-xl transition ${
                              isFavorite(item.symbol)
                                ? "text-yellow-400"
                                : "text-slate-500 hover:text-yellow-400"
                            }`}
                            title={isFavorite(item.symbol) ? "Usuń z ulubionych" : "Dodaj do ulubionych"}
                          >
                            {isFavorite(item.symbol) ? "★" : "☆"}
                          </button>
                        </td>

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
                <div className="flex items-start justify-between gap-4">
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

                  <button
                    onClick={() => handleAddToFavorites(selectedItem)}
                    className={`rounded-full px-4 py-1 text-sm transition ${
                      isFavorite(selectedItem.symbol)
                        ? "bg-yellow-400/10 text-yellow-400"
                        : "bg-slate-950 text-slate-400 hover:text-yellow-400"
                    }`}
                  >
                    {isFavorite(selectedItem.symbol) ? "★ W ulubionych" : "☆ Dodaj"}
                  </button>
                </div>

                <p className="mt-5 rounded-2xl border border-slate-800 bg-slate-950/70 p-4 text-sm leading-6 text-slate-400">
                  {selectedItem.description}
                </p>

                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-500">
                      Wartość
                    </p>

                    <p className="mt-2 text-xl font-bold text-white">
                      {formatValue(selectedItem.value, selectedItem.unit)}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-500">
                      Zmiana
                    </p>

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
                        Wykres prezentujący zmianę wybranego wskaźnika w czasie.
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
                      <p className="text-xs text-slate-500">
                        Minimum
                      </p>

                      <p className="mt-1 font-semibold text-white">
                        {historyPoints.length ? formatValue(minValue, selectedItem.unit) : "-"}
                      </p>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                      <p className="text-xs text-slate-500">
                        Aktualnie
                      </p>

                      <p className="mt-1 font-semibold text-white">
                        {formatValue(selectedItem.value, selectedItem.unit)}
                      </p>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                      <p className="text-xs text-slate-500">
                        Maksimum
                      </p>

                      <p className="mt-1 font-semibold text-white">
                        {historyPoints.length ? formatValue(maxValue, selectedItem.unit) : "-"}
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
                          <span>{historyPoints.length ? formatValue(maxValue, selectedItem.unit) : "-"}</span>
                          <span>{formatValue((maxValue + minValue) / 2, selectedItem.unit)}</span>
                          <span>{historyPoints.length ? formatValue(minValue, selectedItem.unit) : "-"}</span>
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