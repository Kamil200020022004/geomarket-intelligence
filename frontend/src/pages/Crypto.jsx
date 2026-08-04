function Crypto() {
  return (
    <main className="animate-fade-up px-8 py-8">
      <section className="rounded-3xl border border-orange-500/20 bg-gradient-to-br from-slate-900 via-slate-950 to-orange-950/30 p-8 shadow-2xl shadow-orange-950/20">
        <p className="mb-3 inline-flex rounded-full border border-orange-500/30 bg-orange-500/10 px-4 py-1 text-sm text-orange-400">
          Crypto market
        </p>

        <h2 className="text-4xl font-bold">
          Kryptowaluty
        </h2>

        <p className="mt-4 max-w-3xl leading-6 text-slate-400">
          Zakładka prezentująca najważniejsze dane dotyczące rynku kryptowalut:
          Bitcoin, Ethereum, kapitalizację rynku, wolumen, zmienność oraz sentyment.
        </p>
      </section>

      <section className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-500">Bitcoin</p>
          <p className="mt-2 text-2xl font-bold text-orange-400">267 540 PLN</p>
          <p className="mt-1 text-sm text-emerald-400">+2.45%</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-500">Ethereum</p>
          <p className="mt-2 text-2xl font-bold">14 820 PLN</p>
          <p className="mt-1 text-sm text-emerald-400">+1.18%</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-500">Market cap</p>
          <p className="mt-2 text-2xl font-bold">8.42T PLN</p>
          <p className="mt-1 text-sm text-slate-500">rynek krypto</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-500">Sentyment</p>
          <p className="mt-2 text-2xl font-bold text-amber-400">Neutralny</p>
          <p className="mt-1 text-sm text-slate-500">ocena rynku</p>
        </div>
      </section>

      <section className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 lg:col-span-2">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h3 className="text-xl font-semibold">
                Wizualizacja rynku kryptowalut
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Miejsce na wykres BTC, ETH lub całkowitej kapitalizacji rynku krypto.
              </p>
            </div>

            <button className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-orange-400 hover:text-orange-400">
              ☆ Dodaj do ulubionych
            </button>
          </div>

          <div className="mt-6 flex h-72 items-center justify-center rounded-2xl border border-dashed border-slate-700 bg-slate-950/80 text-slate-500">
            Tu będzie wykres kryptowalut
          </div>
        </div>

        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-xl font-semibold">
            Sygnały krypto
          </h3>

          <div className="mt-6 space-y-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
              <p className="text-sm text-orange-400">ZMIENNOŚĆ</p>
              <p className="mt-1 font-semibold">
                Rynek kryptowalut pozostaje podatny na nagłe ruchy cen.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
              <p className="text-sm text-orange-400">WOLUMEN</p>
              <p className="mt-1 font-semibold">
                Podwyższony wolumen może wskazywać na większą aktywność inwestorów.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
              <p className="text-sm text-orange-400">ŹRÓDŁO DANYCH</p>
              <p className="mt-1 text-sm text-slate-400">
                Dane przygotowane w strukturze mock API. Później można je podmienić na backend lub zewnętrzne API.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

export default Crypto