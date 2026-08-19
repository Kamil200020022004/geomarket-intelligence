import { useEffect, useState } from "react"
import {
  getStockQuoteFromInternet,
  getStockHistoryFromInternet,
} from "../api/aiApi"

const FOREIGN_STOCK_SYMBOLS = [
  "aapl.us",
  "msft.us",
  "googl.us",
  "amzn.us",
  "nvda.us",
  "meta.us",
  "tsla.us",
  "amd.us",
  "nflx.us",
  "jpm.us",
]

const POLISH_STOCK_SYMBOLS = [
  "pkn",
  "pko",
  "peo",
  "kgh",
  "pzu",
  "cdr",
  "dnp",
  "ale",
  "lpp",
  "ccc",
]

function StockMarket({ isLoggedIn, onLoginRequired }) {
  const [marketFilter, setMarketFilter] = useState("foreign")
  const [stocks, setStocks] = useState([])
  const [selectedStock, setSelectedStock] = useState(null)
  const [history, setHistory] = useState([])
  const [chartRange, setChartRange] = useState("7D")
  const [hoveredPoint, setHoveredPoint] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  const [favorites, setFavorites] = useState(() => {
    const savedFavorites = localStorage.getItem("stockFavorites")
    return savedFavorites ? JSON.parse(savedFavorites) : []
  })

  const activeSymbols =
    marketFilter === "poland" ? POLISH_STOCK_SYMBOLS : FOREIGN_STOCK_SYMBOLS

  useEffect(() => {
    async function loadStocks() {
      setIsLoading(true)
      setError(false)
      setSelectedStock(null)
      setHistory([])

      try {
        const results = await Promise.all(
          activeSymbols.map(async (symbol) => {
            const data = await getStockQuoteFromInternet(symbol)

            return {
              symbol: data.symbol,
              name: data.name,
              price: data.price,
              change: data.change,
              volume: data.volume,
              marketCap: data.marketCap,
              date: data.date,
              time: data.time,
            }
          })
        )

        setStocks(results)
        setSelectedStock(results[0])
      } catch (error) {
        console.error(error)
        setError(true)
      } finally {
        setIsLoading(false)
      }
    }

    loadStocks()
  }, [marketFilter])

  useEffect(() => {
    async function loadHistory() {
      if (!selectedStock) return

      setHoveredPoint(null)

      try {
        const result = await getStockHistoryFromInternet(selectedStock.symbol)
        setHistory(result)
      } catch (error) {
        console.error(error)
        setHistory([])
      }
    }

    loadHistory()
  }, [selectedStock])

  const handleMarketChange = (market) => {
    setMarketFilter(market)
    setHoveredPoint(null)
  }

  const handleAddToFavorites = (stock) => {
    if (!isLoggedIn) {
      alert("Aby dodać spółkę do ulubionych, zaloguj się.")
      onLoginRequired()
      return
    }

    const alreadyExists = favorites.some(
      (favorite) => favorite.symbol === stock.symbol
    )

    if (alreadyExists) return

    const updatedFavorites = [...favorites, stock]
    setFavorites(updatedFavorites)
    localStorage.setItem("stockFavorites", JSON.stringify(updatedFavorites))
  }

  const isFavorite = (symbol) => {
    return favorites.some((favorite) => favorite.symbol === symbol)
  }

  const formatCurrency = (value) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "-"
    }

    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: marketFilter === "poland" ? "PLN" : "USD",
      maximumFractionDigits: 2,
    }).format(Number(value))
  }

  const formatNumber = (value) => {
    if (!value) return "-"

    return new Intl.NumberFormat("en-US", {
      notation: "compact",
      maximumFractionDigits: 2,
    }).format(Number(value))
  }

  const formatPercent = (value) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
      return "-"
    }

    const number = Number(value)
    const prefix = number > 0 ? "+" : ""
    return `${prefix}${number.toFixed(2)}%`
  }

  const getChangeClass = (value) => {
    if (value > 0) return "text-emerald-400"
    if (value < 0) return "text-red-400"
    return "text-slate-400"
  }

  const ChangeValue = ({ value }) => {
    const number = Number(value)
    const isPositive = number > 0
    const isNegative = number < 0

    return (
      <span
        className={`inline-flex items-center justify-end gap-1 ${getChangeClass(
          number
        )}`}
      >
        {isPositive && <span>▲</span>}
        {isNegative && <span>▼</span>}
        {!isPositive && !isNegative && <span>●</span>}
        {formatPercent(number)}
      </span>
    )
  }

  const getVisibleHistory = () => {
    if (chartRange === "1D") return history.slice(-24)
    if (chartRange === "1M") return history.slice(-30)
    return history.slice(-7)
  }

  const visibleHistory = getVisibleHistory()

  const fallbackHistory = selectedStock
    ? Array.from({ length: 12 }, (_, index) => ({
        price: Number(selectedStock.price) * (0.97 + index * 0.004),
        time: `Punkt ${index + 1}`,
      }))
    : []

  const chartData = visibleHistory.length > 0 ? visibleHistory : fallbackHistory

  const minPrice =
    chartData.length > 0
      ? Math.min(...chartData.map((item) => Number(item.price)))
      : 0

  const maxPrice =
    chartData.length > 0
      ? Math.max(...chartData.map((item) => Number(item.price)))
      : 0

  const chartPoints = chartData.map((item, index) => {
    const price = Number(item.price)
    const x = (index / Math.max(chartData.length - 1, 1)) * 100
    const y =
      100 -
      ((price - minPrice) / Math.max(maxPrice - minPrice, 1)) * 100

    return {
      x,
      y,
      price,
      timeLabel: item.time,
    }
  })

  const chartPath = chartPoints.map((point) => `${point.x},${point.y}`).join(" ")
  const fillPath = chartPoints.length > 0 ? `0,100 ${chartPath} 100,100` : ""

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
      <section className="relative overflow-hidden rounded-3xl border border-emerald-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-emerald-500/10 blur-3xl"></div>

        <div className="relative">
          <p className="mb-4 inline-flex rounded-full border border-emerald-500/40 bg-emerald-500/10 px-4 py-1 text-sm text-emerald-400">
            Stock market
          </p>

          <h2 className="text-4xl font-bold">Giełda</h2>

          <p className="mt-4 max-w-4xl text-slate-400">
            Zakładka prezentuje dane giełdowe pobierane tymczasowo z internetu.
            Użytkownik może przełączać rynek zagraniczny i polski, sprawdzać cenę,
            zmianę procentową, wolumen oraz wykres wybranej spółki. Później źródło
            danych może zostać podmienione na dane przygotowane przez Sebastiana.
          </p>

          <div className="mt-6 grid max-w-5xl grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-emerald-400">Cena</p>
              <p className="mt-2 text-sm text-slate-400">
                Aktualna cena instrumentu z publicznego źródła danych.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-emerald-400">Wolumen</p>
              <p className="mt-2 text-sm text-slate-400">
                Liczba akcji będących przedmiotem obrotu w danym okresie.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-emerald-400">Filtr rynku</p>
              <p className="mt-2 text-sm text-slate-400">
                Możliwość przełączania między spółkami zagranicznymi i polskimi.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8">
        {isLoading && (
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 text-slate-400">
            Pobieranie danych giełdowych z internetu...
          </div>
        )}

        {error && (
          <div className="rounded-3xl border border-red-500/30 bg-slate-900/80 p-6 text-red-400">
            Nie udało się pobrać danych giełdowych z internetu.
          </div>
        )}

        {!isLoading && !error && (
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.45fr_1fr]">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
              <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <h3 className="text-2xl font-bold">
                    Wybrane spółki giełdowe
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">
                    Kliknij spółkę, aby zobaczyć szczegóły i wykres.
                  </p>

                  <div className="mt-4 inline-flex rounded-full border border-slate-800 bg-slate-950 p-1">
                    <button
                      onClick={() => handleMarketChange("foreign")}
                      className={`rounded-full px-4 py-2 text-sm transition ${
                        marketFilter === "foreign"
                          ? "bg-emerald-400 text-slate-950"
                          : "text-slate-400 hover:text-emerald-400"
                      }`}
                    >
                      Zagraniczne
                    </button>

                    <button
                      onClick={() => handleMarketChange("poland")}
                      className={`rounded-full px-4 py-2 text-sm transition ${
                        marketFilter === "poland"
                          ? "bg-emerald-400 text-slate-950"
                          : "text-slate-400 hover:text-emerald-400"
                      }`}
                    >
                      Polska
                    </button>
                  </div>
                </div>

                <span className="rounded-full bg-emerald-500/10 px-4 py-1 text-sm text-emerald-400">
                  Internet market data
                </span>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-slate-800">
                <table className="w-full min-w-[950px] border-collapse text-sm">
                  <thead className="bg-slate-950 text-slate-400">
                    <tr>
                      <th className="px-4 py-4 text-left">☆</th>
                      <th className="px-4 py-4 text-left">Symbol</th>
                      <th className="px-4 py-4 text-left">Spółka</th>
                      <th className="px-4 py-4 text-right">Cena</th>
                      <th className="px-4 py-4 text-right">Zmiana</th>
                      <th className="px-4 py-4 text-right">Wolumen</th>
                      <th className="px-4 py-4 text-right">Data</th>
                    </tr>
                  </thead>

                  <tbody>
                    {stocks.map((stock) => {
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
                            >
                              {isFavorite(stock.symbol) ? "★" : "☆"}
                            </button>
                          </td>

                          <td className="px-4 py-4 font-semibold text-emerald-400">
                            {stock.symbol.toUpperCase()}
                          </td>

                          <td className="px-4 py-4 text-white">
                            {stock.name.toUpperCase()}
                          </td>

                          <td className="px-4 py-4 text-right font-medium text-white">
                            {formatCurrency(stock.price)}
                          </td>

                          <td className="px-4 py-4 text-right">
                            <ChangeValue value={stock.change} />
                          </td>

                          <td className="px-4 py-4 text-right text-slate-300">
                            {formatNumber(stock.volume)}
                          </td>

                          <td className="px-4 py-4 text-right text-slate-300">
                            {stock.date || "-"}
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
                        Wybrana spółka
                      </p>

                      <h3 className="text-2xl font-bold">
                        {selectedStock.symbol.toUpperCase()}
                      </h3>

                      <p className="mt-1 text-sm text-slate-400">
                        {selectedStock.name.toUpperCase()}
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
                        {formatCurrency(selectedStock.price)}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                      <p className="text-sm text-slate-500">Zmiana dzienna</p>
                      <p className="mt-2 text-xl font-bold">
                        <ChangeValue value={selectedStock.change} />
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                      <p className="text-sm text-slate-500">Wolumen</p>
                      <p className="mt-2 text-xl font-bold text-white">
                        {formatNumber(selectedStock.volume)}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                      <p className="text-sm text-slate-500">Data / godzina</p>
                      <p className="mt-2 text-xl font-bold text-white">
                        {selectedStock.date || "-"} {selectedStock.time || ""}
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
                          Dane historyczne pobierane z internetu.
                        </p>
                      </div>

                      <div className="flex rounded-full border border-slate-800 bg-slate-900 p-1">
                        {["1D", "7D", "1M"].map((range) => (
                          <button
                            key={range}
                            onClick={() => {
                              setChartRange(range)
                              setHoveredPoint(null)
                            }}
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
                          {formatCurrency(minPrice)}
                        </p>
                      </div>

                      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                        <p className="text-xs text-slate-500">Aktualnie</p>
                        <p className="mt-1 font-semibold text-white">
                          {formatCurrency(selectedStock.price)}
                        </p>
                      </div>

                      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-3">
                        <p className="text-xs text-slate-500">Maksimum</p>
                        <p className="mt-1 font-semibold text-white">
                          {formatCurrency(maxPrice)}
                        </p>
                      </div>
                    </div>

                    <div
                      className="relative h-[420px] rounded-xl border border-emerald-500/20 bg-slate-950 p-4 pr-14"
                      onMouseMove={handleChartMouseMove}
                      onMouseLeave={() => setHoveredPoint(null)}
                    >
                      {chartPoints.length > 0 ? (
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
                              points={fillPath}
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
                              points={chartPath}
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
                            <span>{formatCurrency(maxPrice)}</span>
                            <span>{formatCurrency((maxPrice + minPrice) / 2)}</span>
                            <span>{formatCurrency(minPrice)}</span>
                          </div>

                          {hoveredPoint && (
                            <div
                              className="pointer-events-none absolute z-10 rounded-xl border border-emerald-500/30 bg-slate-900 px-4 py-3 text-xs shadow-xl"
                              style={{
                                left: `${hoveredPoint.x}%`,
                                top: `${hoveredPoint.y}%`,
                                transform: "translate(-50%, -125%)",
                              }}
                            >
                              <p className="font-semibold text-emerald-400">
                                {formatCurrency(hoveredPoint.price)}
                              </p>

                              <p className="mt-1 text-slate-400">
                                {hoveredPoint.timeLabel}
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
        )}
      </section>
    </main>
  )
}

export default StockMarket