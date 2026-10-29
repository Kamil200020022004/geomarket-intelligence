import { Link } from "react-router-dom"

function MarketCard({ name, value, change, path }) {
  const isPositive = change.startsWith("+")

  return (
    <Link
      to={path}
      className="group block rounded-2xl border border-slate-800/80 bg-slate-900/80 p-5 backdrop-blur transition hover:-translate-y-1 hover:border-cyan-500/40 hover:bg-slate-900 hover:shadow-xl hover:shadow-cyan-950/20"
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400 ring-1 ring-cyan-500/20">
              {name.slice(0, 1)}
            </div>

            <div>
              <p className="font-semibold text-slate-100">
                {name}
              </p>

              <p className="text-xs text-slate-500">
                Market indicator
              </p>
            </div>
          </div>
        </div>

        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            isPositive
              ? "bg-emerald-500/10 text-emerald-400"
              : "bg-red-500/10 text-red-400"
          }`}
        >
          {change}
        </span>
      </div>

      <div className="mt-6">
        <p className="text-3xl font-bold tracking-tight">
          {value}
        </p>

        <p className="mt-1 text-sm text-slate-500">
          Aktualna wartość instrumentu
        </p>
      </div>

      <div className="mt-5">
        <div className="mb-2 flex justify-between text-xs text-slate-500">
          <span>Trend</span>
          <span>{isPositive ? "Wzrost" : "Spadek"}</span>
        </div>

        <div className="h-2 overflow-hidden rounded-full bg-slate-800">
          <div
            className={`h-full rounded-full ${
              isPositive ? "w-3/4 bg-emerald-400" : "w-2/5 bg-red-400"
            }`}
          />
        </div>
      </div>
    </Link>
  )
}

export default MarketCard