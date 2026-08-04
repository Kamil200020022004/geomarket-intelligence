function Markets() {
  return (
    <main className="animate-fade-up px-8 py-8">
      <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-8">
        <p className="mb-3 inline-flex rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-400">
          Markets
        </p>

        <h2 className="text-4xl font-bold">
          Rynki
        </h2>

        <p className="mt-4 max-w-3xl text-slate-400">
          Zakładka przygotowana pod dane rynkowe: waluty, indeksy, surowce oraz instrumenty finansowe.
        </p>

        <div className="mt-8 flex h-72 items-center justify-center rounded-2xl border border-dashed border-slate-700 bg-slate-950/80 text-slate-500">
          Tu będzie widok rynków
        </div>
      </section>
    </main>
  )
}

export default Markets