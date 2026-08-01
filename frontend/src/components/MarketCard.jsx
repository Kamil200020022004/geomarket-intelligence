function MarketCard({ name, value, change }) {
  const isPositive = change.startsWith("+")

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{name}</p>

      <p className="mt-2 text-2xl font-bold">
        {value}
      </p>

      <p className={`mt-2 text-sm ${isPositive ? "text-emerald-400" : "text-red-400"}`}>
        {change}
      </p>
    </div>
  )
}

export default MarketCard