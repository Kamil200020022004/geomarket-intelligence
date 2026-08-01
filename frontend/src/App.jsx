function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 px-8 py-5">
        <h1 className="text-2xl font-bold">
          GeoMarket Intelligence
        </h1>
        <p className="text-slate-400">
          Platforma analizy danych finansowych i geopolitycznych
        </p>
      </header>

      <main className="px-8 py-10">
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
          <h2 className="text-xl font-semibold">
            Dashboard
          </h2>
          <p className="mt-3 text-slate-400">
            Tutaj pojawią się wykresy, newsy, dane rynkowe i analiza AI.
          </p>

          <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-xl bg-slate-800 p-5">
              <p className="text-slate-400">Bitcoin</p>
              <p className="text-2xl font-bold">267 540 PLN</p>
            </div>

            <div className="rounded-xl bg-slate-800 p-5">
              <p className="text-slate-400">WIG20</p>
              <p className="text-2xl font-bold">2 320,41</p>
            </div>

            <div className="rounded-xl bg-slate-800 p-5">
              <p className="text-slate-400">EUR/PLN</p>
              <p className="text-2xl font-bold">4,3120</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App