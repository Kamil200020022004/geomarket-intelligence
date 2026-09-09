import {
  Brain,
  ChartCandlestick,
  Database,
  Globe2,
  LineChart,
  Newspaper,
  ShieldCheck,
  Star,
  TrendingUp,
  Users,
} from "lucide-react"

function AboutProject() {
  return (
    <main className="px-8 py-8">
      <section className="relative overflow-hidden rounded-3xl border border-cyan-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 h-72 w-72 rounded-full bg-violet-500/10 blur-3xl"></div>

        <div className="relative max-w-5xl">
          <p className="mb-4 inline-flex rounded-full border border-cyan-500/40 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-400">
            Engineering Project
          </p>

          <h2 className="text-4xl font-bold">
            O projekcie
          </h2>

          <p className="mt-5 max-w-4xl text-lg leading-8 text-slate-300">
            GeoMarket Intelligence to kompletna platforma analityczna łącząca
            informacje finansowe, dane rynkowe, wiadomości gospodarcze oraz
            analizę wpływu wydarzeń geopolitycznych na wybrane instrumenty.
            System działa jako nowoczesna aplikacja webowa, która w jednym
            miejscu prezentuje dane z obszaru kryptowalut, giełdy,
            makroekonomii oraz newsów, a dodatkowo wspiera użytkownika poprzez
            moduły analityczne oparte na sztucznej inteligencji.
          </p>

          <p className="mt-4 max-w-4xl leading-7 text-slate-400">
            Głównym założeniem projektu jest stworzenie przejrzystego narzędzia,
            które nie tylko pokazuje dane, ale również pomaga zrozumieć ich
            znaczenie. Platforma wspiera użytkownika w szybkim rozpoznaniu
            sytuacji rynkowej, obserwacji zmian cen, analizie trendów oraz
            interpretacji informacji pojawiających się w otoczeniu ekonomicznym
            i geopolitycznym.
          </p>
        </div>
      </section>

      <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-400">
            <Globe2 size={26} />
          </div>

          <h3 className="text-xl font-bold">
            Cel platformy
          </h3>

          <p className="mt-3 leading-7 text-slate-400">
            Celem aplikacji jest zebranie wielu kategorii danych w jednym,
            spójnym środowisku. Użytkownik może obserwować rynki, porównywać
            instrumenty, analizować newsy oraz sprawdzać potencjalny wpływ
            wydarzeń na gospodarkę i aktywa finansowe.
          </p>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-400">
            <Brain size={26} />
          </div>

          <h3 className="text-xl font-bold">
            Warstwa AI
          </h3>

          <p className="mt-3 leading-7 text-slate-400">
            Moduł sztucznej inteligencji wspiera interpretację danych. AI
            analizuje wydarzenia, wskazuje możliwy wpływ na rynek, ocenia
            poziom ryzyka oraz pomaga użytkownikowi szybciej zrozumieć,
            dlaczego dana informacja może być istotna.
          </p>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-400">
            <Database size={26} />
          </div>

          <h3 className="text-xl font-bold">
            Dane i integracje
          </h3>

          <p className="mt-3 leading-7 text-slate-400">
            Platforma korzysta z przygotowanych struktur danych oraz endpointów
            backendowych, które dostarczają informacje wykorzystywane w
            poszczególnych modułach aplikacji. Dane są prezentowane w formie
            tabel, kart, wykresów oraz paneli szczegółowych, dzięki czemu
            użytkownik otrzymuje czytelny obraz sytuacji rynkowej.
          </p>
        </div>
      </section>

      <section className="mt-8 rounded-3xl border border-slate-800 bg-slate-900/80 p-8">
        <div className="mb-8">
          <p className="text-sm text-cyan-400">
            Functional scope
          </p>

          <h3 className="mt-2 text-3xl font-bold">
            Główne funkcjonalności platformy
          </h3>

          <p className="mt-4 max-w-4xl leading-7 text-slate-400">
            Platforma została podzielona na kilka logicznych modułów, dzięki
            czemu użytkownik może szybko przechodzić między różnymi obszarami
            rynku. Każda zakładka pełni inną rolę, ale wszystkie razem tworzą
            jeden spójny system wspierający analizę danych finansowych,
            gospodarczych i geopolitycznych.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
          <div className="rounded-2xl border border-orange-500/20 bg-slate-950/70 p-5">
            <div className="mb-4 flex items-center gap-3 text-orange-400">
              <TrendingUp size={22} />
              <h4 className="font-semibold">Kryptowaluty</h4>
            </div>

            <p className="text-sm leading-6 text-slate-400">
              Zakładka prezentuje ranking największych kryptowalut, aktualne
              ceny, zmiany procentowe, wolumen, kapitalizację oraz wykresy.
              Użytkownik może analizować wybrane aktywo i dodawać je do
              ulubionych po zalogowaniu.
            </p>
          </div>

          <div className="rounded-2xl border border-emerald-500/20 bg-slate-950/70 p-5">
            <div className="mb-4 flex items-center gap-3 text-emerald-400">
              <ChartCandlestick size={22} />
              <h4 className="font-semibold">Giełda</h4>
            </div>

            <p className="text-sm leading-6 text-slate-400">
              Moduł giełdowy zawiera listę spółek polskich i zagranicznych.
              Dla każdego instrumentu widoczna jest cena, zmiana procentowa,
              wolumen, kapitalizacja oraz panel szczegółowy z wykresem. Dane są
              dostarczane do aplikacji w przygotowanej strukturze i prezentowane
              użytkownikowi w spójnej formie.
            </p>
          </div>

          <div className="rounded-2xl border border-violet-500/20 bg-slate-950/70 p-5">
            <div className="mb-4 flex items-center gap-3 text-violet-400">
              <LineChart size={22} />
              <h4 className="font-semibold">Makro</h4>
            </div>

            <p className="text-sm leading-6 text-slate-400">
              Sekcja makroekonomiczna obejmuje kursy walut, inflację, stopy
              procentowe, PKB oraz wybrane surowce. Moduł pokazuje szerszy obraz
              gospodarki i pozwala analizować dane, które mogą wpływać na
              sytuację rynkową oraz decyzje inwestorów.
            </p>
          </div>

          <div className="rounded-2xl border border-blue-500/20 bg-slate-950/70 p-5">
            <div className="mb-4 flex items-center gap-3 text-blue-400">
              <Newspaper size={22} />
              <h4 className="font-semibold">Newsy</h4>
            </div>

            <p className="text-sm leading-6 text-slate-400">
              Zakładka News prezentuje najważniejsze informacje gospodarcze,
              rynkowe i geopolityczne. To tutaj znajdują się szczegółowe
              wiadomości oraz analiza AI pokazująca możliwy wpływ wydarzeń na
              rynek.
            </p>
          </div>

          <div className="rounded-2xl border border-yellow-500/20 bg-slate-950/70 p-5">
            <div className="mb-4 flex items-center gap-3 text-yellow-400">
              <Star size={22} />
              <h4 className="font-semibold">Ulubione</h4>
            </div>

            <p className="text-sm leading-6 text-slate-400">
              Funkcja ulubionych jest dostępna dla zalogowanych użytkowników.
              Pozwala zapisywać wybrane kryptowaluty i instrumenty giełdowe,
              aby szybciej wracać do obserwowanych aktywów.
            </p>
          </div>

          <div className="rounded-2xl border border-cyan-500/20 bg-slate-950/70 p-5">
            <div className="mb-4 flex items-center gap-3 text-cyan-400">
              <Brain size={22} />
              <h4 className="font-semibold">Asystent AI</h4>
            </div>

            <p className="text-sm leading-6 text-slate-400">
              Asystent AI jest dostępny jako pływający panel czatu w prawym
              dolnym rogu aplikacji. Nie posiada osobnej zakładki, dzięki czemu
              użytkownik może korzystać z niego z każdego miejsca platformy.
            </p>
          </div>
        </div>
      </section>

      <section className="mt-8 grid grid-cols-1 gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-8">
          <p className="text-sm text-emerald-400">
            Project assumptions
          </p>

          <h3 className="mt-2 text-3xl font-bold">
            Najważniejsze założenia projektowe
          </h3>

          <div className="mt-6 space-y-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
              <h4 className="font-semibold text-white">
                Przejrzysty interfejs użytkownika
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Aplikacja została zaprojektowana jako nowoczesny dashboard z
                czytelnymi kartami, tabelami, wykresami i panelem bocznym.
                Użytkownik szybko rozumie, gdzie znajduje się dana
                funkcjonalność i jak interpretować prezentowane informacje.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
              <h4 className="font-semibold text-white">
                Jasny podział zakładek
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Kryptowaluty znajdują się w osobnej sekcji, giełda obejmuje
                spółki i instrumenty rynku kapitałowego, natomiast waluty,
                inflacja, stopy procentowe, PKB i surowce zostały umieszczone
                w module Makro.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
              <h4 className="font-semibold text-white">
                AI bez osobnej zakładki
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Zgodnie z założeniem projektu asystent AI nie jest osobnym
                widokiem w menu. Działa jako pływające okno dostępne na każdej
                stronie, natomiast specjalne karty analizy AI pojawiają się
                przede wszystkim na Dashboardzie oraz w zakładce News.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
              <h4 className="font-semibold text-white">
                Kompletna struktura aplikacji
              </h4>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Aplikacja posiada przygotowaną strukturę widoków, komponentów,
                komunikacji z backendem oraz prezentacji danych. Poszczególne
                moduły zostały połączone w jeden spójny system, który umożliwia
                analizę kryptowalut, giełdy, danych makroekonomicznych, newsów
                oraz komunikację z asystentem AI.
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-8">
          <p className="text-sm text-violet-400">
            Project team
          </p>

          <h3 className="mt-2 text-3xl font-bold">
            Zespół projektowy
          </h3>

          <p className="mt-4 leading-7 text-slate-400">
            Projekt jest realizowany zespołowo, a zakres prac został podzielony
            między osoby odpowiedzialne za różne części systemu. Dzięki temu
            platforma łączy interfejs użytkownika, backend, dane oraz sztuczną
            inteligencję w jedną spójną aplikację.
          </p>

          <div className="mt-6 space-y-4">
            <div className="rounded-2xl border border-cyan-500/20 bg-slate-950/70 p-5">
              <div className="mb-3 flex items-center gap-3 text-cyan-400">
                <Users size={21} />
                <h4 className="font-semibold">Kamil</h4>
              </div>

              <p className="text-sm leading-6 text-slate-400">
                Odpowiada za część frontendową aplikacji, przygotowanie
                interfejsu użytkownika, układ zakładek, widoki platformy,
                integrację elementów wizualnych oraz ogólną strukturę działania
                serwisu od strony użytkownika.
              </p>
            </div>

            <div className="rounded-2xl border border-violet-500/20 bg-slate-950/70 p-5">
              <div className="mb-3 flex items-center gap-3 text-violet-400">
                <Brain size={21} />
                <h4 className="font-semibold">Patryk</h4>
              </div>

              <p className="text-sm leading-6 text-slate-400">
                Odpowiada za obszar backendu oraz integrację modułów AI.
                Przygotowuje logikę komunikacji z modelem, endpointy API oraz
                mechanizmy umożliwiające analizę danych i obsługę zapytań
                użytkownika.
              </p>
            </div>

            <div className="rounded-2xl border border-emerald-500/20 bg-slate-950/70 p-5">
              <div className="mb-3 flex items-center gap-3 text-emerald-400">
                <Database size={21} />
                <h4 className="font-semibold">Sebastian</h4>
              </div>

              <p className="text-sm leading-6 text-slate-400">
                Odpowiada za przygotowanie danych, przetwarzanie informacji oraz
                dostarczenie struktur wykorzystywanych w zakładkach Giełda,
                Makro, News i analizach rynkowych.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8 rounded-3xl border border-slate-800 bg-slate-900/80 p-8">
        <div className="grid grid-cols-1 gap-8 xl:grid-cols-[0.9fr_1.1fr]">
          <div>
            <p className="text-sm text-cyan-400">
              System architecture
            </p>

            <h3 className="mt-2 text-3xl font-bold">
              Ogólna architektura rozwiązania
            </h3>

            <p className="mt-4 leading-7 text-slate-400">
              Platforma została zaprojektowana jako aplikacja webowa składająca
              się z warstwy frontendowej, backendowej oraz analitycznej.
              Frontend odpowiada za prezentację danych i interakcję użytkownika
              z aplikacją, backend obsługuje logikę, komunikację z modelem AI
              oraz źródła danych, a warstwa danych zasila system informacjami
              wykorzystywanymi w poszczególnych modułach.
            </p>

            <p className="mt-4 leading-7 text-slate-400">
              Taki podział zapewnia przejrzystość działania systemu oraz
              umożliwia sprawne zarządzanie danymi, logiką aplikacji i warstwą
              prezentacji. Frontend odpowiada za intuicyjny interfejs
              użytkownika, backend za obsługę danych i komunikację z AI, a
              warstwa analityczna pozwala przedstawiać informacje w sposób
              zrozumiały i uporządkowany.
            </p>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-6">
            <div className="space-y-4">
              <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5">
                <h4 className="font-semibold text-cyan-400">
                  Frontend
                </h4>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  React, Vite, Tailwind, routing, widoki użytkownika, tabele,
                  wykresy, panel logowania, ulubione oraz pływający czat AI.
                </p>
              </div>

              <div className="rounded-2xl border border-violet-500/20 bg-violet-500/5 p-5">
                <h4 className="font-semibold text-violet-400">
                  Backend
                </h4>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  FastAPI, endpointy, komunikacja z modelem AI, obsługa zapytań
                  użytkownika oraz dostarczanie danych do modułów aplikacji.
                </p>
              </div>

              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
                <h4 className="font-semibold text-emerald-400">
                  Dane
                </h4>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Dane rynkowe, dane makroekonomiczne, newsy oraz struktury JSON
                  są dostarczane do aplikacji i wykorzystywane przez
                  poszczególne moduły platformy. Dzięki temu informacje mogą być
                  prezentowane w formie tabel, wykresów, kart i paneli
                  szczegółowych.
                </p>
              </div>

              <div className="rounded-2xl border border-orange-500/20 bg-orange-500/5 p-5">
                <h4 className="font-semibold text-orange-400">
                  AI
                </h4>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Analiza wydarzeń, ocena ryzyka, interpretacja wpływu newsów,
                  podsumowania oraz interaktywny asystent dostępny z każdego
                  miejsca aplikacji.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8 rounded-3xl border border-cyan-500/30 bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/40 p-8">
        <div className="grid grid-cols-1 gap-8 xl:grid-cols-[1fr_0.9fr]">
          <div>
            <p className="text-sm text-cyan-400">
              Final result
            </p>

            <h3 className="mt-2 text-3xl font-bold">
              Efekt końcowy projektu
            </h3>

            <p className="mt-4 leading-7 text-slate-300">
              GeoMarket Intelligence stanowi kompletne centrum analityczne,
              które pozwala obserwować rynek, analizować dane, zapisywać
              interesujące aktywa, przeglądać newsy oraz korzystać ze wsparcia
              asystenta AI podczas interpretacji informacji finansowych i
              geopolitycznych.
            </p>

            <p className="mt-4 leading-7 text-slate-400">
              Platforma łączy kilka obszarów analitycznych w jednym środowisku:
              kryptowaluty, giełdę, makroekonomię, wiadomości oraz moduły AI.
              Dzięki temu użytkownik otrzymuje narzędzie, które prezentuje dane
              w czytelnej formie i ułatwia ocenę sytuacji rynkowej.
            </p>
          </div>

          <div className="rounded-3xl border border-slate-700 bg-slate-950/70 p-6">
            <div className="mb-5 flex items-center gap-3 text-cyan-400">
              <ShieldCheck size={24} />
              <h4 className="text-xl font-bold">
                Charakter informacyjny
              </h4>
            </div>

            <p className="leading-7 text-slate-400">
              Platforma ma charakter edukacyjny i informacyjny. Prezentowane
              dane, wykresy, analizy i komunikaty AI nie stanowią porady
              inwestycyjnej ani rekomendacji kupna lub sprzedaży instrumentów
              finansowych. Celem systemu jest przedstawienie działania
              kompletnej aplikacji analitycznej, która integruje dane,
              wizualizacje oraz analizę kontekstową w ramach projektu
              inżynierskiego.
            </p>
          </div>
        </div>
      </section>
    </main>
  )
}

export default AboutProject