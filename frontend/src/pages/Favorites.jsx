import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  BarChart3,
  Bitcoin,
  Heart,
  Star,
  Trash2,
} from "lucide-react"

function Favorites({ isLoggedIn, onLoginRequired }) {
  const navigate = useNavigate()

  const [stockFavorites, setStockFavorites] = useState([])
  const [cryptoFavorites, setCryptoFavorites] = useState([])
  const [macroFavorites, setMacroFavorites] = useState([])

  useEffect(() => {
    loadFavorites()
  }, [])

  useEffect(() => {
    if (!isLoggedIn) {
      onLoginRequired()
    }
  }, [isLoggedIn, onLoginRequired])

  function loadFavorites() {
    const savedStocks = localStorage.getItem("stockFavorites")
    const savedCrypto = localStorage.getItem("cryptoFavorites")
    const savedMacro = localStorage.getItem("macroFavorites")

    setStockFavorites(savedStocks ? JSON.parse(savedStocks) : [])
    setCryptoFavorites(savedCrypto ? JSON.parse(savedCrypto) : [])
    setMacroFavorites(savedMacro ? JSON.parse(savedMacro) : [])
  }

  function removeStockFavorite(event, symbol) {
    event.stopPropagation()

    const updated = stockFavorites.filter((item) => item.symbol !== symbol)

    setStockFavorites(updated)
    localStorage.setItem("stockFavorites", JSON.stringify(updated))
  }

  function removeCryptoFavorite(event, id) {
    event.stopPropagation()

    const updated = cryptoFavorites.filter((item) => item.id !== id)

    setCryptoFavorites(updated)
    localStorage.setItem("cryptoFavorites", JSON.stringify(updated))
  }

  function removeMacroFavorite(event, symbol) {
    event.stopPropagation()

    const updated = macroFavorites.filter((item) => item.symbol !== symbol)

    setMacroFavorites(updated)
    localStorage.setItem("macroFavorites", JSON.stringify(updated))
  }

  function openStock(item) {
    navigate(`/gielda?symbol=${encodeURIComponent(item.symbol)}`, {
      state: { selectedSymbol: item.symbol },
    })
  }

  function openCrypto(item) {
    const cryptoId = item.id || item.symbol

    navigate(`/kryptowaluty?id=${encodeURIComponent(cryptoId)}`, {
      state: { selectedCryptoId: cryptoId },
    })
  }

  function openMacro(item) {
    navigate(`/makro?symbol=${encodeURIComponent(item.symbol)}`, {
      state: { selectedSymbol: item.symbol },
    })
  }

  const totalFavorites =
    stockFavorites.length + cryptoFavorites.length + macroFavorites.length

  if (!isLoggedIn) {
    return (
      <main className="px-8 py-8">
        <section className="rounded-3xl border border-yellow-500/30 bg-slate-900/90 p-8">
          <div className="mb-5 flex items-center gap-3 text-yellow-400">
            <Heart size={28} />

            <h2 className="text-3xl font-bold text-white">
              Ulubione
            </h2>
          </div>

          <p className="max-w-3xl leading-7 text-slate-400">
            Widok ulubionych jest dostępny po zalogowaniu. Po zalogowaniu
            użytkownik może zapisywać wybrane instrumenty giełdowe,
            kryptowaluty oraz wskaźniki makroekonomiczne.
          </p>

          <button
            onClick={onLoginRequired}
            className="mt-6 rounded-2xl border border-yellow-500/30 bg-yellow-500/10 px-5 py-3 text-sm font-semibold text-yellow-300 transition hover:bg-yellow-500/20"
          >
            Przejdź do logowania
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="px-8 py-8">
      <section className="relative overflow-hidden rounded-3xl border border-yellow-500/30 bg-slate-900/90 p-8">
        <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-yellow-500/10 blur-3xl"></div>

        <div className="relative">
          <p className="mb-4 inline-flex rounded-full border border-yellow-500/40 bg-yellow-500/10 px-4 py-1 text-sm text-yellow-400">
            User favorites
          </p>

          <h2 className="text-4xl font-bold">
            Ulubione
          </h2>

          <p className="mt-4 max-w-4xl leading-7 text-slate-300">
            Widok prezentuje zapisane przez użytkownika elementy z głównych
            części aplikacji: instrumenty giełdowe, kryptowaluty oraz wskaźniki
            makroekonomiczne.
          </p>

          <div className="mt-6 grid max-w-5xl grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-emerald-400">
                Giełda
              </p>

              <p className="mt-2 text-2xl font-bold text-white">
                {stockFavorites.length}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-orange-400">
                Kryptowaluty
              </p>

              <p className="mt-2 text-2xl font-bold text-white">
                {cryptoFavorites.length}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-violet-400">
                Makro
              </p>

              <p className="mt-2 text-2xl font-bold text-white">
                {macroFavorites.length}
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-8 rounded-3xl border border-slate-800 bg-slate-900/80 p-6">
        <div className="mb-6">
          <h3 className="text-2xl font-bold">
            Zapisane elementy
          </h3>

          <p className="mt-1 text-sm text-slate-400">
            Łącznie zapisanych elementów: {totalFavorites}
          </p>
        </div>

        {totalFavorites === 0 && (
          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 text-sm leading-7 text-slate-400">
            Nie masz jeszcze zapisanych ulubionych elementów. Możesz dodawać je
            z poziomu zakładek Giełda, Kryptowaluty oraz Makro.
          </div>
        )}

        <div className="space-y-6">
          {stockFavorites.length > 0 && (
            <div>
              <div className="mb-4 flex items-center gap-3 text-emerald-400">
                <BarChart3 size={22} />

                <h4 className="text-xl font-bold text-white">
                  Instrumenty giełdowe
                </h4>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {stockFavorites.map((item) => (
                  <div
                    key={item.symbol}
                    onClick={() => openStock(item)}
                    className="cursor-pointer rounded-2xl border border-slate-800 bg-slate-950/70 p-5 transition hover:border-emerald-400/50 hover:bg-slate-900"
                  >
                    <div className="mb-4 flex items-start justify-between gap-4">
                      <div>
                        <p className="font-bold text-white">
                          {item.name}
                        </p>

                        <p className="mt-1 text-sm text-slate-500">
                          {item.symbol} · {item.market || "Rynek"}
                        </p>
                      </div>

                      <button
                        onClick={(event) => removeStockFavorite(event, item.symbol)}
                        className="text-slate-500 transition hover:text-red-400"
                        title="Usuń z ulubionych"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500">
                        Cena
                      </span>

                      <span className="font-semibold text-white">
                        {item.price ?? "-"}
                      </span>
                    </div>

                    <p className="mt-4 text-xs text-emerald-400">
                      Kliknij, aby przejść do instrumentu
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {cryptoFavorites.length > 0 && (
            <div>
              <div className="mb-4 flex items-center gap-3 text-orange-400">
                <Bitcoin size={22} />

                <h4 className="text-xl font-bold text-white">
                  Kryptowaluty
                </h4>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {cryptoFavorites.map((item) => (
                  <div
                    key={item.id || item.symbol}
                    onClick={() => openCrypto(item)}
                    className="cursor-pointer rounded-2xl border border-slate-800 bg-slate-950/70 p-5 transition hover:border-orange-400/50 hover:bg-slate-900"
                  >
                    <div className="mb-4 flex items-start justify-between gap-4">
                      <div className="flex items-center gap-3">
                        {item.image && (
                          <img
                            src={item.image}
                            alt={item.name}
                            className="h-8 w-8 rounded-full"
                          />
                        )}

                        <div>
                          <p className="font-bold text-white">
                            {item.name}
                          </p>

                          <p className="mt-1 text-sm uppercase text-slate-500">
                            {item.symbol}
                          </p>
                        </div>
                      </div>

                      <button
                        onClick={(event) => removeCryptoFavorite(event, item.id)}
                        className="text-slate-500 transition hover:text-red-400"
                        title="Usuń z ulubionych"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500">
                        Cena
                      </span>

                      <span className="font-semibold text-white">
                        {item.current_price ?? item.price ?? "-"}
                      </span>
                    </div>

                    <p className="mt-4 text-xs text-orange-400">
                      Kliknij, aby przejść do kryptowaluty
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {macroFavorites.length > 0 && (
            <div>
              <div className="mb-4 flex items-center gap-3 text-violet-400">
                <Star size={22} />

                <h4 className="text-xl font-bold text-white">
                  Wskaźniki makroekonomiczne
                </h4>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {macroFavorites.map((item) => (
                  <div
                    key={item.symbol}
                    onClick={() => openMacro(item)}
                    className="cursor-pointer rounded-2xl border border-slate-800 bg-slate-950/70 p-5 transition hover:border-violet-400/50 hover:bg-slate-900"
                  >
                    <div className="mb-4 flex items-start justify-between gap-4">
                      <div>
                        <p className="font-bold text-white">
                          {item.name}
                        </p>

                        <p className="mt-1 text-sm text-slate-500">
                          {item.symbol} · {item.category || "Makro"}
                        </p>
                      </div>

                      <button
                        onClick={(event) => removeMacroFavorite(event, item.symbol)}
                        className="text-slate-500 transition hover:text-red-400"
                        title="Usuń z ulubionych"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-500">
                        Wartość
                      </span>

                      <span className="font-semibold text-white">
                        {item.value ?? "-"} {item.unit || ""}
                      </span>
                    </div>

                    <p className="mt-4 text-xs text-violet-400">
                      Kliknij, aby przejść do wskaźnika
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  )
}

export default Favorites