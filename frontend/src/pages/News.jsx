import { useEffect, useState } from "react"
import {
  AlertTriangle,
  Brain,
  CalendarDays,
  Clock,
  ExternalLink,
  Globe2,
  Newspaper,
  RefreshCw,
  Search,
  ShieldAlert,
} from "lucide-react"
import { getStockAIImpact, getStockNews } from "../api/aiApi"

const NEWS_TOPICS = [
  { label: "Giełda", value: "WIG20.WA" },
  { label: "Makroekonomia", value: "EURPLN=X" },
  { label: "Kryptowaluty", value: "BTC-USD" },
  { label: "Geopolityka", value: "GC=F" },
  { label: "Polska gospodarka", value: "EURPLN=X" },
  { label: "Światowe rynki", value: "AAPL" },
]

function News() {
  const [currentTime, setCurrentTime] = useState(new Date())

  const [activeSection, setActiveSection] = useState("internet")
  const [selectedTopic, setSelectedTopic] = useState(NEWS_TOPICS[0])

  const [internetNews, setInternetNews] = useState([])
  const [selectedNews, setSelectedNews] = useState(null)

  const [aiImpact, setAiImpact] = useState(null)

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
    loadInternetNews(selectedTopic.value)
  }, [selectedTopic])

  useEffect(() => {
    loadAIImpact()
  }, [])

  async function loadInternetNews(symbol) {
    try {
      setLoadingNews(true)
      setErrorNews("")

      const newsData = await getStockNews(symbol)
      const articles = newsData?.articles || []

      const normalizedArticles = articles.map((article, index) => ({
        id: `${symbol}-${index}`,
        title: article.title || "Brak tytułu",
        source: article.source || "Brak źródła",
        published: article.published || "Brak daty publikacji",
        url: article.url || "#",
      }))

      setInternetNews(normalizedArticles)
      setSelectedNews(normalizedArticles[0] || null)
    } catch (err) {
      console.error(err)
      setInternetNews([])
      setSelectedNews(null)
      setErrorNews("Nie udało się pobrać wiadomości.")
    } finally {
      setLoadingNews(false)
    }
  }

  async function loadAIImpact() {
    try {
      setLoadingAI(true)
      setErrorAI("")

      const data = await getStockAIImpact()

      setAiImpact(data)
    } catch (err) {
      console.error(err)
      setErrorAI("Nie udało się pobrać analizy AI.")
    } finally {
      setLoadingAI(false)
    }
  }

  function refreshCurrentSection() {
    if (activeSection === "internet") {
      loadInternetNews(selectedTopic.value)
      return
    }

    loadAIImpact()
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
                  Przełącz między wiadomościami rynkowymi a analizą AI.
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
                  Analiza AI
                </button>
              </div>
            </div>

            {activeSection === "internet" && (
              <>
                <div className="mb-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                  <div className="mb-4 flex items-center gap-3 text-blue-400">
                    <Search size={21} />

                    <div>
                      <h4 className="font-semibold">
                        Temat wiadomości
                      </h4>

                      <p className="mt-1 text-sm text-slate-400">
                        Wybierz obszar wiadomości: giełda, makroekonomia,
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
                        Aktualna analiza AI
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
                            {aiImpact.riskLevel || "Brak danych"}
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
                            {aiImpact.sentiment || "Brak danych"}
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
                  Panel pokazuje wydarzenie, poziom ryzyka, sentyment oraz
                  powiązane rynki.
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
                        Ryzyko: {aiImpact.riskLevel || "Brak danych"}
                      </span>

                      <span
                        className={`rounded-full border px-4 py-2 text-sm font-semibold ${getSentimentClass(
                          aiImpact.sentiment
                        )}`}
                      >
                        Sentyment: {aiImpact.sentiment || "Brak danych"}
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