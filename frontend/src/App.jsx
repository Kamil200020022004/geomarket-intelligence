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

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

function App() {
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [user, setUser] = useState(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)

  const isLoggedIn = Boolean(user)

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

        if (!cancelled) {
          setUser(data.user || data)
        }
      } catch {
        if (!cancelled) {
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

  async function handleLoginSuccess(loginData) {
    const token = loginData.access_token || loginData.token

    if (!token) {
      throw new Error("Backend nie zwrócił tokenu logowania.")
    }

    localStorage.setItem("token", token)

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Nie udało się pobrać danych użytkownika.")
      }

      const data = await response.json()
      const loggedInUser = data.user || data

      localStorage.setItem("user", JSON.stringify(loggedInUser))

      setUser(loggedInUser)
      setIsLoginOpen(false)
    } catch (error) {
      localStorage.removeItem("token")
      localStorage.removeItem("user")
      setUser(null)
      throw error
    }
  }

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
    }
  }

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

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.16),_transparent_32%),linear-gradient(135deg,_#020617_0%,_#0f172a_45%,_#020617_100%)] text-white">
        <Navbar
          isLoggedIn={isLoggedIn}
          user={user}
          onLoginClick={() => setIsLoginOpen(true)}
          onLogout={handleLogout}
        />

        <Routes>
          <Route path="/" element={<Dashboard />} />

          <Route path="/newsy" element={<News />} />

          <Route
            path="/kryptowaluty"
            element={
              <Crypto
                isLoggedIn={isLoggedIn}
                onLoginRequired={() => setIsLoginOpen(true)}
              />
            }
          />

          <Route
            path="/gielda"
            element={
              <StockMarket
                isLoggedIn={isLoggedIn}
                onLoginRequired={() => setIsLoginOpen(true)}
              />
            }
          />

          <Route
            path="/makro"
            element={
              <Macro
                isLoggedIn={isLoggedIn}
                onLoginRequired={() => setIsLoginOpen(true)}
              />
            }
          />

          <Route
            path="/ulubione"
            element={
              <Favorites
                isLoggedIn={isLoggedIn}
                onLoginRequired={() => setIsLoginOpen(true)}
              />
            }
          />

          <Route path="/o-projekcie" element={<AboutProject />} />
        </Routes>

        <Footer />

        <AIBotButton onClick={() => setIsChatOpen(true)} />

        <ChatDrawer
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
        />

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