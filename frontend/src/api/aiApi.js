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

export async function getStockNews(symbol) {
  return apiGet(`/stock/news/${symbol}`)
}

export async function getNewsSentiment(symbol) {
  return apiGet(`/stock/news/${symbol}/sentiment`)
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

export async function getStockQuoteFromInternet(symbol) {
  const url = encodeURIComponent(
    `https://stooq.pl/q/l/?s=${symbol}&f=sd2t2ohlcv&h&e=csv`
  )

  const response = await fetch(`https://api.allorigins.win/raw?url=${url}`)

  if (!response.ok) {
    throw new Error("Stock quote API error")
  }

  const text = await response.text()
  const rows = text.trim().split("\n")

  if (rows.length < 2) {
    throw new Error("No stock data")
  }

  const headers = rows[0].split(",")
  const values = rows[1].split(",")

  const data = Object.fromEntries(
    headers.map((header, index) => [header, values[index]])
  )

  const close = Number(data.Close)
  const open = Number(data.Open)
  const change = open ? ((close - open) / open) * 100 : 0

  return {
    symbol: data.Symbol || symbol,
    name: data.Symbol || symbol,
    price: close,
    change,
    volume: Number(data.Volume) || 0,
    marketCap: null,
    date: data.Date,
    time: data.Time,
  }
}

export async function getStockHistoryFromInternet(symbol) {
  const url = encodeURIComponent(
    `https://stooq.pl/q/d/l/?s=${symbol}&i=d`
  )

  const response = await fetch(`https://api.allorigins.win/raw?url=${url}`)

  if (!response.ok) {
    throw new Error("Stock history API error")
  }

  const text = await response.text()
  const rows = text.trim().split("\n")

  if (rows.length < 2) {
    return []
  }

  const headers = rows[0].split(",")

  return rows.slice(1).map((row) => {
    const values = row.split(",")

    const data = Object.fromEntries(
      headers.map((header, index) => [header, values[index]])
    )

    return {
      time: data.Date,
      price: Number(data.Close),
      volume: Number(data.Volume) || 0,
    }
  })
}

export async function getMacroRawData() {
  return apiGet("/stock/macro/raw")
}