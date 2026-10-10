import { useState } from "react"
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

function App() {
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(false)

  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user")
    return savedUser ? JSON.parse(savedUser) : null
  })

  const isLoggedIn = Boolean(user)

  function handleDemoLogin() {
    const demoUser = {
      id: 1,
      name: "Kamil",
      email: "kamil@test.pl",
    }

    localStorage.setItem("user", JSON.stringify(demoUser))
    localStorage.setItem("token", "demo-jwt-token")

    setUser(demoUser)
    setIsLoginOpen(false)
  }

  function handleLogout() {
    localStorage.removeItem("user")
    localStorage.removeItem("token")

    setUser(null)
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
          onDemoLogin={handleDemoLogin}
        />
      </div>
    </BrowserRouter>
  )
}

export default App