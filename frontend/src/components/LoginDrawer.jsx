function LoginDrawer({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-40 bg-black/60">
      <div className="absolute right-0 top-0 h-full w-full max-w-md border-l border-slate-800 bg-slate-950 p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">Logowanie</h2>

          <button
            onClick={onClose}
            className="rounded-lg border border-slate-700 px-3 py-1 text-slate-300"
          >
            X
          </button>
        </div>

        <p className="mt-2 text-sm text-slate-400">
          Zaloguj się, aby uzyskać dostęp do profilu i ulubionych wykresów.
        </p>

        <div className="mt-6 space-y-4">
          <div>
            <label className="text-sm text-slate-300">E-mail</label>
            <input
              type="email"
              placeholder="jan.kowalski@email.com"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label className="text-sm text-slate-300">Hasło</label>
            <input
              type="password"
              placeholder="••••••••"
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none focus:border-cyan-400"
            />
          </div>

          <button className="w-full rounded-xl bg-cyan-500 py-3 font-semibold text-slate-950">
            Zaloguj się
          </button>

          <button className="w-full rounded-xl border border-slate-700 py-3 text-slate-300">
            Odzyskaj hasło
          </button>
        </div>
      </div>
    </div>
  )
}

export default LoginDrawer