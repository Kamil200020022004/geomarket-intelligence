import { useEffect, useState } from "react"
import {
  AlertTriangle,
  Brain,
  CalendarDays,
  Clock,
  ExternalLink,
  Globe2,
  Newspaper,
  Search,
  ShieldAlert,
} from "lucide-react"

const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8001").replace(/\/$/, "")

const NEWS_TOPICS = [
  { label: "Giełda", value: "stocks" },
  { label: "Makroekonomia", value: "macro" },
  { label: "Kryptowaluty", value: "crypto" },
  { label: "Geopolityka", value: "geopolitics" },
  { label: "Polska gospodarka", value: "poland" },
  { label: "Światowe rynki", value: "global" },
]

async function getApiData(path, signal) {
  const response = await fetch(`${API_URL}${path}`, {
    method: "GET",
    cache: "no-store",
    signal,
  })
  if (!response.ok) throw new Error(`Błąd API (HTTP ${response.status})`)
  return response.json()
}

function formatPublishedDate(value) {
  if (!value) return "Brak daty publikacji"
  const dt = new Date(value)
  return Number.isNaN(dt.getTime())
    ? value
    : dt.toLocaleString("pl-PL", { dateStyle: "medium", timeStyle: "short" })
}

const RISK_LABEL = { low: "Niskie", medium: "Średnie", high: "Wysokie" }
const SENTIMENT_LABEL = { positive: "Pozytywny", neutral: "Neutralny", negative: "Negatywny" }
const riskLabel = (value) => RISK_LABEL[value] || value || "Brak danych"
const sentimentLabel = (value) => SENTIMENT_LABEL[value] || value || "Brak danych"

function News() {
  const [currentTime, setCurrentTime] = useState(new Date())

  const [activeSection, setActiveSection] = useState("internet")
  const [selectedTopic, setSelectedTopic] = useState(NEWS_TOPICS[0])

  const [internetNews, setInternetNews] = useState([])
  const [selectedNews, setSelectedNews] = useState(null)

  const [aiImpact, setAiImpact] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const [loadingNews, setLoadingNews] = useState(false)
  const [loadingAI, setLoadingAI] = useState(false)

  const [errorNews, setErrorNews] = useState("")
  const [errorAI, setErrorAI] = useState("")

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    const category = encodeURIComponent(selectedTopic.value)
    const refresh = refreshKey > 0 ? "&refresh=true" : ""

    if (activeSection === "internet") {
      setLoadingNews(true)
      setErrorNews("")
      setInternetNews([])
      setSelectedNews(null)

      getApiData(`/news?category=${category}${refresh}`, controller.signal)
        .then((data) => {
          const items = Array.isArray(data?.articles) ? data.articles : []
          const normalized = items.map((article, index) => ({
            id: article.id || `${selectedTopic.value}-${index}`,
            title: article.title || "Brak tytułu",
            description: article.description || "",
            source: article.source || "Brak źródła",
            published: formatPublishedDate(article.publishedAt || article.published_at || article.published),
            url: article.url || "#",
          }))
          setInternetNews(normalized)
          setSelectedNews(normalized[0] || null)
        })
        .catch((error) => {
          if (error.name === "AbortError") return
          console.error("Błąd pobierania newsów:", error)
          setErrorNews(`Nie udało się pobrać wiadomości. ${error.message}`)
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoadingNews(false)
        })
    } else {
      setLoadingAI(true)
      setErrorAI("")
      setAiImpact(null)

      getApiData(`/news/analysis?category=${category}${refresh}`, controller.signal)
        .then((data) => {
          const analyses = Array.isArray(data?.analyses) ? data.analyses : []
          const first = analyses[0] || null
          setAiImpact(first ? {
            event: first.title || "Analiza wybranej kategorii",
            summary: first.summary || data.summary || "Brak podsumowania.",
            riskLevel: first.riskLevel || data.uncertainty,
            sentiment: first.sentiment || data.sentiment,
            affectedMarkets: Array.isArray(first.affectedMarkets)
              ? first.affectedMarkets.join(", ")
              : (first.affectedMarkets || ""),
            potentialImpact: first.potentialImpact || data.market_impact || "",
            analyses,
            aiUnavailable: Boolean(data.aiUnavailable),
          } : null)
          if (data.aiUnavailable) setErrorAI("Usługa AI jest chwilowo niedostępna. Ponów próbę później.")
          else if (!first) setErrorAI(data.summary || "Brak analiz dla wybranej kategorii.")
        })
        .catch((error) => {
          if (error.name === "AbortError") return
          console.error("Błąd pobierania analizy AI:", error)
          setErrorAI(`Nie udało się pobrać analizy AI. ${error.message}`)
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoadingAI(false)
        })
    }

    return () => controller.abort()
  }, [selectedTopic, activeSection, refreshKey])

  function refreshCurrentSection() {
    setRefreshKey((previous) => previous + 1)
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

    if (value === "high" || value.includes("wys")) {
      return "border-red-500/30 bg-red-500/10 text-red-400"
    }

    if (value === "medium" || value.includes("śred") || value.includes("sred")) {
      return "border-amber-500/30 bg-amber-500/10 text-amber-400"
    }

    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
  }

  const getSentimentClass = (sentiment) => {
    const value = sentiment?.toLowerCase() || ""

    if (value === "negative" || value.includes("neg")) {
      return "border-red-500/30 bg-red-500/10 text-red-400"
    }

    if (value === "positive" || value.includes("poz")) {
      return "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
    }

    return "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
  }

  return (
    <main className="px-8 py-8">
      <section className="relative overflow-hidden rounded-3xl border border-blue-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-blue-500/10 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl"></div>

        <div className="relative grid grid-cols-1 gap-8 xl:grid-cols-[1.35fr_0.65fr]">
          <div>
            <p className="mb-4 inline-flex rounded-full border border-blue-500/40 bg-blue-500/10 px-4 py-1 text-sm text-blue-400">
              Market intelligence
            </p>

            <h2 className="text-4xl font-bold">
              Newsy i analiza AI
            </h2>

            <p className="mt-5 max-w-4xl text-lg leading-8 text-slate-300">
              Sekcja prezentuje wiadomości rynkowe oraz analizę AI dotyczącą
              wpływu wydarzeń na giełdę, makroekonomię, waluty, surowce,
              kryptowaluty i wybrane aktywa finansowe.
            </p>

            <p className="mt-4 max-w-4xl leading-7 text-slate-400">
              Informacje mają charakter edukacyjny i informacyjny. Platforma
              nie odpowiada za pełną poprawność, aktualność ani kompletność
              danych pochodzących z zewnętrznych serwisów.
            </p>
          </div>

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
        </div>
      </section>

      <section className="mt-8 grid grid-cols-1 gap-6 xl:grid-cols-[1.35fr_0.85fr]">
        <div className="space-y-6">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm text-blue-400">
                  News data source
                </p>

                <h3 className="mt-1 text-2xl font-bold">
                  Źródło danych
                </h3>

                <p className="mt-2 text-sm text-slate-400">
                  Przeglądaj wiadomości albo zbiorczą analizę AI wybranego obszaru.
                </p>
              </div>

              <div className="flex rounded-full border border-slate-700 bg-slate-950 p-1">
                <button
                  onClick={() => setActiveSection("internet")}
                  className={`rounded-full px-4 py-2 text-sm transition ${
                    activeSection === "internet"
                      ? "bg-blue-400 text-slate-950"
                      : "text-slate-400 hover:text-blue-400"
                  }`}
                >
                  Wiadomości internetowe
                </button>

                <button
                  onClick={() => setActiveSection("ai")}
                  className={`rounded-full px-4 py-2 text-sm transition ${
                    activeSection === "ai"
                      ? "bg-blue-400 text-slate-950"
                      : "text-slate-400 hover:text-blue-400"
                  }`}
                >
                  Analiza AI kategorii
                </button>
              </div>
            </div>

                <div className="mb-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                  <div className="mb-4 flex items-center gap-3 text-blue-400">
                    <Search size={21} />

                    <div>
                      <h4 className="font-semibold">
                        Kategoria tematyczna
                      </h4>

                      <p className="mt-1 text-sm text-slate-400">
                        Wybierz kategorię wiadomości i analizy AI: giełda, makroekonomia,
                        kryptowaluty, geopolityka, polska gospodarka albo
                        światowe rynki.
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {NEWS_TOPICS.map((topic) => (
                      <button
                        key={topic.label}
                        onClick={() => setSelectedTopic(topic)}
                        className={`rounded-full border px-4 py-2 text-sm transition ${
                          selectedTopic.label === topic.label
                            ? "border-blue-400 bg-blue-400 text-slate-950"
                            : "border-slate-700 bg-slate-900 text-slate-400 hover:border-blue-400 hover:text-blue-400"
                        }`}
                      >
                        {topic.label}
                      </button>
                    ))}
                  </div>
                </div>

            {activeSection === "internet" && (
              <>
                {loadingNews && (
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5 text-sm text-slate-400">
                    Pobieranie wiadomości...
                  </div>
                )}

                {errorNews && !loadingNews && (
                  <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-sm leading-6 text-red-300">
                    {errorNews}
                  </div>
                )}

                {!loadingNews && !errorNews && internetNews.length === 0 && (
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5 text-sm text-slate-400">
                    Brak wiadomości dla wybranego tematu.
                  </div>
                )}

                {!loadingNews && !errorNews && internetNews.length > 0 && (
                  <div className="space-y-3">
                    {internetNews.map((item) => {
                      const isSelected = selectedNews?.id === item.id

                      return (
                        <article
                          key={item.id}
                          onClick={() => setSelectedNews(item)}
                          className={`cursor-pointer rounded-2xl border p-4 transition hover:border-blue-500/40 ${
                            isSelected
                              ? "border-blue-500/50 bg-blue-500/10"
                              : "border-slate-800 bg-slate-950/60"
                          }`}
                        >
                          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                            <div>
                              <h4 className="text-base font-semibold leading-6 text-white">
                                {item.title}
                              </h4>

                              <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-500">
                                <span className="inline-flex items-center gap-1">
                                  <CalendarDays size={14} />
                                  {item.published}
                                </span>

                                <span className="inline-flex items-center gap-1">
                                  <Globe2 size={14} />
                                  {item.source}
                                </span>
                              </div>
                            </div>

                            {item.url !== "#" && (
                              <a
                                href={item.url}
                                target="_blank"
                                rel="noreferrer"
                                onClick={(event) => event.stopPropagation()}
                                className="inline-flex shrink-0 items-center gap-1 rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-2 text-xs text-blue-300 transition hover:bg-blue-500/20"
                              >
                                Źródło
                                <ExternalLink size={13} />
                              </a>
                            )}
                          </div>
                        </article>
                      )
                    })}
                  </div>
                )}
              </>
            )}

            {activeSection === "ai" && (
              <>
                <div className="mb-5 rounded-2xl border border-cyan-500/20 bg-cyan-500/5 px-5 py-4 text-sm leading-6 text-slate-300">
                  Analiza AI obejmuje najnowsze dostępne wiadomości z całej kategorii
                  <span className="font-semibold text-white"> {selectedTopic.label}</span>.
                  Nie dotyczy wyłącznie pojedynczego artykułu zaznaczonego na liście.
                </div>
                {loadingAI && (
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5 text-sm text-slate-400">
                    Pobieranie analizy AI...
                  </div>
                )}

                {errorAI && !loadingAI && (
                  <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-sm leading-6 text-red-300">
                    {errorAI}
                  </div>
                )}

                {!loadingAI && !errorAI && aiImpact && (
                  <article className="rounded-3xl border border-blue-500/40 bg-blue-500/10 p-6">
                    <div className="mb-4 flex items-center gap-3 text-blue-400">
                      <Brain size={24} />

                      <h4 className="text-xl font-bold text-white">
                        Analiza AI — {selectedTopic.label}
                      </h4>
                    </div>

                    <div className="space-y-5">
                      <div>
                        <p className="text-sm text-slate-500">
                          Wydarzenie
                        </p>

                        <p className="mt-1 text-lg font-semibold text-white">
                          {aiImpact.event || "Brak danych"}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-slate-500">
                          Podsumowanie
                        </p>

                        <p className="mt-2 leading-7 text-slate-300">
                          {aiImpact.summary || "Brak podsumowania."}
                        </p>
                      </div>

                      {aiImpact.potentialImpact && (
                        <div>
                          <p className="text-sm text-slate-500">Potencjalny wpływ na rynki</p>
                          <p className="mt-2 leading-7 text-slate-300">{aiImpact.potentialImpact}</p>
                        </div>
                      )}

                      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                          <p className="text-sm text-slate-500">
                            Poziom ryzyka
                          </p>

                          <span
                            className={`mt-3 inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${getRiskClass(
                              aiImpact.riskLevel
                            )}`}
                          >
                            {riskLabel(aiImpact.riskLevel)}
                          </span>
                        </div>

                        <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                          <p className="text-sm text-slate-500">
                            Sentyment
                          </p>

                          <span
                            className={`mt-3 inline-flex rounded-full border px-4 py-2 text-sm font-semibold ${getSentimentClass(
                              aiImpact.sentiment
                            )}`}
                          >
                            {sentimentLabel(aiImpact.sentiment)}
                          </span>
                        </div>
                      </div>

                      <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                        <p className="mb-3 text-sm text-slate-500">
                          Rynki objęte wpływem
                        </p>

                        <div className="flex flex-wrap gap-2">
                          {affectedMarkets.length > 0 ? (
                            affectedMarkets.map((market) => (
                              <span
                                key={market}
                                className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-sm text-cyan-300"
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
                    </div>
                  </article>
                )}

                {!loadingAI && !errorAI && aiImpact?.analyses?.length > 1 && (
                  <div className="mt-4 space-y-3">
                    {aiImpact.analyses.slice(1).map((analysis) => (
                      <article key={analysis.id} className="rounded-2xl border border-blue-500/30 bg-slate-950/70 p-5">
                        <h4 className="font-semibold text-white">{analysis.title}</h4>
                        <p className="mt-2 text-sm leading-6 text-slate-300">{analysis.summary}</p>
                        {analysis.potentialImpact && (
                          <p className="mt-2 text-sm text-slate-400">Możliwy wpływ: {analysis.potentialImpact}</p>
                        )}
                      </article>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <aside className="sticky top-24 max-h-[calc(100vh-7rem)] self-start overflow-y-auto rounded-3xl border border-blue-500/30 bg-slate-900/90 p-6">
          {activeSection === "internet" && (
            <>
              <div>
                <p className="text-sm text-blue-400">
                  News details
                </p>

                <h3 className="mt-1 text-2xl font-bold">
                  Wybrana wiadomość
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Krótkie informacje o wybranym artykule oraz link do źródła.
                </p>
              </div>

              {selectedNews ? (
                <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                  <div className="mb-3 flex items-center gap-3 text-blue-400">
                    <Newspaper size={22} />

                    <h4 className="font-semibold">
                      Szczegóły
                    </h4>
                  </div>

                  <h5 className="text-lg font-bold leading-7 text-white">
                    {selectedNews.title}
                  </h5>

                  <div className="mt-4 space-y-3 text-sm text-slate-400">
                    <p>
                      <span className="text-slate-500">Temat:</span>{" "}
                      {selectedTopic.label}
                    </p>

                    <p>
                      <span className="text-slate-500">Źródło:</span>{" "}
                      {selectedNews.source}
                    </p>

                    <p>
                      <span className="text-slate-500">Publikacja:</span>{" "}
                      {selectedNews.published}
                    </p>
                    {selectedNews.description && (
                      <p className="leading-6 text-slate-300">{selectedNews.description}</p>
                    )}
                  </div>

                  {selectedNews.url !== "#" && (
                    <a
                      href={selectedNews.url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-5 inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm text-blue-300 transition hover:bg-blue-500/20"
                    >
                      Przejdź do artykułu
                      <ExternalLink size={15} />
                    </a>
                  )}
                </div>
              ) : (
                <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5 text-sm text-slate-400">
                  Wybierz wiadomość z listy.
                </div>
              )}
            </>
          )}

          {activeSection === "ai" && (
            <>
              <div>
                <p className="text-sm text-blue-400">
                  AI analysis
                </p>

                <h3 className="mt-1 text-2xl font-bold">
                  Szczegóły analizy
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Zbiorcza analiza wiadomości z kategorii {selectedTopic.label}:
                  podsumowanie, poziom ryzyka, sentyment oraz powiązane rynki.
                  Nie jest to analiza jednego wybranego artykułu.
                </p>
              </div>

              {aiImpact ? (
                <div className="mt-6 space-y-5">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                    <div className="mb-3 flex items-center gap-3 text-amber-400">
                      <AlertTriangle size={22} />

                      <h4 className="font-semibold">
                        Wydarzenie
                      </h4>
                    </div>

                    <p className="text-lg font-bold text-white">
                      {aiImpact.event || "Brak danych"}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                    <div className="mb-3 flex items-center gap-3 text-red-400">
                      <ShieldAlert size={22} />

                      <h4 className="font-semibold">
                        Ryzyko i sentyment
                      </h4>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <span
                        className={`rounded-full border px-4 py-2 text-sm font-semibold ${getRiskClass(
                          aiImpact.riskLevel
                        )}`}
                      >
                        Ryzyko: {riskLabel(aiImpact.riskLevel)}
                      </span>

                      <span
                        className={`rounded-full border px-4 py-2 text-sm font-semibold ${getSentimentClass(
                          aiImpact.sentiment
                        )}`}
                      >
                        Sentyment: {sentimentLabel(aiImpact.sentiment)}
                      </span>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                    <h4 className="mb-3 font-semibold text-white">
                      Podsumowanie
                    </h4>

                    <p className="text-sm leading-7 text-slate-400">
                      {aiImpact.summary || "Brak podsumowania."}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5 text-sm text-slate-400">
                  Brak danych do wyświetlenia.
                </div>
              )}
            </>
          )}

          <button
            onClick={refreshCurrentSection}
            className="mt-6 w-full rounded-2xl border border-blue-500/30 bg-blue-500/10 px-5 py-3 text-sm font-semibold text-blue-300 transition hover:bg-blue-500/20"
          >
            Odśwież dane
          </button>
        </aside>
      </section>
    </main>
  )
}

export default News