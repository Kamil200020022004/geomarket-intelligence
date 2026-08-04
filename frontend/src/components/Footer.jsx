import { useState } from "react"

function Footer() {
  const [activePolicy, setActivePolicy] = useState(null)

  const policies = {
    privacy: {
      title: "Polityka prywatności",
      label: "Polityka prywatności",
      content: [
        "Platforma GeoMarket Intelligence przetwarza podstawowe dane użytkownika, takie jak adres e-mail, dane logowania oraz zapisane ulubione wykresy.",
        "Dane są wykorzystywane w celu obsługi konta użytkownika, personalizacji widoku, zapisywania ulubionych elementów oraz zapewnienia prawidłowego działania aplikacji.",
        "Dane użytkownika nie są wykorzystywane do podejmowania automatycznych decyzji inwestycyjnych ani przekazywane podmiotom trzecim bez uzasadnionej podstawy prawnej.",
      ],
    },
    terms: {
      title: "Regulamin korzystania z platformy",
      label: "Regulamin",
      content: [
        "Platforma ma charakter edukacyjny, analityczny i informacyjny. Jej celem jest prezentacja danych finansowych, makroekonomicznych i geopolitycznych w formie interaktywnych wizualizacji.",
        "Użytkownik zobowiązuje się korzystać z aplikacji zgodnie z jej przeznaczeniem oraz nie podejmować działań mogących zakłócić działanie systemu.",
        "Funkcje platformy obejmują prezentację danych rynkowych, analizę wydarzeń, chatbot AI, konto użytkownika oraz możliwość zapisywania wybranych wykresów do ulubionych.",
      ],
    },
    legal: {
      title: "Nota prawna",
      label: "Nota prawna",
      content: [
        "Prezentowane dane, wykresy, analizy oraz odpowiedzi generowane przez AI nie stanowią porady inwestycyjnej, rekomendacji finansowej ani zachęty do kupna lub sprzedaży instrumentów finansowych.",
        "Wyniki analiz mają charakter poglądowy i informacyjny. Użytkownik podejmuje ewentualne decyzje inwestycyjne wyłącznie na własną odpowiedzialność.",
        "Autorzy platformy nie ponoszą odpowiedzialności za skutki decyzji podjętych na podstawie informacji prezentowanych w aplikacji.",
      ],
    },
    rodo: {
      title: "Informacja RODO",
      label: "RODO",
      content: [
        "Użytkownik ma prawo dostępu do swoich danych, ich poprawiania, usunięcia, ograniczenia przetwarzania oraz przenoszenia danych.",
        "Zakres przetwarzanych danych jest ograniczony do informacji niezbędnych do działania konta użytkownika, logowania, odzyskiwania hasła oraz zapisywania ulubionych elementów.",
        "Dane osobowe są przetwarzane zgodnie z zasadami minimalizacji danych, ograniczenia celu, poufności oraz integralności.",
      ],
    },
  }

  const policy = activePolicy ? policies[activePolicy] : null

  return (
    <>
      <footer className="mt-12 border-t border-slate-800/80 bg-slate-950/70 px-8 py-8 text-sm text-slate-500">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="font-semibold text-slate-300">
              GeoMarket Intelligence
            </p>

            <p className="mt-2 max-w-3xl leading-6">
              Prezentowane dane, analizy i wizualizacje mają charakter informacyjny
              i edukacyjny. Nie stanowią porady inwestycyjnej ani rekomendacji
              kupna lub sprzedaży instrumentów finansowych.
            </p>

            <p className="mt-3 text-xs text-slate-600">
              © 2026 GeoMarket Intelligence. Wszelkie prawa zastrzeżone.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            {Object.entries(policies).map(([key, item]) => (
              <button
                key={key}
                onClick={() => setActivePolicy(key)}
                className="rounded-full border border-slate-800 px-4 py-2 transition hover:border-cyan-500/40 hover:bg-cyan-500/10 hover:text-cyan-400"
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </footer>

      {policy && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
          <div className="w-full max-w-2xl overflow-hidden rounded-3xl border border-cyan-500/20 bg-slate-950 shadow-2xl shadow-cyan-950/50">
            <div className="flex items-start justify-between border-b border-slate-800 bg-slate-900/80 px-6 py-5">
              <div>
                <p className="text-sm text-cyan-400">
                  Dokument prawny
                </p>

                <h3 className="mt-1 text-xl font-bold text-slate-100">
                  {policy.title}
                </h3>
              </div>

              <button
                onClick={() => setActivePolicy(null)}
                className="rounded-xl border border-slate-700 px-3 py-1 text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
              >
                X
              </button>
            </div>

            <div className="max-h-[65vh] overflow-y-auto px-6 py-6">
              <div className="space-y-4">
                {policy.content.map((paragraph, index) => (
                  <div
                    key={index}
                    className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4"
                  >
                    <p className="text-sm leading-6 text-slate-400">
                      {paragraph}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end border-t border-slate-800 bg-slate-900/80 px-6 py-4">
              <button
                onClick={() => setActivePolicy(null)}
                className="rounded-full bg-cyan-400 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300"
              >
                Zamknij
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default Footer