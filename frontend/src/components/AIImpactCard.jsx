import aiImpact from "../mock/aiImpact.json"

function AIImpactCard() {
  return (
    <div className="rounded-2xl border border-cyan-500/30 bg-slate-900 p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold">
          Analiza AI wpływu wydarzeń
        </h3>

        <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-sm text-cyan-400">
          AI Insight
        </span>
      </div>

      <div className="mt-5 rounded-xl bg-slate-800 p-4">
        <p className="text-sm text-slate-400">Wydarzenie</p>
        <p className="mt-1 font-semibold">
          {aiImpact.event}
        </p>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl bg-slate-800 p-4">
          <p className="text-sm text-slate-400">Możliwy wpływ</p>
          <p className="mt-1 font-semibold text-amber-400">
            {aiImpact.affectedMarkets}
          </p>
        </div>

        <div className="rounded-xl bg-slate-800 p-4">
          <p className="text-sm text-slate-400">Ryzyko</p>
          <p className="mt-1 font-semibold text-red-400">
            {aiImpact.riskLevel}
          </p>
        </div>

        <div className="rounded-xl bg-slate-800 p-4">
          <p className="text-sm text-slate-400">Sentyment</p>
          <p className="mt-1 font-semibold text-red-400">
            {aiImpact.sentiment}
          </p>
        </div>
      </div>

      {aiImpact.showChart && (
        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-700 bg-slate-950 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">Wykres bazowy</p>
                <p className="text-sm text-slate-400">
                  Aktualny trend wskazanego instrumentu
                </p>
              </div>

              <span className="text-sm text-slate-500">
                Dane historyczne
              </span>
            </div>

            <div className="mt-4 flex h-56 items-center justify-center rounded-lg border border-dashed border-slate-700 text-slate-500">
              Tu będzie wykres aktualny
            </div>
          </div>

          <div className="rounded-xl border border-cyan-500/30 bg-slate-950 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">Scenariusz AI</p>
                <p className="text-sm text-slate-400">
                  Możliwa zmiana po wydarzeniu
                </p>
              </div>

              <span className="text-sm text-cyan-400">
                Prognoza AI
              </span>
            </div>

            <div className="mt-4 flex h-56 items-center justify-center rounded-lg border border-dashed border-cyan-500/40 text-slate-500">
              Tu będzie wykres scenariusza AI
            </div>
          </div>
        </div>
      )}

      <p className="mt-4 text-sm text-slate-400">
        {aiImpact.summary}
      </p>

      <p className="mt-4 text-xs text-slate-500">
        To nie jest porada inwestycyjna. Analiza ma charakter informacyjny.
      </p>
    </div>
  )
}

export default AIImpactCard