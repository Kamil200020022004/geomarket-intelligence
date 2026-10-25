import { useEffect, useState } from "react"
import useFavorites from "../hooks/useFavorites"

const STOCKS = [
  // 50 zagranicznych
  { symbol: "AAPL", name: "Apple", market: "Zagraniczny", price: 229.4, change: 1.24, volume: 58420000, marketCap: 3580000000000 },
  { symbol: "MSFT", name: "Microsoft", market: "Zagraniczny", price: 418.9, change: -0.42, volume: 22100000, marketCap: 3110000000000 },
  { symbol: "NVDA", name: "Nvidia", market: "Zagraniczny", price: 124.7, change: 2.86, volume: 315000000, marketCap: 3060000000000 },
  { symbol: "GOOGL", name: "Alphabet", market: "Zagraniczny", price: 164.2, change: 0.73, volume: 27800000, marketCap: 2020000000000 },
  { symbol: "AMZN", name: "Amazon", market: "Zagraniczny", price: 186.5, change: -1.18, volume: 39800000, marketCap: 1940000000000 },
  { symbol: "META", name: "Meta Platforms", market: "Zagraniczny", price: 512.3, change: 1.77, volume: 14200000, marketCap: 1290000000000 },
  { symbol: "TSLA", name: "Tesla", market: "Zagraniczny", price: 247.6, change: -2.31, volume: 102000000, marketCap: 790000000000 },
  { symbol: "AMD", name: "Advanced Micro Devices", market: "Zagraniczny", price: 153.2, change: 3.12, volume: 67200000, marketCap: 248000000000 },
  { symbol: "NFLX", name: "Netflix", market: "Zagraniczny", price: 697.5, change: 0.95, volume: 4100000, marketCap: 300000000000 },
  { symbol: "JPM", name: "JPMorgan Chase", market: "Zagraniczny", price: 211.8, change: -0.35, volume: 8800000, marketCap: 608000000000 },
  { symbol: "V", name: "Visa", market: "Zagraniczny", price: 276.9, change: 0.48, volume: 6200000, marketCap: 560000000000 },
  { symbol: "MA", name: "Mastercard", market: "Zagraniczny", price: 463.7, change: 0.66, volume: 2900000, marketCap: 430000000000 },
  { symbol: "KO", name: "Coca-Cola", market: "Zagraniczny", price: 63.4, change: -0.21, volume: 14500000, marketCap: 273000000000 },
  { symbol: "PEP", name: "PepsiCo", market: "Zagraniczny", price: 171.6, change: 0.19, volume: 4800000, marketCap: 236000000000 },
  { symbol: "MCD", name: "McDonald's", market: "Zagraniczny", price: 287.1, change: -0.74, volume: 3100000, marketCap: 207000000000 },
  { symbol: "DIS", name: "Walt Disney", market: "Zagraniczny", price: 91.8, change: 1.08, volume: 9700000, marketCap: 167000000000 },
  { symbol: "INTC", name: "Intel", market: "Zagraniczny", price: 21.7, change: -1.92, volume: 76400000, marketCap: 93000000000 },
  { symbol: "BA", name: "Boeing", market: "Zagraniczny", price: 173.4, change: 0.84, volume: 6100000, marketCap: 107000000000 },
  { symbol: "WMT", name: "Walmart", market: "Zagraniczny", price: 80.3, change: 0.31, volume: 15800000, marketCap: 646000000000 },
  { symbol: "NKE", name: "Nike", market: "Zagraniczny", price: 78.6, change: -0.58, volume: 8600000, marketCap: 117000000000 },
  { symbol: "ORCL", name: "Oracle", market: "Zagraniczny", price: 139.5, change: 1.44, volume: 9300000, marketCap: 383000000000 },
  { symbol: "CRM", name: "Salesforce", market: "Zagraniczny", price: 252.8, change: -0.86, volume: 5100000, marketCap: 242000000000 },
  { symbol: "ADBE", name: "Adobe", market: "Zagraniczny", price: 529.4, change: 1.12, volume: 2800000, marketCap: 234000000000 },
  { symbol: "PYPL", name: "PayPal", market: "Zagraniczny", price: 67.2, change: -1.05, volume: 11400000, marketCap: 71000000000 },
  { symbol: "UBER", name: "Uber", market: "Zagraniczny", price: 73.9, change: 2.17, volume: 18400000, marketCap: 155000000000 },
  { symbol: "ABNB", name: "Airbnb", market: "Zagraniczny", price: 131.4, change: -0.33, volume: 4600000, marketCap: 83000000000 },
  { symbol: "SHOP", name: "Shopify", market: "Zagraniczny", price: 74.5, change: 1.61, volume: 8200000, marketCap: 96000000000 },
  { symbol: "BABA", name: "Alibaba", market: "Zagraniczny", price: 79.2, change: -0.91, volume: 16600000, marketCap: 192000000000 },
  { symbol: "PFE", name: "Pfizer", market: "Zagraniczny", price: 29.1, change: 0.27, volume: 33100000, marketCap: 165000000000 },
  { symbol: "JNJ", name: "Johnson & Johnson", market: "Zagraniczny", price: 158.7, change: -0.18, volume: 7200000, marketCap: 382000000000 },
  { symbol: "XOM", name: "Exxon Mobil", market: "Zagraniczny", price: 118.6, change: 0.94, volume: 14800000, marketCap: 468000000000 },
  { symbol: "CVX", name: "Chevron", market: "Zagraniczny", price: 146.3, change: 0.51, volume: 6900000, marketCap: 270000000000 },
  { symbol: "GS", name: "Goldman Sachs", market: "Zagraniczny", price: 492.8, change: -0.39, volume: 2400000, marketCap: 158000000000 },
  { symbol: "BAC", name: "Bank of America", market: "Zagraniczny", price: 39.7, change: 0.82, volume: 42100000, marketCap: 306000000000 },
  { symbol: "C", name: "Citigroup", market: "Zagraniczny", price: 61.3, change: -0.28, volume: 13800000, marketCap: 117000000000 },
  { symbol: "T", name: "AT&T", market: "Zagraniczny", price: 19.8, change: 0.14, volume: 35200000, marketCap: 142000000000 },
  { symbol: "VZ", name: "Verizon", market: "Zagraniczny", price: 41.5, change: -0.22, volume: 19600000, marketCap: 175000000000 },
  { symbol: "QCOM", name: "Qualcomm", market: "Zagraniczny", price: 171.2, change: 1.93, volume: 8400000, marketCap: 191000000000 },
  { symbol: "AVGO", name: "Broadcom", market: "Zagraniczny", price: 167.6, change: 2.31, volume: 23800000, marketCap: 780000000000 },
  { symbol: "TXN", name: "Texas Instruments", market: "Zagraniczny", price: 201.4, change: -0.42, volume: 5200000, marketCap: 183000000000 },
  { symbol: "IBM", name: "IBM", market: "Zagraniczny", price: 198.2, change: 0.61, volume: 4500000, marketCap: 183000000000 },
  { symbol: "GE", name: "General Electric", market: "Zagraniczny", price: 169.4, change: 1.02, volume: 6400000, marketCap: 184000000000 },
  { symbol: "GM", name: "General Motors", market: "Zagraniczny", price: 48.7, change: -1.11, volume: 13300000, marketCap: 55000000000 },
  { symbol: "F", name: "Ford", market: "Zagraniczny", price: 10.9, change: 0.74, volume: 49200000, marketCap: 43000000000 },
  { symbol: "SBUX", name: "Starbucks", market: "Zagraniczny", price: 95.6, change: -0.47, volume: 7100000, marketCap: 108000000000 },
  { symbol: "COST", name: "Costco", market: "Zagraniczny", price: 881.2, change: 0.88, volume: 1900000, marketCap: 391000000000 },
  { symbol: "HD", name: "Home Depot", market: "Zagraniczny", price: 363.5, change: -0.64, volume: 3800000, marketCap: 361000000000 },
  { symbol: "LOW", name: "Lowe's", market: "Zagraniczny", price: 241.9, change: 0.39, volume: 2700000, marketCap: 137000000000 },
  { symbol: "UPS", name: "UPS", market: "Zagraniczny", price: 132.7, change: -0.71, volume: 4200000, marketCap: 113000000000 },
  { symbol: "FDX", name: "FedEx", market: "Zagraniczny", price: 296.4, change: 1.26, volume: 2100000, marketCap: 73000000000 },

  // 50 polskich
  { symbol: "PKN", name: "Orlen", market: "Polska", price: 63.4, change: 1.11, volume: 4210000, marketCap: 74000000000 },
  { symbol: "PKO", name: "PKO BP", market: "Polska", price: 58.2, change: -0.43, volume: 3820000, marketCap: 72700000000 },
  { symbol: "PEO", name: "Bank Pekao", market: "Polska", price: 168.7, change: 0.92, volume: 890000, marketCap: 44300000000 },
  { symbol: "KGH", name: "KGHM", market: "Polska", price: 149.3, change: 2.14, volume: 1260000, marketCap: 29800000000 },
  { symbol: "PZU", name: "PZU", market: "Polska", price: 51.6, change: -0.27, volume: 1870000, marketCap: 44600000000 },
  { symbol: "CDR", name: "CD Projekt", market: "Polska", price: 174.8, change: 1.73, volume: 920000, marketCap: 17600000000 },
  { symbol: "DNP", name: "Dino Polska", market: "Polska", price: 386.5, change: -1.22, volume: 310000, marketCap: 37900000000 },
  { symbol: "ALE", name: "Allegro", market: "Polska", price: 34.2, change: 0.67, volume: 3810000, marketCap: 36000000000 },
  { symbol: "LPP", name: "LPP", market: "Polska", price: 15420, change: 0.41, volume: 9400, marketCap: 28600000000 },
  { symbol: "CCC", name: "CCC", market: "Polska", price: 147.9, change: 3.21, volume: 410000, marketCap: 8600000000 },
  { symbol: "MBK", name: "mBank", market: "Polska", price: 612.5, change: -0.76, volume: 71000, marketCap: 26000000000 },
  { symbol: "SPL", name: "Santander Bank Polska", market: "Polska", price: 487.8, change: 0.33, volume: 62000, marketCap: 49800000000 },
  { symbol: "ING", name: "ING Bank Śląski", market: "Polska", price: 286.4, change: 0.89, volume: 48000, marketCap: 37200000000 },
  { symbol: "ALR", name: "Alior Bank", market: "Polska", price: 86.3, change: -1.41, volume: 740000, marketCap: 11300000000 },
  { symbol: "OPL", name: "Orange Polska", market: "Polska", price: 8.7, change: 0.22, volume: 2360000, marketCap: 11400000000 },
  { symbol: "TPE", name: "Tauron", market: "Polska", price: 3.9, change: 1.95, volume: 8120000, marketCap: 6900000000 },
  { symbol: "PGE", name: "PGE", market: "Polska", price: 7.8, change: -0.64, volume: 5200000, marketCap: 14600000000 },
  { symbol: "ENA", name: "Enea", market: "Polska", price: 10.2, change: 1.18, volume: 1430000, marketCap: 4500000000 },
  { symbol: "JSW", name: "JSW", market: "Polska", price: 28.4, change: -2.54, volume: 1620000, marketCap: 3340000000 },
  { symbol: "ACP", name: "Asseco Poland", market: "Polska", price: 89.6, change: 0.44, volume: 210000, marketCap: 7440000000 },
  { symbol: "XTB", name: "XTB", market: "Polska", price: 62.1, change: 2.08, volume: 680000, marketCap: 7300000000 },
  { symbol: "BFT", name: "Benefit Systems", market: "Polska", price: 2760, change: -0.51, volume: 7200, marketCap: 8100000000 },
  { symbol: "KTY", name: "Grupa Kęty", market: "Polska", price: 813, change: 0.73, volume: 9600, marketCap: 7900000000 },
  { symbol: "KER", name: "Kernel", market: "Polska", price: 12.8, change: -1.02, volume: 180000, marketCap: 1100000000 },
  { symbol: "ATT", name: "Grupa Azoty", market: "Polska", price: 21.4, change: 0.19, volume: 390000, marketCap: 2120000000 },
  { symbol: "GPW", name: "GPW", market: "Polska", price: 44.8, change: 0.54, volume: 84000, marketCap: 1880000000 },
  { symbol: "MIL", name: "Bank Millennium", market: "Polska", price: 9.1, change: -0.33, volume: 2210000, marketCap: 11000000000 },
  { symbol: "BHW", name: "Bank Handlowy", market: "Polska", price: 98.7, change: 0.26, volume: 67000, marketCap: 12900000000 },
  { symbol: "CAR", name: "Inter Cars", market: "Polska", price: 575, change: 1.01, volume: 12300, marketCap: 8140000000 },
  { symbol: "EUR", name: "Eurocash", market: "Polska", price: 9.8, change: -0.91, volume: 360000, marketCap: 1360000000 },
  { symbol: "CPS", name: "Cyfrowy Polsat", market: "Polska", price: 13.5, change: 0.37, volume: 920000, marketCap: 8600000000 },
  { symbol: "11B", name: "11 bit studios", market: "Polska", price: 512, change: 2.22, volume: 21000, marketCap: 1240000000 },
  { symbol: "WPL", name: "Wirtualna Polska", market: "Polska", price: 92.4, change: -0.28, volume: 37000, marketCap: 2700000000 },
  { symbol: "MAB", name: "Mabion", market: "Polska", price: 17.6, change: 1.49, volume: 180000, marketCap: 285000000 },
  { symbol: "DAT", name: "DataWalk", market: "Polska", price: 48.2, change: -1.83, volume: 41000, marketCap: 300000000 },
  { symbol: "TEN", name: "Ten Square Games", market: "Polska", price: 92.5, change: 0.76, volume: 58000, marketCap: 670000000 },
  { symbol: "PLW", name: "PlayWay", market: "Polska", price: 314, change: -0.62, volume: 19000, marketCap: 2070000000 },
  { symbol: "RBW", name: "Rainbow Tours", market: "Polska", price: 92.7, change: 1.82, volume: 48000, marketCap: 1350000000 },
  { symbol: "VRG", name: "VRG", market: "Polska", price: 4.1, change: 0.98, volume: 490000, marketCap: 960000000 },
  { symbol: "WLT", name: "Wielton", market: "Polska", price: 7.4, change: -0.54, volume: 76000, marketCap: 445000000 },
  { symbol: "NEU", name: "Neuca", market: "Polska", price: 841, change: 0.31, volume: 5300, marketCap: 3600000000 },
  { symbol: "SNK", name: "Sanok Rubber", market: "Polska", price: 23.8, change: -0.71, volume: 32000, marketCap: 640000000 },
  { symbol: "DOM", name: "Dom Development", market: "Polska", price: 178.4, change: 0.85, volume: 41000, marketCap: 4550000000 },
  { symbol: "ECH", name: "Echo Investment", market: "Polska", price: 4.6, change: -0.22, volume: 290000, marketCap: 1900000000 },
  { symbol: "GTC", name: "GTC", market: "Polska", price: 5.7, change: 0.71, volume: 350000, marketCap: 3300000000 },
  { symbol: "MRC", name: "Mercator Medical", market: "Polska", price: 43.2, change: -1.33, volume: 65000, marketCap: 460000000 },
  { symbol: "PCR", name: "PCC Rokita", market: "Polska", price: 93.8, change: 0.43, volume: 21000, marketCap: 1870000000 },
  { symbol: "SNT", name: "Synektik", market: "Polska", price: 186.9, change: 2.74, volume: 84000, marketCap: 1590000000 },
  { symbol: "VOT", name: "Votum", market: "Polska", price: 38.6, change: -0.39, volume: 47000, marketCap: 463000000 },
  { symbol: "MLS", name: "ML System", market: "Polska", price: 31.9, change: 1.16, volume: 38000, marketCap: 210000000 },
]

function generateHistory(basePrice, change) {
  const points = []
  const direction = change >= 0 ? 1 : -1

  for (let index = 0; index < 48; index++) {
    const wave = Math.sin(index / 4) * basePrice * 0.015
    const trend = direction * index * basePrice * 0.0008
    const noise = Math.cos(index / 2.7) * basePrice * 0.006

    points.push({
      time: `${index + 1}`,
      price: Math.max(basePrice + wave + trend + noise, 0.01),
    })
  }

  return points
}

function StockMarket({ user, isLoggedIn, onLoginRequired }) {
  const [stocks, setStocks] = useState([])
  const [selectedStock, setSelectedStock] = useState(null)
  const {
    isFavorite,
    toggleFavorite,
    error: favoritesError,
  } = useFavorites("stock", user?.id)

  const [chartRange, setChartRange] = useState("1M")
  const [hoveredPoint, setHoveredPoint] = useState(null)

  useEffect(() => {
    const preparedStocks = STOCKS.map((stock) => ({
      ...stock,
      history: generateHistory(stock.price, stock.change),
    }))

    setStocks(preparedStocks)
    setSelectedStock(preparedStocks[0])
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
    if (!value) return "-"

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

    if (chartRange === "1D") return history.slice(-12)
    if (chartRange === "1W") return history.slice(-24)

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