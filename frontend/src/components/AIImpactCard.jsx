import { useEffect, useState } from "react"
import { getStockAIImpact } from "../api/aiApi"

function AIImpactCard() {
  const [aiImpact, setAiImpact] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    async function loadAIImpact() {
      try {
        const result = await getStockAIImpact()
        setAiImpact(result)
      } catch (error) {
        console.error(error)
        setError(true)
      } finally {
        setIsLoading(false)
      }
    }

    loadAIImpact()
  }, [])

  if (isLoading) {
    return (
      <div className="relative overflow-hidden rounded-3xl border border-cyan-500/30 bg-slate-900/90 p-6 backdrop-blur">
        <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-cyan-500/10 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-blue-500/10 blur-3xl"></div>

        <div className="relative">
          <p className="mb-3 inline-flex rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-400">
            AI Market Impact Engine
          </p>

          <h3 className="text-2xl font-bold">
            Analiza AI wpływu wydarzeń
          </h3>

          <p className="mt-4 text-sm text-slate-400">
            AI analizuje dane z backendu...
          </p>
        </div>
      </div>
    )
  }

  if (error || !aiImpact) {
    return (
      <div className="relative overflow-hidden rounded-3xl border border-red-500/30 bg-slate-900/90 p-6 backdrop-blur">
        <div className="relative">
          <p className="mb-3 inline-flex rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1 text-sm text-red-400">
            AI Market Impact Engine
          </p>

          <h3 className="text-2xl font-bold">
            Analiza AI wpływu wydarzeń
          </h3>

          <p className="mt-4 text-sm text-slate-400">
            Nie udało się pobrać analizy AI z backendu. Sprawdź, czy backend działa pod adresem http://127.0.0.1:8000.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative overflow-hidden rounded-3xl border border-cyan-500/30 bg-slate-900/90 p-6 backdrop-blur">
      <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-cyan-500/10 blur-3xl"></div>
      <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-blue-500/10 blur-3xl"></div>

      <div className="relative">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="mb-3 inline-flex rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1 text-sm text-cyan-400">
              AI Market Impact Engine
            </p>

            <h3 className="text-2xl font-bold">
              Analiza AI wpływu wydarzeń
            </h3>

            <p className="mt-2 max-w-2xl text-sm text-slate-400">
              Moduł AI analizuje wydarzenie, określa możliwy wpływ na rynki i decyduje,
              czy potrzebna jest dodatkowa wizualizacja scenariusza.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-4">
            <p className="text-sm text-slate-500">Status analizy</p>
            <p className="mt-1 font-semibold text-emerald-400">
              Przetworzone przez AI
            </p>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/80 p-5">
          <p className="text-sm text-slate-500">Wykryte wydarzenie</p>
          <p className="mt-2 text-lg font-semibold">
            {aiImpact.event}
          </p>
        </div>

        <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
            <p className="text-sm text-slate-500">Możliwy wpływ</p>
            <p className="mt-2 font-semibold text-amber-400">
              {aiImpact.affectedMarkets}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
            <p className="text-sm text-slate-500">Poziom ryzyka</p>
            <p className="mt-2 font-semibold text-red-400">
              {aiImpact.riskLevel}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
            <p className="text-sm text-slate-500">Sentyment</p>
            <p className="mt-2 font-semibold text-red-400">
              {aiImpact.sentiment}
            </p>
          </div>
        </div>

        <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
          <div className="flex items-start gap-4">
            <div className="mt-1 flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400 ring-1 ring-cyan-500/30">
              AI
            </div>

            <div>
              <p className="font-semibold">
                Wniosek z analizy
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                {aiImpact.summary}
              </p>
            </div>
          </div>
        </div>

        {aiImpact.showChart ? (
          <div className="mt-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h4 className="font-semibold">
                  Wizualizacja scenariusza
                </h4>

                <p className="text-sm text-slate-500">
                  AI uznało, że dla tej analizy warto pokazać porównanie danych.
                </p>
              </div>

              <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-sm text-cyan-400">
                Wykres wymagany
              </span>
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <div className="rounded-2xl border border-slate-800 bg-slate-950/80 p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">Wariant bazowy</p>
                    <p className="text-sm text-slate-500">
                      Aktualny trend instrumentu
                    </p>
                  </div>

                  <span className="text-sm text-slate-500">Historical</span>
                </div>

                <div className="mt-5 flex h-56 items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/60 text-slate-500">
                  Tu będzie wykres bazowy
                </div>
              </div>

              <div className="rounded-2xl border border-cyan-500/30 bg-slate-950/80 p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">Scenariusz AI</p>
                    <p className="text-sm text-slate-500">
                      Możliwa zmiana po wydarzeniu
                    </p>
                  </div>

                  <span className="text-sm text-cyan-400">AI forecast</span>
                </div>

                <div className="mt-5 flex h-56 items-center justify-center rounded-xl border border-dashed border-cyan-500/40 bg-cyan-500/5 text-slate-500">
                  Tu będzie wykres scenariusza AI
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/70 p-5">
            <p className="font-semibold text-slate-200">
              Brak wykresu dla tej analizy
            </p>

            <p className="mt-2 text-sm text-slate-500">
              AI uznało, że opis tekstowy wystarczy i dodatkowa wizualizacja nie jest wymagana.
            </p>
          </div>
        )}

        <p className="mt-5 text-xs text-slate-500">
          To nie jest porada inwestycyjna. Analiza ma charakter informacyjny.
        </p>
      </div>
    </div>
  )
}

export default AIImpactCard