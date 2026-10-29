import { apiGet, apiPost } from "./apiClient"

export async function sendChatMessage({ message, history = [], symbol }) {
  return apiPost("/chat", {
    message,
    history,
    symbol,
  })
}

export async function getStockAIImpact() {
  return apiGet("/stock/ai-impact")
}

export async function getMacroRawData() {
  return apiGet("/stock/macro/raw")
}

export async function getMacroAnalysis() {
  return apiGet("/stock/macro/analysis")
}

export async function getStockData(symbol) {
  return apiGet(`/stock/${symbol}`)
}

export async function getStockAnalysis(symbol) {
  return apiGet(`/stock/analyze/${symbol}`)
}

export async function getStockHistory(symbol) {
  return apiGet(`/stock/history/${symbol}`)
}

export async function getStockChart(symbol) {
  return apiGet(`/stock/chart/${symbol}`)
}

export async function getStockNews(symbol) {
  return apiGet(`/stock/news/${symbol}`)
}

export async function getNewsSentiment(symbol) {
  return apiGet(`/stock/news/${symbol}/sentiment`)
}

export async function getStockReport(symbol) {
  return apiGet(`/stock/report/${symbol}`)
}

export async function getTopCryptocurrencies() {
  const response = await fetch(
    "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=true&price_change_percentage=1h,24h,7d"
  )

  if (!response.ok) {
    throw new Error("Crypto API error")
  }

  return response.json()
}

export async function getStockChartFromInternet(
  symbol,
  range = "1mo",
  interval = "1d"
) {
  const response = await fetch(
    `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}?range=${range}&interval=${interval}`
  )

  if (!response.ok) {
    throw new Error("Stock internet API error")
  }

  const data = await response.json()
  const result = data.chart?.result?.[0]

  if (!result) {
    throw new Error("No stock data")
  }

  const quote = result.indicators?.quote?.[0]
  const timestamps = result.timestamp || []
  const meta = result.meta || {}

  const history = timestamps
    .map((timestamp, index) => ({
      time: new Date(timestamp * 1000).toLocaleDateString("pl-PL"),
      price: quote?.close?.[index],
      volume: quote?.volume?.[index] || 0,
    }))
    .filter((item) => item.price !== null && item.price !== undefined)

  const firstPrice = history[0]?.price || meta.regularMarketPrice || 0
  const lastPrice =
    history[history.length - 1]?.price || meta.regularMarketPrice || 0

  const change = firstPrice ? ((lastPrice - firstPrice) / firstPrice) * 100 : 0

  return {
    symbol,
    name: meta.longName || meta.shortName || symbol,
    price: meta.regularMarketPrice || lastPrice,
    change,
    volume: history[history.length - 1]?.volume || 0,
    currency: meta.currency || "USD",
    exchangeName: meta.exchangeName || "",
    history,
  }
}

export async function getStockQuoteFromInternet(symbol) {
  return getStockChartFromInternet(symbol, "1mo", "1d")
}

export async function getStockHistoryFromInternet(symbol) {
  const data = await getStockChartFromInternet(symbol, "1mo", "1d")
  return data.history
}