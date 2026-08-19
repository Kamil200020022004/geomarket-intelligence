import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { getStockNews } from "../api/aiApi"

function LatestNewsCard() {
  const [news, setNews] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    async function loadLatestNews() {
      try {
        const result = await getStockNews("AAPL")

        const latestNews = Array.isArray(result)
          ? result[0]
          : result.articles?.[0] || result.news?.[0] || result.data?.[0]

        setNews(latestNews)
      } catch (error) {
        console.error(error)
        setError(true)
      } finally {
        setIsLoading(false)
      }
    }

    loadLatestNews()
  }, [])

  if (isLoading) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <p className="text-sm text-cyan-400">Najnowszy news</p>
        <p className="mt-3 text-sm text-slate-400">Pobieranie najnowszego newsa...</p>
      </div>
    )
  }

  if (error || !news) {
    return (
      <div className="rounded-3xl border border-red-500/30 bg-slate-900/80 p-6">
        <p className="text-sm text-red-400">Najnowszy news</p>
        <p className="mt-3 text-sm text-slate-400">
          Nie udało się pobrać najnowszego newsa z backendu.
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-3xl border border-cyan-500/30 bg-slate-900/90 p-6 shadow-lg shadow-cyan-950/20">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="mb-3 inline-flex rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-400">
            Najnowszy news rynkowy
          </p>

          <h3 className="text-2xl font-bold">
            {news.title || "Brak tytułu"}
          </h3>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
            {news.description || news.summary || "Brak opisu newsa."}
          </p>
        </div>

        <Link
          to="/newsy"
          className="rounded-full bg-cyan-400 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
        >
          Zobacz analizę AI
        </Link>
      </div>

      <div className="mt-5 flex flex-wrap gap-3 text-xs text-slate-500">
        <span>
          Źródło: {news.source?.name || news.source || "brak danych"}
        </span>

        <span>
          Data: {news.publishedAt || news.date || "brak danych"}
        </span>
      </div>
    </div>
  )
}

export default LatestNewsCard