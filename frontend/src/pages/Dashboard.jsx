import MarketCard from "../components/MarketCard"
import markets from "../mock/markets.json"

function Dashboard() {
  return (
    <main className="px-8 py-10">
      <section className="mb-8">
        <h2 className="text-3xl font-bold">
          Dashboard
        </h2>

        <p className="mt-2 text-slate-400">
          Najważniejsze dane finansowe, geopolityczne i analizy rynku w jednym miejscu.
        </p>
      </section>
            <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {markets.map((market) => (
                <MarketCard
                key={market.id}
                name={market.name}
                value={market.value}
                change={market.change}
                />
            ))}
</section>

      <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xl font-semibold">
            Wykres główny
          </h3>

          <div className="mt-6 flex h-64 items-center justify-center rounded-xl border border-dashed border-slate-700 text-slate-500">
            Tu będzie wykres Plotly
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-xl font-semibold">
            Najnowsze newsy
          </h3>

          <div className="mt-6 space-y-4">
            <div className="rounded-xl bg-slate-800 p-4">
              <p className="text-sm text-cyan-400">GEOPOLITYKA</p>
              <p className="mt-1 font-semibold">
                Nowe napięcia geopolityczne wpływają na rynek surowców.
              </p>
            </div>

            <div className="rounded-xl bg-slate-800 p-4">
              <p className="text-sm text-cyan-400">RYNKI</p>
              <p className="mt-1 font-semibold">
                Indeksy giełdowe reagują na najnowsze dane makroekonomiczne.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default Dashboard