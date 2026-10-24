import { useState } from "react"

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

const INITIAL_FORM = {
  name: "",
  email: "",
  password: "",
  repeatPassword: "",
}

async function authRequest(endpoint, body) {
  let response

  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })
  } catch {
    throw new Error(
      "Nie można połączyć się z serwerem. Sprawdź, czy backend FastAPI jest uruchomiony."
    )
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Nieprawidłowy adres e-mail lub hasło.")
    }

    if (response.status === 409) {
      throw new Error("Konto z podanym adresem e-mail już istnieje.")
    }

    if (response.status === 422) {
      throw new Error(
        "Nieprawidłowe dane formularza. Sprawdź poprawność wprowadzonych informacji."
      )
    }

    const detail =
      typeof data.detail === "string"
        ? data.detail
        : typeof data.message === "string"
          ? data.message
          : null

    throw new Error(
      detail || `Wystąpił błąd serwera (${response.status}).`
    )
  }

  return data
}

function LoginDrawer({ isOpen, onClose, onLoginSuccess }) {
  const [mode, setMode] = useState("login")
  const [formData, setFormData] = useState(INITIAL_FORM)

  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [loading, setLoading] = useState(false)

  if (!isOpen) return null

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }))

    setError("")
    setSuccess("")
  }

  function switchMode(nextMode) {
    if (loading) return

    setMode(nextMode)
    setError("")
    setSuccess("")
    setFormData(INITIAL_FORM)
  }

  function handleClose() {
    if (loading) return

    setMode("login")
    setError("")
    setSuccess("")
    setFormData(INITIAL_FORM)

    onClose()
  }

  async function handleLogin(event) {
    event.preventDefault()

    if (loading) return

    const email = formData.email.trim().toLowerCase()
    const password = formData.password

    if (!email || !password) {
      setError("Uzupełnij adres e-mail oraz hasło.")
      return
    }

    setLoading(true)
    setError("")
    setSuccess("")

    try {
      const data = await authRequest("/auth/login", {
        email,
        password,
      })

      // App.jsx zapisuje token i sprawdza konto przez /auth/me.
      await onLoginSuccess(data)

      setFormData(INITIAL_FORM)
      setMode("login")
    } catch (requestError) {
      setError(
        requestError.message || "Nie udało się zalogować."
      )
    } finally {
      setLoading(false)
    }
  }

  async function handleRegister(event) {
    event.preventDefault()

    if (loading) return

    const name = formData.name.trim()
    const email = formData.email.trim().toLowerCase()
    const password = formData.password

    if (!name || !email || !password || !formData.repeatPassword) {
      setError("Uzupełnij wszystkie pola rejestracji.")
      return
    }

    if (name.length < 2) {
      setError("Imię powinno mieć co najmniej 2 znaki.")
      return
    }

    if (password.length < 8) {
      setError("Hasło musi zawierać co najmniej 8 znaków.")
      return
    }

    if (password !== formData.repeatPassword) {
      setError("Podane hasła nie są identyczne.")
      return
    }

    setLoading(true)
    setError("")
    setSuccess("")

    try {
      await authRequest("/auth/register", {
        name,
        email,
        password,
      })

      setMode("login")

      setFormData({
        ...INITIAL_FORM,
        email,
      })

      setSuccess(
        "Konto zostało utworzone. Możesz teraz się zalogować."
      )
    } catch (requestError) {
      setError(
        requestError.message || "Nie udało się utworzyć konta."
      )
    } finally {
      setLoading(false)
    }
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
        ? "Utwórz konto, aby zapisywać instrumenty giełdowe, kryptowaluty i wskaźniki makroekonomiczne."
        : "Odzyskiwanie hasła będzie dostępne po uruchomieniu odpowiedniej funkcji backendu."

  const inputClass =
    "mt-2 w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-400 disabled:opacity-50"

  const submitClass =
    "w-full rounded-xl bg-cyan-400 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"

  const secondaryButtonClass =
    "w-full rounded-xl border border-slate-700 py-3 text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"

  return (
    <div className="fixed inset-0 z-40 bg-black/60">
      <div className="absolute right-0 top-0 h-full w-full max-w-md overflow-y-auto border-l border-slate-800 bg-slate-950 p-6 shadow-2xl shadow-cyan-950/30">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">
            {title}
          </h2>

          <button
            type="button"
            onClick={handleClose}
            disabled={loading}
            className="rounded-lg border border-slate-700 px-3 py-1 text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400 disabled:opacity-50"
            aria-label="Zamknij panel"
          >
            X
          </button>
        </div>

        <p className="mt-2 text-sm leading-6 text-slate-400">
          {description}
        </p>

        <div className="mt-6 flex rounded-full border border-slate-800 bg-slate-900 p-1">
          <button
            type="button"
            onClick={() => switchMode("login")}
            disabled={loading}
            className={`flex-1 rounded-full px-4 py-2 text-sm transition ${
              mode === "login"
                ? "bg-cyan-400 text-slate-950"
                : "text-slate-400 hover:text-cyan-400"
            }`}
          >
            Logowanie
          </button>

          <button
            type="button"
            onClick={() => switchMode("register")}
            disabled={loading}
            className={`flex-1 rounded-full px-4 py-2 text-sm transition ${
              mode === "register"
                ? "bg-cyan-400 text-slate-950"
                : "text-slate-400 hover:text-cyan-400"
            }`}
          >
            Rejestracja
          </button>

          <button
            type="button"
            onClick={() => switchMode("reset")}
            disabled={loading}
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
          <div
            role="alert"
            className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300"
          >
            {error}
          </div>
        )}

        {success && (
          <div
            role="status"
            className="mt-5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300"
          >
            {success}
          </div>
        )}

        {mode === "login" && (
          <form onSubmit={handleLogin} className="mt-6 space-y-4">
            <div>
              <label
                htmlFor="login-email"
                className="text-sm text-slate-300"
              >
                E-mail
              </label>

              <input
                id="login-email"
                name="email"
                type="email"
                autoComplete="email"
                required
                disabled={loading}
                value={formData.email}
                onChange={handleChange}
                placeholder="jan.kowalski@email.com"
                className={inputClass}
              />
            </div>

            <div>
              <label
                htmlFor="login-password"
                className="text-sm text-slate-300"
              >
                Hasło
              </label>

              <input
                id="login-password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                disabled={loading}
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className={inputClass}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={submitClass}
            >
              {loading ? "Logowanie..." : "Zaloguj się"}
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => switchMode("reset")}
              className={secondaryButtonClass}
            >
              Odzyskaj hasło
            </button>
          </form>
        )}

        {mode === "register" && (
          <form onSubmit={handleRegister} className="mt-6 space-y-4">
            <div>
              <label
                htmlFor="register-name"
                className="text-sm text-slate-300"
              >
                Imię
              </label>

              <input
                id="register-name"
                name="name"
                type="text"
                autoComplete="given-name"
                required
                minLength={2}
                disabled={loading}
                value={formData.name}
                onChange={handleChange}
                placeholder="Kamil"
                className={inputClass}
              />
            </div>

            <div>
              <label
                htmlFor="register-email"
                className="text-sm text-slate-300"
              >
                E-mail
              </label>

              <input
                id="register-email"
                name="email"
                type="email"
                autoComplete="email"
                required
                disabled={loading}
                value={formData.email}
                onChange={handleChange}
                placeholder="jan.kowalski@email.com"
                className={inputClass}
              />
            </div>

            <div>
              <label
                htmlFor="register-password"
                className="text-sm text-slate-300"
              >
                Hasło
              </label>

              <input
                id="register-password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                disabled={loading}
                value={formData.password}
                onChange={handleChange}
                placeholder="Minimum 8 znaków"
                className={inputClass}
              />
            </div>

            <div>
              <label
                htmlFor="register-repeat-password"
                className="text-sm text-slate-300"
              >
                Powtórz hasło
              </label>

              <input
                id="register-repeat-password"
                name="repeatPassword"
                type="password"
                autoComplete="new-password"
                required
                disabled={loading}
                value={formData.repeatPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className={inputClass}
              />
            </div>

            <p className="text-xs leading-5 text-slate-500">
              Hasło powinno mieć co najmniej 8 znaków.
            </p>

            <button
              type="submit"
              disabled={loading}
              className={submitClass}
            >
              {loading ? "Tworzenie konta..." : "Utwórz konto"}
            </button>
          </form>
        )}

        {mode === "reset" && (
          <div className="mt-6 space-y-4">
            <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5">
              <h3 className="font-semibold text-amber-300">
                Resetowanie hasła
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Ta funkcja nie jest jeszcze obsługiwana przez
                tymczasowy backend Excel. Nie wysyłamy obecnie
                wiadomości z linkiem resetującym.
              </p>
            </div>

            <button
              type="button"
              onClick={() => switchMode("login")}
              className={secondaryButtonClass}
            >
              Wróć do logowania
            </button>
          </div>
        )}

        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <p className="text-sm font-semibold text-cyan-400">
            Konto użytkownika
          </p>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            Rejestracja i logowanie są obsługiwane przez backend
            GeoMarket Intelligence. Dane kont użytkowników są
            przechowywane w tymczasowej bazie Excel.
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginDrawer