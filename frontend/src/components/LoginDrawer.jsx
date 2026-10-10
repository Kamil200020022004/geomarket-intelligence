import { useState } from "react"

function LoginDrawer({ isOpen, onClose, onDemoLogin }) {
  const [mode, setMode] = useState("login")
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    repeatPassword: "",
  })
  const [error, setError] = useState("")

  if (!isOpen) return null

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))

    setError("")
  }

  function handleLogin(event) {
    event.preventDefault()

    if (!formData.email || !formData.password) {
      setError("Uzupełnij e-mail oraz hasło.")
      return
    }

    onDemoLogin()
  }

  function handleRegister(event) {
    event.preventDefault()

    if (
      !formData.name ||
      !formData.email ||
      !formData.password ||
      !formData.repeatPassword
    ) {
      setError("Uzupełnij wszystkie pola rejestracji.")
      return
    }

    if (formData.password !== formData.repeatPassword) {
      setError("Hasła nie są takie same.")
      return
    }

    onDemoLogin()
  }

  function handleResetPassword(event) {
    event.preventDefault()

    if (!formData.email) {
      setError("Podaj adres e-mail do resetu hasła.")
      return
    }

    setError("")
    alert("Link do resetu hasła został wysłany na podany adres e-mail.")
    setMode("login")
  }

  function switchMode(nextMode) {
    setMode(nextMode)
    setError("")
  }

  const title =
    mode === "login"
      ? "Logowanie"
      : mode === "register"
        ? "Rejestracja"
        : "Reset hasła"

  const description =
    mode === "login"
      ? "Zaloguj się, aby uzyskać dostęp do ulubionych elementów."
      : mode === "register"
        ? "Utwórz konto, aby zapisywać ulubione instrumenty giełdowe, kryptowaluty i wskaźniki makroekonomiczne."
        : "Podaj adres e-mail, aby otrzymać link do resetu hasła."

  return (
    <div className="fixed inset-0 z-40 bg-black/60">
      <div className="absolute right-0 top-0 h-full w-full max-w-md overflow-y-auto border-l border-slate-800 bg-slate-950 p-6 shadow-2xl shadow-cyan-950/30">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">
            {title}
          </h2>

          <button
            onClick={onClose}
            className="rounded-lg border border-slate-700 px-3 py-1 text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
          >
            X
          </button>
        </div>

        <p className="mt-2 text-sm leading-6 text-slate-400">
          {description}
        </p>

        <div className="mt-6 flex rounded-full border border-slate-800 bg-slate-900 p-1">
          <button
            onClick={() => switchMode("login")}
            className={`flex-1 rounded-full px-4 py-2 text-sm transition ${
              mode === "login"
                ? "bg-cyan-400 text-slate-950"
                : "text-slate-400 hover:text-cyan-400"
            }`}
          >
            Logowanie
          </button>

          <button
            onClick={() => switchMode("register")}
            className={`flex-1 rounded-full px-4 py-2 text-sm transition ${
              mode === "register"
                ? "bg-cyan-400 text-slate-950"
                : "text-slate-400 hover:text-cyan-400"
            }`}
          >
            Rejestracja
          </button>

          <button
            onClick={() => switchMode("reset")}
            className={`flex-1 rounded-full px-4 py-2 text-sm transition ${
              mode === "reset"
                ? "bg-cyan-400 text-slate-950"
                : "text-slate-400 hover:text-cyan-400"
            }`}
          >
            Reset
          </button>
        </div>

        {error && (
          <div className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {mode === "login" && (
          <form onSubmit={handleLogin} className="mt-6 space-y-4">
            <div>
              <label className="text-sm text-slate-300">
                E-mail
              </label>

              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="jan.kowalski@email.com"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-sm text-slate-300">
                Hasło
              </label>

              <input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-xl bg-cyan-400 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              Zaloguj się
            </button>

            <button
              type="button"
              onClick={() => switchMode("reset")}
              className="w-full rounded-xl border border-slate-700 py-3 text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
            >
              Odzyskaj hasło
            </button>
          </form>
        )}

        {mode === "register" && (
          <form onSubmit={handleRegister} className="mt-6 space-y-4">
            <div>
              <label className="text-sm text-slate-300">
                Imię
              </label>

              <input
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                placeholder="Kamil"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-sm text-slate-300">
                E-mail
              </label>

              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="jan.kowalski@email.com"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-sm text-slate-300">
                Hasło
              </label>

              <input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-sm text-slate-300">
                Powtórz hasło
              </label>

              <input
                name="repeatPassword"
                type="password"
                value={formData.repeatPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-xl bg-cyan-400 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              Utwórz konto
            </button>
          </form>
        )}

        {mode === "reset" && (
          <form onSubmit={handleResetPassword} className="mt-6 space-y-4">
            <div>
              <label className="text-sm text-slate-300">
                E-mail
              </label>

              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="jan.kowalski@email.com"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-400"
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-xl bg-cyan-400 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300"
            >
              Wyślij link resetujący
            </button>

            <button
              type="button"
              onClick={() => switchMode("login")}
              className="w-full rounded-xl border border-slate-700 py-3 text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
            >
              Wróć do logowania
            </button>
          </form>
        )}

        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <p className="text-sm font-semibold text-cyan-400">
            Tryb testowy
          </p>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            Do czasu podpięcia backendu logowanie działa lokalnie. Po integracji
            z API logowanie będzie obsługiwane przez token JWT.
          </p>

          <button
            onClick={onDemoLogin}
            className="mt-4 w-full rounded-xl border border-cyan-500/30 bg-cyan-500/10 py-3 font-semibold text-cyan-300 transition hover:bg-cyan-500/20"
          >
            Zaloguj testowo
          </button>
        </div>
      </div>
    </div>
  )
}

export default LoginDrawer