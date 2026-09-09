import { useState } from "react"
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  Brain,
  CalendarDays,
  Database,
  FileText,
  Globe2,
  LineChart,
  Newspaper,
  ShieldAlert,
  TrendingDown,
  TrendingUp,
} from "lucide-react"

const EXTERNAL_NEWS = [
  {
    id: "external-1",
    title: "Globalne rynki reagują na oczekiwania dotyczące stóp procentowych",
    summary:
      "Inwestorzy analizują najnowsze sygnały z banków centralnych, ponieważ decyzje dotyczące stóp procentowych mogą wpływać na kursy walut, obligacje oraz rynek akcji.",
    sourceName: "Zewnętrzny serwis informacyjny",
    sourceUrl: "#",
    date: "Dzisiaj",
    category: "Makroekonomia",
    dataOrigin: "Źródła zewnętrzne",
    impact: "Średni",
    sentiment: "Neutralny",
    affectedMarkets: ["EUR/USD", "USD/PLN", "S&P 500", "Obligacje"],
    chartData: [44, 47, 45, 51, 54, 56, 55, 59],
    aiAnalysis:
      "AI wskazuje, że oczekiwania dotyczące stóp procentowych mogą wpływać na wycenę akcji, walut i obligacji. Utrzymanie wysokich stóp może ograniczać apetyt na ryzyko, natomiast oczekiwanie obniżek może poprawiać nastroje inwestorów.",
  },
  {
    id: "external-2",
    title: "Ceny ropy pozostają ważnym czynnikiem dla inflacji",
    summary:
      "Zmiany cen surowców energetycznych są obserwowane przez rynek, ponieważ mogą wpływać na koszty transportu, produkcji i oczekiwania inflacyjne.",
    sourceName: "Zewnętrzny serwis informacyjny",
    sourceUrl: "#",
    date: "Dzisiaj",
    category: "Surowce",
    dataOrigin: "Źródła zewnętrzne",
    impact: "Wysoki",
    sentiment: "Negatywny",
    affectedMarkets: ["Ropa", "Gaz", "CPI", "Sektor energetyczny"],
    chartData: [39, 42, 48, 53, 57, 61, 66, 70],
    aiAnalysis:
      "AI ocenia, że wzrost cen ropy może zwiększać presję inflacyjną oraz wpływać na koszty przedsiębiorstw. Najbardziej wrażliwe mogą być sektory transportu, przemysłu i energetyki.",
  },
  {
    id: "external-3",
    title: "Sektor technologiczny nadal przyciąga uwagę inwestorów",
    summary:
      "Największe spółki technologiczne pozostają istotnym elementem globalnych indeksów, szczególnie w kontekście rozwoju sztucznej inteligencji.",
    sourceName: "Zewnętrzny serwis informacyjny",
    sourceUrl: "#",
    date: "Wczoraj",
    category: "Giełda",
    dataOrigin: "Źródła zewnętrzne",
    impact: "Średni",
    sentiment: "Pozytywny",
    affectedMarkets: ["NASDAQ", "NVDA", "MSFT", "AMD"],
    chartData: [50, 53, 55, 58, 63, 61, 66, 72],
    aiAnalysis:
      "AI wskazuje, że pozytywne informacje z sektora technologicznego mogą wspierać indeksy wzrostowe. Jednocześnie wysoka koncentracja rynku oznacza większą wrażliwość na pojedyncze negatywne informacje.",
  },
  {
    id: "external-4",
    title: "Rynek kryptowalut reaguje na globalny apetyt na ryzyko",
    summary:
      "Kryptowaluty pozostają aktywami wrażliwymi na płynność, nastroje inwestorów, regulacje oraz zmiany oczekiwań dotyczących polityki pieniężnej.",
    sourceName: "Zewnętrzny serwis informacyjny",
    sourceUrl: "#",
    date: "Wczoraj",
    category: "Kryptowaluty",
    dataOrigin: "Źródła zewnętrzne",
    impact: "Średni",
    sentiment: "Neutralny",
    affectedMarkets: ["BTC", "ETH", "SOL", "NASDAQ"],
    chartData: [61, 58, 60, 57, 62, 65, 63, 67],
    aiAnalysis:
      "AI ocenia, że kryptowaluty mogą silnie reagować na zmianę apetytu na ryzyko. Lepsze nastroje na rynku akcji mogą wspierać aktywa cyfrowe, natomiast wzrost niepewności może prowadzić do odpływu kapitału.",
  },
]

const PROJECT_NEWS = [
  {
    id: "project-1",
    title: "Model danych wskazuje zależność między inflacją a stopami procentowymi",
    summary:
      "Warstwa danych projektu analizuje powiązanie między poziomem inflacji, decyzjami banków centralnych oraz reakcją rynku walutowego i giełdowego.",
    sourceName: "Warstwa danych projektu",
    sourceUrl: "#",
    date: "Dane projektowe",
    category: "Analiza danych",
    dataOrigin: "Moduł analityczny",
    impact: "Wysoki",
    sentiment: "Neutralny",
    affectedMarkets: ["CPI", "NBP", "FED", "Waluty"],
    chartData: [72, 69, 65, 62, 58, 54, 51, 49],
    aiAnalysis:
      "AI wskazuje, że spadek inflacji może zwiększać oczekiwania dotyczące łagodniejszej polityki pieniężnej. Może to wpływać na wyceny walut, obligacji oraz indeksów giełdowych.",
  },
  {
    id: "project-2",
    title: "Dane zespołu pokazują wpływ geopolityki na aktywa defensywne",
    summary:
      "Zagregowane dane pokazują, że w okresach podwyższonego ryzyka inwestorzy częściej zwracają uwagę na złoto, dolara oraz mniej ryzykowne klasy aktywów.",
    sourceName: "Warstwa danych projektu",
    sourceUrl: "#",
    date: "Dane projektowe",
    category: "Geopolityka",
    dataOrigin: "Moduł analityczny",
    impact: "Wysoki",
    sentiment: "Negatywny",
    affectedMarkets: ["Złoto", "USD", "Ropa", "Indeksy"],
    chartData: [46, 48, 52, 59, 64, 68, 72, 75],
    aiAnalysis:
      "AI ocenia, że wzrost napięć geopolitycznych może zwiększać popyt na aktywa defensywne. Jednocześnie może negatywnie wpływać na rynek akcji oraz zwiększać zmienność cen surowców.",
  },
  {
    id: "project-3",
    title: "Analiza zespołowa wskazuje możliwy wpływ kursów walut na spółki",
    summary:
      "Zmiany kursów EUR/PLN i USD/PLN mogą wpływać na wyniki przedsiębiorstw importujących towary, eksportujących produkty oraz rozliczających koszty w walutach obcych.",
    sourceName: "Warstwa danych projektu",
    sourceUrl: "#",
    date: "Dane projektowe",
    category: "Waluty",
    dataOrigin: "Moduł analityczny",
    impact: "Średni",
    sentiment: "Neutralny",
    affectedMarkets: ["EUR/PLN", "USD/PLN", "Eksporterzy", "Importerzy"],
    chartData: [55, 54, 56, 59, 57, 60, 62, 61],
    aiAnalysis:
      "AI wskazuje, że zmienność kursów walut może mieć różny wpływ na spółki w zależności od struktury kosztów i przychodów. Eksporterzy mogą korzystać na słabszej walucie krajowej, natomiast importerzy mogą odczuwać wyższe koszty.",
  },
]

const OLDER_AI_ANALYSES = [
  {
    id: 1,
    title: "Wpływ mocnego dolara na rynki wschodzące",
    date: "Starsza analiza",
    risk: "Średnie ryzyko",
    summary:
      "Silniejszy dolar może obciążać waluty rynków wschodzących, zwiększać koszty obsługi długu oraz wpływać na ceny surowców wycenianych w USD.",
    affectedMarkets: ["USD/PLN", "EUR/USD", "Złoto", "Rynki EM"],
    chartData: [48, 51, 55, 58, 62, 60, 64, 67],
  },
  {
    id: 2,
    title: "Presja inflacyjna a decyzje banków centralnych",
    date: "Starsza analiza",
    risk: "Wysokie ryzyko",
    summary:
      "Wyższa inflacja może opóźniać obniżki stóp procentowych i zwiększać zmienność na rynkach akcji, obligacji oraz walut.",
    affectedMarkets: ["CPI", "Obligacje", "S&P 500", "Waluty"],
    chartData: [70, 68, 66, 63, 61, 58, 56, 54],
  },
  {
    id: 3,
    title: "Rynek kryptowalut a zmiana apetytu na ryzyko",
    date: "Starsza analiza",
    risk: "Średnie ryzyko",
    summary:
      "Kryptowaluty silnie reagują na płynność, nastroje inwestorów oraz informacje regulacyjne. W okresach niepewności mogą pojawiać się gwałtowne wahania cen.",
    affectedMarkets: ["BTC", "ETH", "SOL", "NASDAQ"],
    chartData: [52, 49, 54, 50, 57, 61, 59, 63],
  },
]

function MiniChart({ data = [], type = "basic" }) {
  const minValue = Math.min(...data)
  const maxValue = Math.max(...data)

  const points = data.map((value, index) => {
    const x = (index / Math.max(data.length - 1, 1)) * 100
    const y =
      100 -
      ((value - minValue) / Math.max(maxValue - minValue, 1)) * 100

    return `${x},${y}`
  })

  const fillPoints = points.length > 0 ? `0,100 ${points.join(" ")} 100,100` : ""

  return (
    <div className="h-44 rounded-2xl border border-slate-800 bg-slate-900 p-4">
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        className="h-full w-full"
      >
        {[25, 50, 75].map((line) => (
          <line
            key={line}
            x1="0"
            y1={line}
            x2="100"
            y2={line}
            stroke="currentColor"
            strokeWidth="0.25"
            className="text-slate-700"
          />
        ))}

        {[25, 50, 75].map((line) => (
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

        {type === "advanced" && (
          <polygon
            points={fillPoints}
            fill="currentColor"
            className="text-blue-500/20"
          />
        )}

        <polyline
          points={points.join(" ")}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-blue-400"
        />

        {type === "advanced" && (
          <polyline
            points="0,68 14,63 28,66 42,55 56,51 70,47 84,43 100,39"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeDasharray="3 3"
            className="text-emerald-400"
          />
        )}

        {type === "advanced" && (
          <polyline
            points="0,40 14,44 28,47 42,53 56,58 70,61 84,65 100,70"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.4"
            strokeDasharray="3 3"
            className="text-red-400"
          />
        )}
      </svg>
    </div>
  )
}

function News() {
  const [selectedNews, setSelectedNews] = useState(EXTERNAL_NEWS[0])
  const [activeSection, setActiveSection] = useState("external")
  const [activeAnalysisIndex, setActiveAnalysisIndex] = useState(0)
  const [analysisChartMode, setAnalysisChartMode] = useState("basic")

  const activeNews =
    activeSection === "external" ? EXTERNAL_NEWS : PROJECT_NEWS

  const currentOlderAnalysis = OLDER_AI_ANALYSES[activeAnalysisIndex]

  const handlePreviousAnalysis = () => {
    setActiveAnalysisIndex((currentIndex) =>
      currentIndex === 0 ? OLDER_AI_ANALYSES.length - 1 : currentIndex - 1
    )
  }

  const handleNextAnalysis = () => {
    setActiveAnalysisIndex((currentIndex) =>
      currentIndex === OLDER_AI_ANALYSES.length - 1 ? 0 : currentIndex + 1
    )
  }

  const getImpactClass = (impact) => {
    if (impact === "Wysoki") return "text-red-400 bg-red-500/10 border-red-500/30"
    if (impact === "Średni") return "text-yellow-400 bg-yellow-500/10 border-yellow-500/30"
    return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
  }

  const getSentimentClass = (sentiment) => {
    if (sentiment === "Pozytywny") return "text-emerald-400"
    if (sentiment === "Negatywny") return "text-red-400"
    return "text-yellow-400"
  }

  const getSentimentIcon = (sentiment) => {
    if (sentiment === "Pozytywny") return <TrendingUp size={18} />
    if (sentiment === "Negatywny") return <TrendingDown size={18} />
    return <ShieldAlert size={18} />
  }

  return (
    <main className="px-8 py-8">
      <section className="relative overflow-hidden rounded-3xl border border-blue-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-blue-500/10 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl"></div>

        <div className="relative max-w-5xl">
          <p className="mb-4 inline-flex rounded-full border border-blue-500/40 bg-blue-500/10 px-4 py-1 text-sm text-blue-400">
            Market intelligence
          </p>

          <h2 className="text-4xl font-bold">
            Newsy i analiza AI
          </h2>

          <p className="mt-5 max-w-4xl text-lg leading-8 text-slate-300">
            Zakładka News prezentuje informacje rynkowe z dwóch warstw danych:
            zewnętrznych źródeł informacyjnych oraz modułu danych projektu.
            Widok umożliwia analizowanie wiadomości gospodarczych,
            geopolitycznych i finansowych oraz sprawdzanie ich potencjalnego
            wpływu na wybrane rynki.
          </p>

          <p className="mt-4 max-w-4xl leading-7 text-slate-400">
            Dane prezentowane w tej sekcji mają charakter informacyjny i
            edukacyjny. Platforma nie odpowiada za pełną aktualność,
            kompletność ani prawdziwość informacji pochodzących ze źródeł
            zewnętrznych. Użytkownik powinien każdorazowo weryfikować dane w
            oficjalnych źródłach.
          </p>
        </div>
      </section>

      <section className="mt-8 grid grid-cols-1 gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <div className="space-y-6">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm text-blue-400">
                  News data sources
                </p>

                <h3 className="mt-1 text-2xl font-bold">
                  Źródła informacji
                </h3>

                <p className="mt-2 text-sm text-slate-400">
                  Wybierz warstwę danych prezentowaną w sekcji wiadomości.
                </p>
              </div>

              <div className="flex rounded-full border border-slate-700 bg-slate-950 p-1">
                <button
                  onClick={() => {
                    setActiveSection("external")
                    setSelectedNews(EXTERNAL_NEWS[0])
                  }}
                  className={`rounded-full px-4 py-2 text-sm transition ${
                    activeSection === "external"
                      ? "bg-blue-400 text-slate-950"
                      : "text-slate-400 hover:text-blue-400"
                  }`}
                >
                  Źródła zewnętrzne
                </button>

                <button
                  onClick={() => {
                    setActiveSection("project")
                    setSelectedNews(PROJECT_NEWS[0])
                  }}
                  className={`rounded-full px-4 py-2 text-sm transition ${
                    activeSection === "project"
                      ? "bg-blue-400 text-slate-950"
                      : "text-slate-400 hover:text-blue-400"
                  }`}
                >
                  Warstwa danych projektu
                </button>
              </div>
            </div>

            <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
              <div className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-5">
                <div className="mb-3 flex items-center gap-3 text-blue-400">
                  <Globe2 size={22} />
                  <h4 className="font-semibold">
                    Źródła zewnętrzne
                  </h4>
                </div>

                <p className="text-sm leading-6 text-slate-400">
                  Sekcja prezentuje krótkie informacje pochodzące z zewnętrznych
                  serwisów informacyjnych. Widoczne są tytuły, opisy, daty,
                  kategorie, źródła oraz linki do artykułów.
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  Dane wymagają samodzielnej weryfikacji przez użytkownika.
                </p>
              </div>

              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
                <div className="mb-3 flex items-center gap-3 text-emerald-400">
                  <Database size={22} />
                  <h4 className="font-semibold">
                    Warstwa danych projektu
                  </h4>
                </div>

                <p className="text-sm leading-6 text-slate-400">
                  To część przeznaczona na dane przygotowane w projekcie:
                  zagregowane informacje, wyniki przetwarzania, powiązane
                  rynki, ocenę ryzyka oraz dane zasilające moduł AI.
                </p>

                <p className="mt-3 text-xs text-slate-500">
                  Struktura gotowa pod dane przygotowane przez Sebastiana.
                </p>
              </div>
            </div>

            <div className="mb-6 rounded-2xl border border-yellow-500/30 bg-yellow-500/10 p-5 text-sm leading-6 text-yellow-200">
              Informacje prezentowane w tej sekcji nie stanowią oficjalnego
              źródła danych. Platforma nie ponosi odpowiedzialności za ich
              pełną poprawność, aktualność ani kompletność.
            </div>

            <div className="space-y-4">
              {activeNews.map((item) => {
                const isSelected = selectedNews?.id === item.id

                return (
                  <article
                    key={item.id}
                    onClick={() => setSelectedNews(item)}
                    className={`cursor-pointer rounded-3xl border p-5 transition hover:border-blue-500/40 ${
                      isSelected
                        ? "border-blue-500/50 bg-blue-500/10"
                        : "border-slate-800 bg-slate-950/60"
                    }`}
                  >
                    <div className="mb-3 flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs text-blue-300">
                        {item.category}
                      </span>

                      <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">
                        {item.dataOrigin}
                      </span>

                      <span className={`rounded-full border px-3 py-1 text-xs ${getImpactClass(item.impact)}`}>
                        Wpływ: {item.impact}
                      </span>

                      <span className={`inline-flex items-center gap-1 text-xs ${getSentimentClass(item.sentiment)}`}>
                        {getSentimentIcon(item.sentiment)}
                        {item.sentiment}
                      </span>
                    </div>

                    <h4 className="text-xl font-bold text-white">
                      {item.title}
                    </h4>

                    <p className="mt-3 text-sm leading-6 text-slate-400">
                      {item.summary}
                    </p>

                    <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-slate-500">
                      <span className="inline-flex items-center gap-1">
                        <CalendarDays size={15} />
                        {item.date}
                      </span>

                      <span className="inline-flex items-center gap-1">
                        <Globe2 size={15} />
                        {item.sourceName}
                      </span>

                      {item.sourceUrl !== "#" && (
                        <a
                          href={item.sourceUrl}
                          target="_blank"
                          rel="noreferrer"
                          onClick={(event) => event.stopPropagation()}
                          className="text-blue-400 hover:text-blue-300"
                        >
                          Otwórz źródło
                        </a>
                      )}
                    </div>
                  </article>
                )
              })}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-violet-400">
                  Historical AI review
                </p>

                <h3 className="mt-1 text-2xl font-bold">
                  Starsze analizy AI
                </h3>

                <p className="mt-2 text-sm text-slate-400">
                  Sekcja pozwala przechodzić między wcześniejszymi analizami AI
                  oraz sprawdzać ich uproszczoną wizualizację na wykresie.
                </p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handlePreviousAnalysis}
                  className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-700 bg-slate-950 text-slate-400 transition hover:border-violet-400 hover:text-violet-400"
                >
                  <ArrowLeft size={18} />
                </button>

                <button
                  onClick={handleNextAnalysis}
                  className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-700 bg-slate-950 text-slate-400 transition hover:border-violet-400 hover:text-violet-400"
                >
                  <ArrowRight size={18} />
                </button>
              </div>
            </div>

            <div className="rounded-3xl border border-violet-500/20 bg-slate-950/70 p-6">
              <div className="mb-4 flex items-center gap-3 text-violet-400">
                <Brain size={24} />
                <h4 className="text-xl font-bold">
                  {currentOlderAnalysis.title}
                </h4>
              </div>

              <p className="text-sm text-violet-400">
                {currentOlderAnalysis.date} · {currentOlderAnalysis.risk}
              </p>

              <p className="mt-4 leading-7 text-slate-400">
                {currentOlderAnalysis.summary}
              </p>

              <div className="mt-5 flex flex-wrap gap-2">
                {currentOlderAnalysis.affectedMarkets.map((market) => (
                  <span
                    key={market}
                    className="rounded-full border border-violet-500/30 bg-violet-500/10 px-3 py-1 text-xs text-violet-300"
                  >
                    {market}
                  </span>
                ))}
              </div>

              <div className="mt-6">
                <div className="mb-3 flex items-center gap-3 text-violet-400">
                  <LineChart size={20} />
                  <h5 className="font-semibold">
                    Wykres starszej analizy
                  </h5>
                </div>

                <MiniChart data={currentOlderAnalysis.chartData} type="advanced" />
              </div>

              <div className="mt-5 text-xs text-slate-500">
                Analiza {activeAnalysisIndex + 1} z {OLDER_AI_ANALYSES.length}
              </div>
            </div>
          </div>
        </div>

        <aside className="sticky top-24 max-h-[calc(100vh-7rem)] self-start overflow-y-auto rounded-3xl border border-blue-500/30 bg-slate-900/90 p-6">
          {selectedNews && (
            <>
              <div>
                <p className="text-sm text-blue-400">
                  Latest AI analysis
                </p>

                <h3 className="mt-1 text-2xl font-bold">
                  Najnowsza analiza AI
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  Panel prezentuje interpretację wybranej informacji oraz jej
                  możliwe znaczenie dla rynku.
                </p>
              </div>

              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                <div className="mb-3 flex items-center gap-3 text-blue-400">
                  <Newspaper size={22} />
                  <h4 className="font-semibold">
                    Wybrana informacja
                  </h4>
                </div>

                <h5 className="text-lg font-bold text-white">
                  {selectedNews.title}
                </h5>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  {selectedNews.summary}
                </p>

                <div className="mt-4 text-xs text-slate-500">
                  Źródło: {selectedNews.sourceName}
                </div>
              </div>

              <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-500">Poziom wpływu</p>

                  <p className={`mt-2 font-bold ${getImpactClass(selectedNews.impact).split(" ")[0]}`}>
                    {selectedNews.impact}
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-500">Sentyment</p>

                  <p className={`mt-2 flex items-center gap-2 font-bold ${getSentimentClass(selectedNews.sentiment)}`}>
                    {getSentimentIcon(selectedNews.sentiment)}
                    {selectedNews.sentiment}
                  </p>
                </div>
              </div>

              <div className="mt-6 rounded-2xl border border-violet-500/20 bg-violet-500/5 p-5">
                <div className="mb-4 flex items-center gap-3 text-violet-400">
                  <Brain size={22} />
                  <h4 className="font-semibold">
                    Interpretacja AI
                  </h4>
                </div>

                <p className="text-sm leading-6 text-slate-300">
                  {selectedNews.aiAnalysis}
                </p>
              </div>

              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                <h4 className="font-semibold text-white">
                  Powiązane rynki
                </h4>

                <div className="mt-4 flex flex-wrap gap-2">
                  {selectedNews.affectedMarkets.map((market) => (
                    <span
                      key={market}
                      className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300"
                    >
                      {market}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                <div className="mb-4 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 text-emerald-400">
                    <LineChart size={22} />
                    <h4 className="font-semibold">
                      Wykres wpływu AI
                    </h4>
                  </div>

                  <div className="flex rounded-full border border-slate-700 bg-slate-900 p-1">
                    <button
                      onClick={() => setAnalysisChartMode("basic")}
                      className={`rounded-full px-3 py-1 text-xs transition ${
                        analysisChartMode === "basic"
                          ? "bg-emerald-400 text-slate-950"
                          : "text-slate-400 hover:text-emerald-400"
                      }`}
                    >
                      Podstawowy
                    </button>

                    <button
                      onClick={() => setAnalysisChartMode("advanced")}
                      className={`rounded-full px-3 py-1 text-xs transition ${
                        analysisChartMode === "advanced"
                          ? "bg-emerald-400 text-slate-950"
                          : "text-slate-400 hover:text-emerald-400"
                      }`}
                    >
                      Rozszerzony
                    </button>
                  </div>
                </div>

                <p className="mb-5 text-sm leading-6 text-slate-400">
                  Wersja podstawowa pokazuje uproszczony kierunek wpływu
                  informacji. Wersja rozszerzona prezentuje miejsce na porównanie
                  kilku reakcji rynkowych jednocześnie.
                </p>

                <MiniChart data={selectedNews.chartData} type={analysisChartMode} />
              </div>

              <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
                <div className="mb-4 flex items-center gap-3 text-orange-400">
                  <Activity size={22} />
                  <h4 className="font-semibold">
                    Rozszerzona analiza rynkowa
                  </h4>
                </div>

                <p className="text-sm leading-6 text-slate-400">
                  Po podłączeniu pełnych danych wykres może zestawiać wpływ
                  informacji na kilka obszarów: waluty, giełdę, surowce i
                  kryptowaluty. Może również pokazywać zmianę sentymentu,
                  poziom ryzyka oraz czas reakcji rynku.
                </p>

                <div className="mt-5 grid grid-cols-3 gap-3">
                  <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3">
                    <p className="text-xs text-slate-500">Giełda</p>
                    <p className="mt-1 text-sm font-semibold text-emerald-400">
                      +1.24%
                    </p>
                  </div>

                  <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3">
                    <p className="text-xs text-slate-500">Waluty</p>
                    <p className="mt-1 text-sm font-semibold text-red-400">
                      -0.42%
                    </p>
                  </div>

                  <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-3">
                    <p className="text-xs text-slate-500">Surowce</p>
                    <p className="mt-1 text-sm font-semibold text-yellow-400">
                      +2.11%
                    </p>
                  </div>
                </div>

                <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900 p-4">
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <FileText size={15} />
                    Miejsce na dane z modułu analitycznego i endpointów backendowych.
                  </div>
                </div>
              </div>
            </>
          )}
        </aside>
      </section>
    </main>
  )
}

export default News