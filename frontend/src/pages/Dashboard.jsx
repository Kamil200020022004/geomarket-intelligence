import { useEffect, useState } from "react"
import {
  AlertTriangle,
  Brain,
  CalendarDays,
  Clock,
  Globe2,
  RefreshCw,
  ShieldAlert,
} from "lucide-react"
import MarketCard from "../components/MarketCard"
import markets from "../mock/markets.json"
import { getStockAIImpact } from "../api/aiApi"

function Dashboard() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [aiImpact, setAiImpact] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    loadAIImpact()
  }, [])

  async function loadAIImpact() {
    try {
      setLoading(true)
      setError("")

      const data = await getStockAIImpact()

      setAiImpact(data)
    } catch (err) {
      console.error(err)
      setError("Nie udało się pobrać danych AI z backendu.")
    } finally {
      setLoading(false)
    }
  }

  const formattedTime = currentTime.toLocaleTimeString("pl-PL", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  })

  const formattedDate = currentTime.toLocaleDateString("pl-PL", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  })

  const affectedMarkets = aiImpact?.affectedMarkets
    ? aiImpact.affectedMarkets
        .split(",")
        .map((market) => market.trim())
        .filter(Boolean)
    : []

  const getRiskClass = (riskLevel) => {
    const value = riskLevel?.toLowerCase() || ""

    if (value.includes("wys")) {
      return "border-red-500/30 bg-red-500/10 text-red-400"
    }

    if (value.includes("śred") || value.includes("sred")) {
      return "border-amber-500/30 bg-amber-500/10 text-amber-400"
    }

    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
  }

  const getSentimentClass = (sentiment) => {
    const value = sentiment?.toLowerCase() || ""

    if (value.includes("neg")) {
      return "border-red-500/30 bg-red-500/10 text-red-400"
    }

    if (value.includes("poz")) {
      return "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
    }

    return "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
  }

  return (
    <main className="px-8 py-8">
      <section className="animate-fade-up rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-950 to-cyan-950/40 p-8 shadow-2xl shadow-cyan-950/20">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1.15fr_0.85fr]">
          <div>
            <p className="mb-3 inline-block rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-400">
              Financial & Geopolitical Intelligence
            </p>

            <h2 className="text-4xl font-bold leading-tight">
              GeoMarket Intelligence
            </h2>

            <p className="mt-4 max-w-xl text-slate-400">
              Platforma analizująca dane finansowe, makroekonomiczne i
              geopolityczne z wykorzystaniem modułów AI oraz danych rynkowych.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <span className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-300">
                Rynki finansowe
              </span>

              <span className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-300">
                Analiza AI
              </span>

              <span className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-300">
                Geopolityka
              </span>

              <span className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-300">
                Makroekonomia
              </span>
            </div>

            <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-2xl border border-cyan-500/20 bg-slate-950/70 p-5">
                <div className="mb-3 flex items-center gap-3 text-cyan-400">
                  <Clock size={22} />
                  <p className="text-sm text-slate-400">
                    Aktualny czas
                  </p>
                </div>

                <p className="text-3xl font-bold text-white">
                  {formattedTime}
                </p>

                <p className="mt-2 text-sm capitalize text-slate-500">
                  {formattedDate}
                </p>
              </div>

              <div className="rounded-2xl border border-violet-500/20 bg-slate-950/70 p-5">
                <div className="mb-3 flex items-center gap-3 text-violet-400">
                  <Brain size={22} />
                  <p className="text-sm text-slate-400">
                    Status AI
                  </p>
                </div>

                <p className="text-3xl font-bold text-white">
                  {loading ? "..." : error ? "OFF" : "ON"}
                </p>

                <p className="mt-2 text-sm text-slate-500">
                  Moduł analizy wydarzeń
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-cyan-500/20 bg-slate-950/70 p-6 shadow-2xl shadow-cyan-950/20 backdrop-blur">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm text-slate-400">
                  Panel AI
                </p>

                <h3 className="mt-1 text-xl font-bold">
                  Główna analiza AI
                </h3>
              </div>

              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-400 ring-1 ring-cyan-500/30">
                <Globe2 size={26} />
              </div>
            </div>

            {loading && (
              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-5 text-sm text-slate-400">
                Pobieranie aktualnej analizy AI...
              </div>
            )}

            {error && !loading && (
              <div className="mt-6 rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-sm leading-6 text-red-300">
                {error}
              </div>
            )}

            {!loading && !error && aiImpact && (
              <div className="mt-6 space-y-4">
                <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
                  <div className="mb-3 flex items-center gap-3 text-cyan-400">
                    <AlertTriangle size={22} />
                    <p className="text-sm font-semibold">
                      Aktualne wydarzenie
                    </p>
                  </div>

                  <h4 className="text-xl font-bold text-white">
                    {aiImpact.event || "Brak danych"}
                  </h4>

                  <p className="mt-4 text-sm leading-6 text-slate-400">
                    {aiImpact.summary || "Brak podsumowania."}
                  </p>
                </div>

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
                    <p className="text-sm text-slate-500">
                      Poziom ryzyka
                    </p>

                    <span
                      className={`mt-3 inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${getRiskClass(
                        aiImpact.riskLevel
                      )}`}
                    >
                      {aiImpact.riskLevel || "Brak danych"}
                    </span>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
                    <p className="text-sm text-slate-500">
                      Sentyment
                    </p>

                    <span
                      className={`mt-3 inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${getSentimentClass(
                        aiImpact.sentiment
                      )}`}
                    >
                      {aiImpact.sentiment || "Brak danych"}
                    </span>
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
                  <div className="mb-4 flex items-center gap-3 text-amber-400">
                    <ShieldAlert size={22} />
                    <p className="font-semibold">
                      Rynki objęte wpływem
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {affectedMarkets.length > 0 ? (
                      affectedMarkets.map((market) => (
                        <span
                          key={market}
                          className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-sm text-amber-300"
                        >
                          {market}
                        </span>
                      ))
                    ) : (
                      <p className="text-sm text-slate-500">
                        Brak danych o powiązanych rynkach.
                      </p>
                    )}
                  </div>
                </div>

                <button
                  onClick={loadAIImpact}
                  className="w-full rounded-2xl border border-cyan-500/30 bg-cyan-500/10 px-5 py-3 text-sm font-semibold text-cyan-300 transition hover:bg-cyan-500/20"
                >
                  Odśwież analizę AI
                </button>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="animate-fade-up mt-8 rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <div className="mb-5 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm text-slate-500">
              Market overview
            </p>

            <h3 className="text-2xl font-bold text-white">
              Szybki podgląd rynku
            </h3>
          </div>

          <div className="rounded-full border border-slate-700 bg-slate-950 px-4 py-2 text-xs text-slate-400">
            Sekcja informacyjna — osobna od analizy AI
          </div>
        </div>

        <p className="mb-6 max-w-4xl text-sm leading-7 text-slate-400">
          Poniższe kafelki pokazują wybrane instrumenty rynkowe i służą jako
          szybki podgląd sytuacji. Nie są częścią głównej analizy AI.
        </p>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {markets.map((market) => (
            <MarketCard
              key={market.id}
              name={market.name}
              value={market.value}
              change={market.change}
              path={market.path}
            />
          ))}
        </div>
      </section>

      <section className="animate-fade-up mt-8 rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <div className="mb-5 flex items-center gap-3 text-cyan-400">
          <CalendarDays size={24} />
          <h3 className="text-2xl font-bold text-white">
            Zakres platformy
          </h3>
        </div>

        <p className="max-w-4xl text-sm leading-7 text-slate-400">
          Platforma łączy widok rynku, wiadomości, dane makroekonomiczne,
          kryptowaluty oraz analizę AI. Strona główna prezentuje najważniejszy
          sygnał analityczny i osobny podgląd wybranych instrumentów.
        </p>
      </section>
    </main>
  )
}

export default Dashboard