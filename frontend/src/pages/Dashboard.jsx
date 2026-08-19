import MarketCard from "../components/MarketCard"
import AIImpactCard from "../components/AIImpactCard"
import markets from "../mock/markets.json"


function Dashboard() {
  return (
    <main className="px-8 py-8">
      <section className="animate-fade-up rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-950 to-cyan-950/40 p-8 shadow-2xl shadow-cyan-950/20">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div>
            <p className="mb-3 inline-block rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-400">
              Financial & Geopolitical Intelligence
            </p>

            <h2 className="text-4xl font-bold leading-tight">
              GeoMarket Intelligence
            </h2>

            <p className="mt-4 max-w-xl text-slate-400">
              Platforma analizująca dane finansowe, makroekonomiczne i geopolityczne
              z wykorzystaniem modułów AI oraz interaktywnych wizualizacji.
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

            <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <p className="text-sm text-slate-500">Źródła danych</p>
                <p className="mt-1 text-2xl font-bold text-cyan-400">API</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <p className="text-sm text-slate-500">AI engine</p>
                <p className="mt-1 text-2xl font-bold text-emerald-400">ON</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <p className="text-sm text-slate-500">Rynek</p>
                <p className="mt-1 text-2xl font-bold text-amber-400">LIVE</p>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <p className="text-sm text-slate-500">Alerty</p>
                <p className="mt-1 text-2xl font-bold text-red-400">3</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-cyan-500/20 bg-slate-950/70 p-6 shadow-2xl shadow-cyan-950/20 backdrop-blur">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">
                  Panel sytuacyjny
                </p>

                <h3 className="mt-1 text-xl font-bold">
                  Status rynku
                </h3>
              </div>

              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/10 text-2xl ring-1 ring-cyan-500/30">
                🌐
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 gap-3">
              <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 text-xl ring-1 ring-amber-500/20">
                      📈
                    </div>

                    <div>
                      <p className="font-semibold text-slate-200">
                        Zmienność rynku
                      </p>

                      <p className="text-sm text-slate-500">
                        aktywność cenowa
                      </p>
                    </div>
                  </div>

                  <span className="rounded-full bg-amber-500/10 px-3 py-1 text-sm text-amber-400">
                    Podwyższona
                  </span>
                </div>

                <div className="mt-4 h-2 rounded-full bg-slate-800">
                  <div className="h-2 w-3/4 rounded-full bg-amber-400"></div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500/10 text-xl ring-1 ring-red-500/20">
                      ⚠️
                    </div>

                    <div>
                      <p className="font-semibold text-slate-200">
                        Ryzyko geopolityczne
                      </p>

                      <p className="text-sm text-slate-500">
                        wpływ wydarzeń globalnych
                      </p>
                    </div>
                  </div>

                  <span className="rounded-full bg-red-500/10 px-3 py-1 text-sm text-red-400">
                    Wysokie
                  </span>
                </div>

                <div className="mt-4 h-2 rounded-full bg-slate-800">
                  <div className="h-2 w-5/6 rounded-full bg-red-400"></div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 text-xl ring-1 ring-cyan-500/20">
                      🧠
                    </div>

                    <div>
                      <p className="font-semibold text-slate-200">
                        Sentyment AI
                      </p>

                      <p className="text-sm text-slate-500">
                        ocena nastroju rynku
                      </p>
                    </div>
                  </div>

                  <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-sm text-cyan-400">
                    Neutralny
                  </span>
                </div>

                <div className="mt-4 h-2 rounded-full bg-slate-800">
                  <div className="h-2 w-1/2 rounded-full bg-cyan-400"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="animate-fade-up mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
        {markets.map((market) => (
          <MarketCard
            key={market.id}
            name={market.name}
            value={market.value}
            change={market.change}
            path={market.path}
          />
        ))}
      </section>

      <section className="animate-fade-up mt-8">
        <AIImpactCard />
      </section>

      
    </main>
  )
}

export default Dashboard