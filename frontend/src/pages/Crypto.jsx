import { useEffect, useState } from "react"
import { getTopCryptocurrencies } from "../api/aiApi"
import useFavorites from "../hooks/useFavorites"

function Crypto({ user, isLoggedIn, onLoginRequired }) {
  const [coins, setCoins] = useState([])
  const [selectedCoin, setSelectedCoin] = useState(null)
  const {
    isFavorite,
    toggleFavorite,
    error: favoritesError,
  } = useFavorites("crypto", user?.id)

  const [chartRange, setChartRange] = useState("7D")
  const [hoveredPoint, setHoveredPoint] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    async function loadCryptoData() {
      try {
        const result = await getTopCryptocurrencies()
        setCoins(result)
        setSelectedCoin(result[0])
      } catch (error) {
        console.error(error)
        setError(true)
      } finally {
        setIsLoading(false)
      }
    }

    loadCryptoData()
  }, [])

  useEffect(() => {
    setHoveredPoint(null)
  }, [selectedCoin, chartRange])

  async function handleAddToFavorites(coin) {
    if (!isLoggedIn || user?.id === null || user?.id === undefined) {
      onLoginRequired()
      return
    }

    try {
      await toggleFavorite(coin)
    } catch (error) {
      console.error("Nie udało się zmienić ulubionych kryptowalut:", error)
    }
  }

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return "-"

    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: value < 1 ? 4 : 2,
    }).format(value)
  }

  const formatPercent = (value) => {
    if (value === null || value === undefined) return "-"

    const prefix = value > 0 ? "+" : ""
    return `${prefix}${value.toFixed(2)}%`
  }

  const formatDateTime = (date) => {
    return new Intl.DateTimeFormat("pl-PL", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date)
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

  const allSparklinePoints = selectedCoin?.sparkline_in_7d?.price || []

  const getVisiblePoints = () => {
    if (chartRange === "1H") return allSparklinePoints.slice(-2)
    if (chartRange === "24H") return allSparklinePoints.slice(-24)
    return allSparklinePoints
  }

  const sparklinePoints = getVisiblePoints()
  const minPrice = sparklinePoints.length > 0 ? Math.min(...sparklinePoints) : 0
  const maxPrice = sparklinePoints.length > 0 ? Math.max(...sparklinePoints) : 0

  const chartPoints = sparklinePoints.map((price, index) => {
    const x = (index / Math.max(sparklinePoints.length - 1, 1)) * 100
    const y =
      100 -
      ((price - minPrice) / Math.max(maxPrice - minPrice, 1)) * 100

    const hoursBack = sparklinePoints.length - 1 - index
    const time = new Date(Date.now() - hoursBack * 60 * 60 * 1000)

    return {
      x,
      y,
      price,
      timeLabel: formatDateTime(time),
    }
  })

  const sparklinePath = chartPoints.map((point) => `${point.x},${point.y}`).join(" ")
  const fillPath = chartPoints.length > 0 ? `0,100 ${sparklinePath} 100,100` : ""

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
        <div role="alert" className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {favoritesError}
        </div>
      )}
      <section className="relative overflow-hidden rounded-3xl border border-orange-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-orange-500/10 blur-3xl"></div>

        <div className="relative">
          <p className="mb-4 inline-flex rounded-full border border-orange-500/40 bg-orange-500/10 px-4 py-1 text-sm text-orange-400">
            Crypto market
          </p>

          <h2 className="text-4xl font-bold">
            Kryptowaluty
          </h2>

          <p className="mt-4 max-w-4xl text-slate-400">
            Kryptowaluty to cyfrowe aktywa działające w oparciu o technologię blockchain.
            Ich ceny zmieniają się dynamicznie pod wpływem popytu, podaży, wolumenu obrotu,
            informacji rynkowych, regulacji oraz nastrojów inwestorów. Ta sekcja prezentuje
            największe kryptowaluty według kapitalizacji rynkowej, ich aktualną cenę,
            zmienność oraz dane rynkowe.
          </p>

          <div className="mt-6 grid max-w-5xl grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-orange-400">Cena</p>
              <p className="mt-2 text-sm text-slate-400">
                Pokazuje aktualną wartość rynkową danej kryptowaluty.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-orange-400">Wolumen</p>
              <p className="mt-2 text-sm text-slate-400">
                Informuje o aktywności inwestorów w ostatnich 24 godzinach.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm text-orange-400">Zmienność</p>
              <p className="mt-2 text-sm text-slate-400">
                Pomaga ocenić ryzyko oraz dynamikę ruchu ceny.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8">
        {isLoading && (
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 text-slate-400">
            Pobieranie danych kryptowalut...
          </div>
        )}

        {error && (
          <div className="rounded-3xl border border-red-500/30 bg-slate-900/80 p-6 text-red-400">
            Nie udało się pobrać danych kryptowalut z internetu.
          </div>
        )}

        {!isLoading && !error && (
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.45fr_1fr]">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
              <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <h3 className="text-2xl font-bold">
                    TOP 100 kryptowalut
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">
                    Ranking według kapitalizacji rynkowej. Kliknij kryptowalutę, aby zobaczyć szczegóły.
                  </p>
                </div>

                <span className="rounded-full bg-orange-500/10 px-4 py-1 text-sm text-orange-400">
                  Live market data
                </span>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-slate-800">
                <table className="w-full min-w-[1050px] border-collapse text-sm">
                  <thead className="bg-slate-950 text-slate-400">
                    <tr>
                      <th className="px-4 py-4 text-left">☆</th>
                      <th className="px-4 py-4 text-left">#</th>
                      <th className="px-4 py-4 text-left">Coin</th>
                      <th className="px-4 py-4 text-right">Price</th>
                      <th className="px-4 py-4 text-right">1h</th>
                      <th className="px-4 py-4 text-right">24h</th>
                      <th className="px-4 py-4 text-right">7d</th>
                      <th className="px-4 py-4 text-right">24h Volume</th>
                      <th className="px-4 py-4 text-right">Market Cap</th>
                    </tr>
                  </thead>

                  <tbody>
                    {coins.map((coin) => {
                      const isSelected = selectedCoin?.id === coin.id

                      return (
                        <tr
                          key={coin.id}
                          onClick={() => setSelectedCoin(coin)}
                          className={`cursor-pointer border-t border-slate-800 transition hover:bg-slate-800/70 ${
                            isSelected ? "bg-cyan-500/10" : "bg-slate-950/40"
                          }`}
                        >
                          <td className="px-4 py-4">
                            <button
                              onClick={(event) => {
                                event.stopPropagation()
                                handleAddToFavorites(coin)
                              }}
                              className={`text-xl transition ${
                                isFavorite(coin.id)
                                  ? "text-yellow-400"
                                  : "text-slate-500 hover:text-yellow-400"
                              }`}
                              title={isFavorite(coin.id) ? "Usuń z ulubionych" : "Dodaj do ulubionych"}
                            >
                              {isFavorite(coin.id) ? "★" : "☆"}
                            </button>
                          </td>

                          <td className="px-4 py-4 text-slate-400">
                            {coin.market_cap_rank}
                          </td>

                          <td className="px-4 py-4">
                            <div className="flex items-center gap-3">
                              <img
                                src={coin.image}
                                alt={coin.name}
                                className="h-7 w-7 rounded-full"
                              />

                              <div>
                                <p className="font-semibold text-white">
                                  {coin.name}
                                </p>
                                <p className="text-xs uppercase text-slate-500">
                                  {coin.symbol}
                                </p>
                              </div>
                            </div>
                          </td>

                          <td className="px-4 py-4 text-right font-medium text-white">
                            {formatCurrency(coin.current_price)}
                          </td>

                          <td className="px-4 py-4 text-right">
                            <ChangeValue value={coin.price_change_percentage_1h_in_currency} />
                          </td>

                          <td className="px-4 py-4 text-right">
                            <ChangeValue value={coin.price_change_percentage_24h_in_currency} />
                          </td>

                          <td className="px-4 py-4 text-right">
                            <ChangeValue value={coin.price_change_percentage_7d_in_currency} />
                          </td>

                          <td className="px-4 py-4 text-right text-slate-300">
                            {formatCurrency(coin.total_volume)}
                          </td>

                          <td className="px-4 py-4 text-right text-slate-300">
                            {formatCurrency(coin.market_cap)}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="sticky top-24 max-h-[calc(100vh-7rem)] self-start overflow-y-auto rounded-3xl border border-cyan-500/30 bg-slate-900/90 p-6">
              {selectedCoin && (
                <>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <img
                        src={selectedCoin.image}
                        alt={selectedCoin.name}
                        className="h-12 w-12 rounded-full"
                      />

                      <div>
                        <p className="text-sm text-cyan-400">
                          Wybrana kryptowaluta
                        </p>

                        <h3 className="text-2xl font-bold">
                          {selectedCoin.name}{" "}
                          <span className="text-base uppercase text-slate-500">
                            {selectedCoin.symbol}
                          </span>
                        </h3>
                      </div>
                    </div>

                    <button
                      onClick={() => handleAddToFavorites(selectedCoin)}
                      className={`rounded-full px-4 py-1 text-sm transition ${
                        isFavorite(selectedCoin.id)
                          ? "bg-yellow-400/10 text-yellow-400"
                          : "bg-slate-950 text-slate-400 hover:text-yellow-400"
                      }`}
                    >
                      {isFavorite(selectedCoin.id) ? "★ W ulubionych" : "☆ Dodaj"}
                    </button>
                  </div>

                  <div className="mt-6 grid grid-cols-2 gap-4">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                      <p className="text-sm text-slate-500">Cena</p>
                      <p className="mt-2 text-xl font-bold text-white">
                        {formatCurrency(selectedCoin.current_price)}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                      <p className="text-sm text-slate-500">Zmiana 24h</p>
                      <p className="mt-2 text-xl font-bold">
                        <ChangeValue value={selectedCoin.price_change_percentage_24h_in_currency} />
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                      <p className="text-sm text-slate-500">Market cap</p>
                      <p className="mt-2 text-xl font-bold text-white">
                        {formatCurrency(selectedCoin.market_cap)}
                      </p>
                    </div>

                    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                      <p className="text-sm text-slate-500">Wolumen 24h</p>
                      <p className="mt-2 text-xl font-bold text-white">
                        {formatCurrency(selectedCoin.total_volume)}
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
                          Siatka pokazuje kierunek ceny, lokalne szczyty, dołki oraz zmienność.
                        </p>
                      </div>

                      <div className="flex rounded-full border border-slate-800 bg-slate-900 p-1">
                        {["1H", "24H", "7D"].map((range) => (
                          <button
                            key={range}
                            onClick={() => setChartRange(range)}
                            className={`rounded-full px-4 py-1 text-sm transition ${
                              chartRange === range
                                ? "bg-cyan-400 text-slate-950"
                                : "text-slate-400 hover:text-cyan-400"
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
                          {formatCurrency(selectedCoin.current_price)}
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
                      className="relative h-[420px] rounded-xl border border-cyan-500/20 bg-slate-950 p-4 pr-14"
                      onMouseMove={handleChartMouseMove}
                      onMouseLeave={() => setHoveredPoint(null)}
                    >
                      {sparklinePoints.length > 0 ? (
                        <>
                          <svg
                            viewBox="0 0 100 100"
                            preserveAspectRatio="none"
                            className="h-full w-full"
                          >
                            <defs>
                              <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
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
                              fill="url(#chartFill)"
                              className={
                                selectedCoin.price_change_percentage_7d_in_currency >= 0
                                  ? "text-emerald-400"
                                  : "text-red-400"
                              }
                            />

                            <polyline
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="1.6"
                              points={sparklinePath}
                              className={
                                selectedCoin.price_change_percentage_7d_in_currency >= 0
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
                                  className="text-cyan-300"
                                />

                                <circle
                                  cx={hoveredPoint.x}
                                  cy={hoveredPoint.y}
                                  r="1.7"
                                  fill="currentColor"
                                  className="text-cyan-300"
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
                              className="pointer-events-none absolute z-10 rounded-xl border border-cyan-500/30 bg-slate-900 px-4 py-3 text-xs shadow-xl shadow-cyan-950/40"
                              style={{
                                left: `${hoveredPoint.x}%`,
                                top: `${hoveredPoint.y}%`,
                                transform: "translate(-50%, -125%)",
                              }}
                            >
                              <p className="font-semibold text-cyan-400">
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

export default Crypto