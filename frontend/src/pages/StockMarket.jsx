import { useEffect, useState } from "react"
import useFavorites from "../hooks/useFavorites"

// Backend Sebastiana udostępnia notowania zapisane w Lakehouse.
const MARKET_API_URL = (
  import.meta.env.VITE_MARKET_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "")

function normalizeStock(stock) {
  return {
    ...stock,
    change: stock.change ?? null,
    marketCap: stock.marketCap ?? stock.market_cap ?? null,
    history: Array.isArray(stock.history)
      ? stock.history
          .filter((point) => point && point.price != null && Number.isFinite(Number(point.price)))
          .map((point) => ({
            time: point.time,
            price: Number(point.price),
          }))
      : [],
  }
}

function formatHistoryTime(value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? String(value ?? "-")
    : date.toLocaleString("pl-PL", {
        day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit",
      })
}

function StockMarket({ user, isLoggedIn, onLoginRequired }) {
  const [stocks, setStocks] = useState([])
  const [selectedStock, setSelectedStock] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState("")
  const {
    isFavorite,
    toggleFavorite,
    error: favoritesError,
  } = useFavorites("stock", user?.id)

  const [chartRange, setChartRange] = useState("1M")
  const [hoveredPoint, setHoveredPoint] = useState(null)

  useEffect(() => {
    let active = true
    let controller = null

    async function loadStocks() {
      if (controller) return // nie nakładaj na siebie kolejnych odświeżeń
      controller = new AbortController()
      const currentController = controller

      try {
        const response = await fetch(`${MARKET_API_URL}/api/stocks`, {
          signal: currentController.signal,
          cache: "no-store",
        })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const data = await response.json()
        if (!Array.isArray(data)) throw new Error("Nieprawidłowy format notowań")

        const incoming = data.map(normalizeStock)
        if (active) {
          setStocks(incoming)
          setSelectedStock((current) =>
            incoming.find((stock) => stock.symbol === current?.symbol) || incoming[0] || null
          )
          setLoadError("")
        }
      } catch (error) {
        if (active && error.name !== "AbortError") {
          console.error("Nie udało się pobrać notowań giełdowych:", error)
          setLoadError("Nie można pobrać notowań z backendu Sebastiana (port 8000).")
        }
      } finally {
        if (active) setIsLoading(false)
        if (controller === currentController) controller = null
      }
    }

    loadStocks()
    const interval = setInterval(loadStocks, 60_000)
    return () => {
      active = false
      clearInterval(interval)
      controller?.abort()
    }
  }, [])

  useEffect(() => {
    setHoveredPoint(null)
  }, [selectedStock, chartRange])

  async function handleAddToFavorites(stock) {
    if (!isLoggedIn || user?.id === null || user?.id === undefined) {
      onLoginRequired()
      return
    }

    try {
      await toggleFavorite(stock)
    } catch (error) {
      console.error("Nie udało się zmienić ulubionych:", error)
    }
  }

  const formatCurrency = (value, market) => {
    if (value === null || value === undefined) return "-"

    return new Intl.NumberFormat("pl-PL", {
      style: "currency",
      currency: market === "Polska" ? "PLN" : "USD",
      maximumFractionDigits: value > 1000 ? 0 : 2,
    }).format(value)
  }

  const formatLargeNumber = (value) => {
    if (value === null || value === undefined) return "-"

    return new Intl.NumberFormat("pl-PL", {
      notation: "compact",
      maximumFractionDigits: 2,
    }).format(value)
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
    const history = selectedStock?.history || []

    const days = chartRange === "1D" ? 1 : chartRange === "1W" ? 7 : 30
    const cutoff = Date.now() - days * 24 * 60 * 60 * 1000
    const dated = history.filter((point) => !Number.isNaN(new Date(point.time).getTime()))
    if (dated.length === history.length && history.length > 0) {
      return dated.filter((point) => new Date(point.time).getTime() >= cutoff)
    }
    // Zgodność z historią bez dat — nie generujemy fikcyjnych punktów.
    return history
  }

  const historyPoints = getVisibleHistory()

  const minPrice =
    historyPoints.length > 0
      ? Math.min(...historyPoints.map((point) => point.price))
      : 0

  const maxPrice =
    historyPoints.length > 0
      ? Math.max(...historyPoints.map((point) => point.price))
      : 0

  const chartPoints = historyPoints.map((point, index) => {
    const x = (index / Math.max(historyPoints.length - 1, 1)) * 100
    const y =
      100 -
      ((point.price - minPrice) / Math.max(maxPrice - minPrice, 1)) * 100

    return {
      x,
      y,
      price: point.price,
      timeLabel: formatHistoryTime(point.time),
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
      {favoritesError && (
        <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {favoritesError}
        </div>
      )}
      <section className="relative overflow-hidden rounded-3xl border border-emerald-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-emerald-500/10 blur-3xl"></div>

        <div className="relative">
          <p className="mb-4 inline-flex rounded-full border border-emerald-500/40 bg-emerald-500/10 px-4 py-1 text-sm text-emerald-400">
            Stock market
          </p>

          <h2 className="text-4xl font-bold">
            Giełda
          </h2>

          <p className="mt-4 max-w-4xl leading-7 text-slate-300">
            Zakładka prezentuje wybrane instrumenty giełdowe z rynku
            polskiego i zagranicznego. Użytkownik może sprawdzić cenę,
            zmianę procentową, wolumen, kapitalizację oraz wykres
            historyczny wybranego instrumentu.
          </p>

          <div className="mt-6 grid max-w-5xl grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-emerald-400">
                Cena
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Aktualna wartość instrumentu wraz ze zmianą procentową
                względem poprzedniego okresu.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-emerald-400">
                Wolumen
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Informacja o aktywności handlowej i liczbie jednostek
                będących przedmiotem obrotu.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-emerald-400">
                Rynek
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Oznaczenie rynku, z którego pochodzi instrument: polskiego
                lub zagranicznego.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8">
        {isLoading && (
          <div className="mb-4 rounded-xl border border-slate-800 bg-slate-900 p-4 text-slate-300">
            Pobieranie notowań giełdowych...
          </div>
        )}
        {loadError && (
          <div role="alert" className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
            {loadError} {stocks.length > 0 ? "Wyświetlane są ostatnio pobrane dane." : ""}
          </div>
        )}
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.45fr_1fr]">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h3 className="text-2xl font-bold">
                  Lista instrumentów giełdowych
                </h3>

                <p className="mt-1 text-sm text-slate-400">
                  Zestawienie instrumentów z rynku polskiego i zagranicznego.
                </p>
              </div>

              <span className="rounded-full bg-emerald-500/10 px-4 py-1 text-sm text-emerald-400">
                Market data
              </span>
            </div>

            <div className="overflow-x-auto rounded-2xl border border-slate-800">
              <table className="w-full min-w-[1050px] border-collapse text-sm">
                <thead className="bg-slate-950 text-slate-400">
                  <tr>
                    <th className="px-4 py-4 text-left">☆</th>
                    <th className="px-4 py-4 text-left">#</th>
                    <th className="px-4 py-4 text-left">Spółka</th>
                    <th className="px-4 py-4 text-left">Rynek</th>
                    <th className="px-4 py-4 text-right">Cena</th>
                    <th className="px-4 py-4 text-right">Zmiana</th>
                    <th className="px-4 py-4 text-right">Wolumen</th>
                    <th className="px-4 py-4 text-right">Kapitalizacja</th>
                  </tr>
                </thead>

                <tbody>
                  {stocks.map((stock, index) => {
                    const isSelected = selectedStock?.symbol === stock.symbol

                    return (
                      <tr
                        key={stock.symbol}
                        onClick={() => setSelectedStock(stock)}
                        className={`cursor-pointer border-t border-slate-800 transition hover:bg-slate-800/70 ${
                          isSelected ? "bg-emerald-500/10" : "bg-slate-950/40"
                        }`}
                      >
                        <td className="px-4 py-4">
                          <button
                            onClick={(event) => {
                              event.stopPropagation()
                              handleAddToFavorites(stock)
                            }}
                            className={`text-xl transition ${
                              isFavorite(stock.symbol)
                                ? "text-yellow-400"
                                : "text-slate-500 hover:text-yellow-400"
                            }`}
                            title={isFavorite(stock.symbol) ? "Usuń z ulubionych" : "Dodaj do ulubionych"}
                          >
                            {isFavorite(stock.symbol) ? "★" : "☆"}
                          </button>
                        </td>

                        <td className="px-4 py-4 text-slate-400">
                          {index + 1}
                        </td>

                        <td className="px-4 py-4">
                          <div>
                            <p className="font-semibold text-white">
                              {stock.name}
                            </p>

                            <p className="text-xs uppercase text-slate-500">
                              {stock.symbol}
                            </p>
                          </div>
                        </td>

                        <td className="px-4 py-4">
                          <span
                            className={`rounded-full px-3 py-1 text-xs ${
                              stock.market === "Polska"
                                ? "bg-red-500/10 text-red-300"
                                : "bg-cyan-500/10 text-cyan-300"
                            }`}
                          >
                            {stock.market}
                          </span>
                        </td>

                        <td className="px-4 py-4 text-right font-medium text-white">
                          {formatCurrency(stock.price, stock.market)}
                        </td>

                        <td className="px-4 py-4 text-right">
                          <ChangeValue value={stock.change} />
                        </td>

                        <td className="px-4 py-4 text-right text-slate-300">
                          {formatLargeNumber(stock.volume)}
                        </td>

                        <td className="px-4 py-4 text-right text-slate-300">
                          {formatLargeNumber(stock.marketCap)}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="sticky top-24 max-h-[calc(100vh-7rem)] self-start overflow-y-auto rounded-3xl border border-emerald-500/30 bg-slate-900/90 p-6">
            {selectedStock && (
              <>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm text-emerald-400">
                      Wybrany instrument
                    </p>

                    <h3 className="mt-1 text-2xl font-bold">
                      {selectedStock.name}
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                      {selectedStock.symbol} · {selectedStock.market}
                    </p>
                  </div>

                  <button
                    onClick={() => handleAddToFavorites(selectedStock)}
                    className={`rounded-full px-4 py-1 text-sm transition ${
                      isFavorite(selectedStock.symbol)
                        ? "bg-yellow-400/10 text-yellow-400"
                        : "bg-slate-950 text-slate-400 hover:text-yellow-400"
                    }`}
                  >
                    {isFavorite(selectedStock.symbol) ? "★ W ulubionych" : "☆ Dodaj"}
                  </button>
                </div>

                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-500">Cena</p>
                    <p className="mt-2 text-xl font-bold text-white">
                      {formatCurrency(selectedStock.price, selectedStock.market)}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-500">Zmiana</p>
                    <p className="mt-2 text-xl font-bold">
                      <ChangeValue value={selectedStock.change} />
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-500">Wolumen</p>
                    <p className="mt-2 text-xl font-bold text-white">
                      {formatLargeNumber(selectedStock.volume)}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-500">Kapitalizacja</p>
                    <p className="mt-2 text-xl font-bold text-white">
                      {formatLargeNumber(selectedStock.marketCap)}
                    </p>
                  </div>
                </div>

                <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                  <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <h4 className="font-semibold">
                        Wykres ceny
                      </h4>

                      <p className="text-sm text-slate-500">
                        Wykres prezentujący kierunek zmian ceny wybranego instrumentu.
                      </p>
                    </div>

                    <div className="flex rounded-full border border-slate-800 bg-slate-900 p-1">
                      {["1D", "1W", "1M"].map((range) => (
                        <button
                          key={range}
                          onClick={() => setChartRange(range)}
                          className={`rounded-full px-4 py-1 text-sm transition ${
                            chartRange === range
                              ? "bg-emerald-400 text-slate-950"
                              : "text-slate-400 hover:text-emerald-400"
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
                        {formatCurrency(minPrice, selectedStock.market)}
                      </p>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                      <p className="text-xs text-slate-500">Aktualnie</p>
                      <p className="mt-1 font-semibold text-white">
                        {formatCurrency(selectedStock.price, selectedStock.market)}
                      </p>
                    </div>

                    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                      <p className="text-xs text-slate-500">Maksimum</p>
                      <p className="mt-1 font-semibold text-white">
                        {formatCurrency(maxPrice, selectedStock.market)}
                      </p>
                    </div>
                  </div>

                  <div
                    className="relative h-[420px] rounded-xl border border-emerald-500/20 bg-slate-950 p-4 pr-14"
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
                            <linearGradient id="stockChartFill" x1="0" y1="0" x2="0" y2="1">
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
                            fill="url(#stockChartFill)"
                            className={
                              selectedStock.change >= 0
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
                              selectedStock.change >= 0
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
                                className="text-emerald-300"
                              />

                              <circle
                                cx={hoveredPoint.x}
                                cy={hoveredPoint.y}
                                r="1.7"
                                fill="currentColor"
                                className="text-emerald-300"
                              />
                            </>
                          )}
                        </svg>

                        <div className="absolute right-3 top-3 flex h-[calc(100%-24px)] flex-col justify-between text-xs text-slate-500">
                          <span>{formatCurrency(maxPrice, selectedStock.market)}</span>
                          <span>{formatCurrency((maxPrice + minPrice) / 2, selectedStock.market)}</span>
                          <span>{formatCurrency(minPrice, selectedStock.market)}</span>
                        </div>

                        {hoveredPoint && (
                          <div
                            className="pointer-events-none absolute z-10 rounded-xl border border-emerald-500/30 bg-slate-900 px-4 py-3 text-xs shadow-xl shadow-emerald-950/40"
                            style={{
                              left: `${hoveredPoint.x}%`,
                              top: `${hoveredPoint.y}%`,
                              transform: "translate(-50%, -125%)",
                            }}
                          >
                            <p className="font-semibold text-emerald-400">
                              {formatCurrency(hoveredPoint.price, selectedStock.market)}
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

export default StockMarket