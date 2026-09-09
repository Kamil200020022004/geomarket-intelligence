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

export async function getInternetNews() {
  const response = await fetch(
    "https://api.freenewsapi.ai/api/search?query=finance%20markets%20economy%20geopolitics&language=en&page_size=8"
  )

  if (!response.ok) {
    throw new Error("Internet news API error")
  }

  const data = await response.json()
  const articles = data.articles || data.data || data.results || []

  return articles.map((article, index) => ({
    id: `internet-${index + 1}`,
    title: article.title || "Brak tytułu",
    summary:
      article.description ||
      article.summary ||
      article.snippet ||
      "Brak krótkiego opisu artykułu.",
    sourceName:
      article.source?.name ||
      article.source ||
      article.publisher ||
      "External source",
    sourceUrl: article.url || article.link || article.source_url || "#",
    date:
      article.published_at || article.publishedAt || article.date
        ? new Date(
            article.published_at || article.publishedAt || article.date
          ).toLocaleString("pl-PL")
        : "Brak daty",
    category: "Źródło zewnętrzne",
    dataOrigin: "Informacje zewnętrzne",
    impact: "Średni",
    sentiment: "Neutralny",
    affectedMarkets: ["Giełda", "Waluty", "Surowce"],
    aiAnalysis:
      "Miejsce na analizę AI wygenerowaną na podstawie treści newsa, danych rynkowych oraz informacji dostarczonych przez warstwę danych projektu.",
  }))
}

export async function getMacroRawData() {
  return apiGet("/stock/macro/raw")
}