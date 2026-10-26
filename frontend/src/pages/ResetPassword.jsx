import { useState } from "react"
import { Link, useSearchParams } from "react-router-dom"

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

export default function ResetPassword() {
  const [params] = useSearchParams()
  const token = params.get("token") || ""
  const [password, setPassword] = useState("")
  const [repeatPassword, setRepeatPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  async function handleSubmit(event) {
    event.preventDefault()
    setError("")
    setSuccess("")
    if (password.length < 8) return setError("Hasło musi mieć co najmniej 8 znaków.")
    if (password !== repeatPassword) return setError("Hasła muszą być identyczne.")
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Nie udało się zmienić hasła.")
      setSuccess("Hasło zostało zmienione. Wróć do logowania.")
      setPassword("")
      setRepeatPassword("")
      // Avoid retaining password reset tokens in address bar after success.
      window.history.replaceState({}, "", "/reset-password")
    } catch (err) {
      setError(err.message || "Nie udało się zmienić hasła.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="flex min-h-[75vh] items-center justify-center px-6 py-12">
      <section className="w-full max-w-md rounded-3xl border border-cyan-500/30 bg-slate-900/90 p-8">
        <h1 className="text-3xl font-bold text-white">Ustaw nowe hasło</h1>
        <p className="mt-3 text-sm text-slate-400">Link do zmiany hasła jest ważny przez 15 minut.</p>
        {!token && !success && <p role="alert" className="mt-5 text-red-400">Brak tokenu. Otwórz link otrzymany w wiadomości e-mail.</p>}
        {error && <p role="alert" className="mt-5 text-sm text-red-400">{error}</p>}
        {success && <p role="status" className="mt-5 text-sm text-emerald-400">{success}</p>}
        {!!token && !success && (
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block text-sm text-slate-300">Nowe hasło
              <input type="password" autoComplete="new-password" minLength={8} maxLength={128} required value={password} onChange={event => setPassword(event.target.value)} disabled={loading} className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400" />
            </label>
            <label className="block text-sm text-slate-300">Powtórz hasło
              <input type="password" autoComplete="new-password" minLength={8} maxLength={128} required value={repeatPassword} onChange={event => setRepeatPassword(event.target.value)} disabled={loading} className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400" />
            </label>
            <button disabled={loading} type="submit" className="w-full rounded-xl bg-cyan-400 py-3 font-semibold text-slate-950 hover:bg-cyan-300 disabled:opacity-60">{loading ? "Zmieniam hasło..." : "Zmień hasło"}</button>
          </form>
        )}
        <Link className="mt-6 inline-block text-sm text-cyan-400 hover:text-cyan-300" to="/">Wróć do strony głównej i zaloguj się</Link>
      </section>
    </main>
  )
}
