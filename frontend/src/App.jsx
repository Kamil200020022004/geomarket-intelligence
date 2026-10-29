
import { useEffect, useState } from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom"

import Navbar from "./components/Navbar"
import AIBotButton from "./components/AIBotButton"
import LoginDrawer from "./components/LoginDrawer"
import ChatDrawer from "./components/ChatDrawer"
import Footer from "./components/Footer"

import Dashboard from "./pages/Dashboard"
import Crypto from "./pages/Crypto"
import StockMarket from "./pages/StockMarket"
import Macro from "./pages/Macro"
import News from "./pages/News"
import AboutProject from "./pages/AboutProject"
import Favorites from "./pages/Favorites"
import ResetPassword from "./pages/ResetPassword"

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

function App() {
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(false)

  const [user, setUser] = useState(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)

  const isLoggedIn = Boolean(user)

  // ==========================================================
  // PRZYWRACANIE SESJI PO ODŚWIEŻENIU STRONY
  // ==========================================================

  useEffect(() => {
    let cancelled = false

    async function restoreSession() {
      const token = localStorage.getItem("token")

      if (!token) {
        setIsCheckingSession(false)
        return
      }

      try {
        const response = await fetch(`${API_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          throw new Error("Sesja jest nieważna")
        }

        const data = await response.json()
        const currentUser = data.user || data

        if (!cancelled) {
          setUser(currentUser)

          localStorage.setItem(
            "user",
            JSON.stringify(currentUser)
          )
        }
      } catch (error) {
        if (!cancelled) {
          console.error(
            "Nie udało się przywrócić sesji:",
            error
          )

          localStorage.removeItem("token")
          localStorage.removeItem("user")

          setUser(null)
        }
      } finally {
        if (!cancelled) {
          setIsCheckingSession(false)
        }
      }
    }

    restoreSession()

    return () => {
      cancelled = true
    }
  }, [])

  // ==========================================================
  // LOGOWANIE
  // ==========================================================

  async function handleLoginSuccess(loginData) {
    const token = loginData.access_token || loginData.token

    if (!token) {
      throw new Error(
        "Backend nie zwrócił tokenu uwierzytelniania."
      )
    }

    localStorage.setItem("token", token)

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error(
          "Nie udało się pobrać danych użytkownika."
        )
      }

      const data = await response.json()
      const loggedInUser = data.user || data

      if (
        loggedInUser.id === null ||
        loggedInUser.id === undefined
      ) {
        throw new Error(
          "Backend nie zwrócił identyfikatora użytkownika."
        )
      }

      localStorage.setItem(
        "user",
        JSON.stringify(loggedInUser)
      )

      setUser(loggedInUser)
      setIsLoginOpen(false)

    } catch (error) {
      localStorage.removeItem("token")
      localStorage.removeItem("user")

      setUser(null)

      throw error
    }
  }

  // ==========================================================
  // WYLOGOWANIE
  // ==========================================================

  async function handleLogout() {
    const token = localStorage.getItem("token")

    try {
      if (token) {
        await fetch(`${API_URL}/auth/logout`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      }
    } catch (error) {
      console.error("Błąd wylogowania:", error)

    } finally {
      localStorage.removeItem("token")
      localStorage.removeItem("user")

      setUser(null)
      setIsLoginOpen(false)
    }
  }

  // ==========================================================
  // SPRAWDZANIE SESJI
  // ==========================================================

  if (isCheckingSession) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="text-center">

          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />

          <p className="text-sm text-slate-400">
            Sprawdzanie sesji użytkownika...
          </p>

        </div>
      </div>
    )
  }

  // ==========================================================
  // GŁÓWNA APLIKACJA
  // ==========================================================

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.16),_transparent_32%),linear-gradient(135deg,_#020617_0%,_#0f172a_45%,_#020617_100%)] text-white">

        {/* NAWIGACJA */}

        <Navbar
          isLoggedIn={isLoggedIn}
          user={user}
          onLoginClick={() => setIsLoginOpen(true)}
          onLogout={handleLogout}
        />

        {/* ZAKŁADKI */}

        <Routes>

          {/* DASHBOARD */}

          <Route
            path="/"
            element={<Dashboard />}
          />

          {/* NEWSY */}

          <Route
            path="/newsy"
            element={<News />}
          />

          {/* KRYPTOWALUTY */}

          <Route
            path="/kryptowaluty"
            element={
              <Crypto
                user={user}
                isLoggedIn={isLoggedIn}
                onLoginRequired={() => setIsLoginOpen(true)}
              />
            }
          />

          {/* GIEŁDA */}

          <Route
            path="/gielda"
            element={
              <StockMarket
                user={user}
                isLoggedIn={isLoggedIn}
                onLoginRequired={() => setIsLoginOpen(true)}
              />
            }
          />

          {/* MAKRO */}

          <Route
            path="/makro"
            element={
              <Macro
                user={user}
                isLoggedIn={isLoggedIn}
                onLoginRequired={() => setIsLoginOpen(true)}
              />
            }
          />

          {/* ULUBIONE */}

          <Route
            path="/ulubione"
            element={
              <Favorites
                user={user}
                isLoggedIn={isLoggedIn}
                onLoginRequired={() => setIsLoginOpen(true)}
              />
            }
          />

          {/* O PROJEKCIE */}

          <Route
            path="/o-projekcie"
            element={<AboutProject />}
          />

          {/* ODZYSKIWANIE HASŁA */}

          <Route
            path="/reset-password"
            element={<ResetPassword />}
          />

        </Routes>

        {/* STOPKA */}

        <Footer />

        {/* PRZYCISK CHATBOTA AI */}

        <AIBotButton
          onClick={() => setIsChatOpen(true)}
        />

        {/* PANEL CHATBOTA AI */}

        <ChatDrawer
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
        />

        {/* PANEL LOGOWANIA I REJESTRACJI */}

        <LoginDrawer
          isOpen={isLoginOpen}
          onClose={() => setIsLoginOpen(false)}
          onLoginSuccess={handleLoginSuccess}
        />

      </div>
    </BrowserRouter>
  )
}

export default App
