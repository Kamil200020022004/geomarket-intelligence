function ChatDrawer({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="fixed bottom-24 right-6 z-50 flex h-[620px] w-[380px] flex-col overflow-hidden rounded-3xl border border-slate-700/80 bg-slate-950 shadow-2xl shadow-cyan-950/50">
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900 px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="relative flex h-11 w-11 items-center justify-center rounded-full bg-cyan-400 text-xl text-slate-950">
            🤖
            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-slate-900 bg-emerald-400"></span>
          </div>

          <div>
            <p className="font-semibold text-slate-100">
              GeoMarket AI
            </p>

            <p className="text-xs text-slate-400">
              Aktywny teraz
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-cyan-400">
          <button className="transition hover:text-cyan-300">
            —
          </button>

          <button
            onClick={onClose}
            className="text-xl transition hover:text-cyan-300"
          >
            ×
          </button>
        </div>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto bg-slate-950 px-4 py-5">
        <div className="flex justify-center">
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">
            Dzisiaj
          </span>
        </div>

        <div className="max-w-[80%] rounded-3xl rounded-bl-md bg-slate-800 px-4 py-3 text-sm text-slate-100">
          Cześć! Jestem asystentem AI platformy GeoMarket Intelligence.
        </div>

        <div className="ml-auto max-w-[80%] rounded-3xl rounded-br-md bg-cyan-400 px-4 py-3 text-sm font-medium text-slate-950">
          Jak napięcia geopolityczne mogą wpłynąć na EUR/PLN?
        </div>

        <div className="max-w-[85%] rounded-3xl rounded-bl-md bg-slate-800 px-4 py-3 text-sm leading-6 text-slate-100">
          Na podstawie danych AI może wskazać potencjalny wpływ wydarzenia na waluty,
          surowce oraz indeksy giełdowe. W przyszłości odpowiedź będzie generowana
          przez backend i model AI.
        </div>

        <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-3 text-xs text-slate-300">
          <p className="font-semibold text-cyan-400">
            Przykładowe możliwości:
          </p>

          <div className="mt-2 space-y-2">
            <p>• analiza wpływu wydarzeń na rynek</p>
            <p>• wyjaśnianie wykresów</p>
            <p>• pytania o Bitcoin, giełdę i makroekonomię</p>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-800 bg-slate-900 p-3">
        <div className="flex items-center gap-2">
          <button className="flex h-10 w-10 items-center justify-center rounded-full text-cyan-400 transition hover:bg-slate-800">
            +
          </button>

          <input
            type="text"
            placeholder="Aa"
            className="h-10 flex-1 rounded-full border border-slate-700 bg-slate-800 px-4 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-400"
          />

          <button className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-400 text-slate-950 transition hover:bg-cyan-300">
            ➤
          </button>
        </div>

        <p className="mt-2 text-center text-[11px] text-slate-500">
          To nie jest porada inwestycyjna. Odpowiedzi mają charakter informacyjny.
        </p>
      </div>
    </div>
  )
}

export default ChatDrawer