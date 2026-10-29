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
      "Nie można nawiązać połączenia. Spróbuj ponownie za chwilę."
    )
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Nieprawidłowy adres e-mail lub hasło.")
    }

    if (response.status === 409) {
      throw new Error("Konto z tym adresem już istnieje.")
    }

    if (response.status === 422) {
      throw new Error("Sprawdź poprawność wprowadzonych danych.")
    }

    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : `Wystąpił błąd serwera (${response.status}).`
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
    setFormData(INITIAL_FORM)
    setError("")
    setSuccess("")
    onClose()
  }

  async function handleLogin(event) {
    event.preventDefault()
    if (loading) return

    setLoading(true)
    setError("")
    setSuccess("")

    try {
      const result = await authRequest("/auth/login", {
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
      })

      await onLoginSuccess(result)
      setFormData(INITIAL_FORM)
      setMode("login")
    } catch (err) {
      setError(err.message || "Nie udało się zalogować.")
    } finally {
      setLoading(false)
    }
  }

  async function handleRegister(event) {
    event.preventDefault()
    if (loading) return

    const name = formData.name.trim()
    const email = formData.email.trim().toLowerCase()

    if (name.length < 2) {
      setError("Imię musi mieć co najmniej 2 znaki.")
      return
    }

    if (formData.password.length < 8) {
      setError("Hasło musi mieć co najmniej 8 znaków.")
      return
    }

    if (formData.password !== formData.repeatPassword) {
      setError("Hasła nie są identyczne.")
      return
    }

    setLoading(true)
    setError("")
    setSuccess("")

    try {
      await authRequest("/auth/register", {
        name,
        email,
        password: formData.password,
      })

      setMode("login")
      setFormData({
        ...INITIAL_FORM,
        email,
      })

      setSuccess(
        "Konto zostało utworzone. Możesz się zalogować."
      )
    } catch (err) {
      setError(err.message || "Nie udało się utworzyć konta.")
    } finally {
      setLoading(false)
    }
  }

  async function handleForgotPassword(event) {
    event.preventDefault()
    if (loading) return

    const email = formData.email.trim().toLowerCase()

    if (!email) {
      setError("Podaj adres e-mail.")
      return
    }

    setLoading(true)
    setError("")
    setSuccess("")

    try {
      const result = await authRequest(
        "/auth/forgot-password",
        { email }
      )

      setSuccess(
        result.message ||
        "Jeśli konto istnieje, wyślemy wiadomość z linkiem resetującym."
      )
    } catch (err) {
      setError(
        err.message || "Nie udało się wysłać żądania."
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
        : "Podaj adres e-mail przypisany do Twojego konta. Otrzymasz link do ustawienia nowego hasła."

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
          {[
            ["login", "Logowanie"],
            ["register", "Rejestracja"],
            ["reset", "Reset"],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => switchMode(value)}
              disabled={loading}
              className={`flex-1 rounded-full px-4 py-2 text-sm transition ${
                mode === value
                  ? "bg-cyan-400 text-slate-950"
                  : "text-slate-400 hover:text-cyan-400"
              }`}
            >
              {label}
            </button>
          ))}
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
              <label htmlFor="login-email" className="text-sm text-slate-300">
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
              <label htmlFor="login-password" className="text-sm text-slate-300">
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
              Nie pamiętasz hasła?
            </button>
          </form>
        )}

        {mode === "register" && (
          <form onSubmit={handleRegister} className="mt-6 space-y-4">
            <div>
              <label htmlFor="register-name" className="text-sm text-slate-300">
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
              <label htmlFor="register-email" className="text-sm text-slate-300">
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
              <label htmlFor="register-password" className="text-sm text-slate-300">
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
              <label htmlFor="register-repeat-password" className="text-sm text-slate-300">
                Powtórz hasło
              </label>

              <input
                id="register-repeat-password"
                name="repeatPassword"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
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
          <form
            onSubmit={handleForgotPassword}
            className="mt-6 space-y-4"
          >
            <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5">
              <h3 className="font-semibold text-cyan-300">
                Odzyskiwanie hasła
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                Wpisz swój adres e-mail. Jeśli konto istnieje,
                wyślemy link do zmiany hasła, ważny przez 15 minut.
              </p>
            </div>

            <div>
              <label htmlFor="reset-email" className="text-sm text-slate-300">
                Adres e-mail
              </label>

              <input
                id="reset-email"
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

            <button
              type="submit"
              disabled={loading}
              className={submitClass}
            >
              {loading ? "Wysyłanie..." : "Wyślij link resetujący"}
            </button>

            <button
              type="button"
              onClick={() => switchMode("login")}
              disabled={loading}
              className={secondaryButtonClass}
            >
              Wróć do logowania
            </button>
          </form>
        )}

        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <p className="text-sm font-semibold text-cyan-400">
            Twoje konto GeoMarket
          </p>

          <p className="mt-2 text-sm leading-6 text-slate-400">
            Korzystaj z własnej listy ulubionych instrumentów,
            zarządzaj kontem i odzyskuj dostęp do niego za pomocą
            adresu e-mail.
          </p>
        </div>

      </div>
    </div>
  )
}

export default LoginDrawer
