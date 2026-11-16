// Adapter API dla frontendu — przygotowany przez Sebastiana do podmiany pliku
// frontend/src/api/aiApi.js. Nazwy i sygnatury istniejących funkcji bez zmian.
//
// Zmiany względem obecnej wersji:
// - getTopCryptocurrencies(): backend zamiast bezpośrednio CoinGecko z przeglądarki,
// - funkcje z notowaniami (getStockData, getStockHistory, getStockChart, *FromInternet):
//   backend zamiast Yahoo z przeglądarki — jedno źródło cen w całym systemie,
// - nowe funkcje: getStocks(), getMacroData(), getDashboardMarkets().
//
// Wszystkie adresy względem VITE_API_URL (bramka Sebastiana, port 8000).

import { apiGet, apiPost } from "./apiClient"

// ----------------------------------------------------------------------------
// AI (pośredniczy bramka Sebastiana, analizy generuje serwis AI Patryka)
// ----------------------------------------------------------------------------

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

export async function getStockAnalysis(symbol) {
  return apiGet(`/stock/analyze/${encodeURIComponent(symbol)}`)
}

export async function getStockNews(symbol) {
  return apiGet(`/stock/news/${encodeURIComponent(symbol)}`)
}

export async function getNewsSentiment(symbol) {
  return apiGet(`/stock/news/${encodeURIComponent(symbol)}/sentiment`)
}

export async function getStockReport(symbol) {
  return apiGet(`/stock/report/${encodeURIComponent(symbol)}`)
}

// ----------------------------------------------------------------------------
// Dane rynkowe (potok strumieniowy Sebastiana)
// ----------------------------------------------------------------------------

// Zakładka Giełda: tablica obiektów { symbol, name, market, price, change,
// volume, marketCap, history: [{ time, price }] } — jak dotychczasowa tablica STOCKS.
export async function getStocks() {
  return apiGet("/api/stocks")
}

// Zakładka Makro: tablica obiektów { symbol, name, category, value, change,
// unit, description, history: [{ time, value }] } — jak dotychczasowa tablica MACRO_DATA.
export async function getMacroData() {
  return apiGet("/api/macro")
}

// Strona główna: kafelki { id, name, value, change, path } — jak mock/markets.json.
export async function getDashboardMarkets() {
  return apiGet("/api/dashboard/markets")
}

// Zakładka Krypto: ten sam format co CoinGecko /coins/markets (TOP 100).
export async function getTopCryptocurrencies() {
  return apiGet("/api/crypto/top")
}

async function findStock(symbol) {
  const stocks = await getStocks()
  const stock = stocks.find((item) => item.symbol === symbol)

  if (!stock) {
    throw new Error(`Brak danych dla symbolu ${symbol}`)
  }

  return stock
}

export async function getStockData(symbol) {
  return findStock(symbol)
}

export async function getStockHistory(symbol) {
  const stock = await findStock(symbol)
  return stock.history
}

export async function getStockChart(symbol) {
  return getStockHistory(symbol)
}

// Dawne funkcje pobierające z Yahoo w przeglądarce — zostawione dla zgodności nazw,
// teraz korzystają z backendu (parametry range i interval nie są już używane).
export async function getStockChartFromInternet(symbol) {
  return findStock(symbol)
}

export async function getStockQuoteFromInternet(symbol) {
  return findStock(symbol)
}

export async function getStockHistoryFromInternet(symbol) {
  return getStockHistory(symbol)
}
