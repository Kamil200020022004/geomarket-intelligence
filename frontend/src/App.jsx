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
import Profile from "./pages/Profile"

function App() {
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(false)

  const isLoggedIn = false

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.16),_transparent_32%),linear-gradient(135deg,_#020617_0%,_#0f172a_45%,_#020617_100%)] text-white">
        <Navbar
          isLoggedIn={isLoggedIn}
          onLoginClick={() => setIsLoginOpen(true)}
        />

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/newsy" element={<News />} />
          <Route path="/kryptowaluty" element={<Crypto />} />
          <Route path="/gielda" element={<StockMarket />} />
          <Route path="/makro" element={<Macro />} />
          <Route path="/o-projekcie" element={<AboutProject />} />

          {isLoggedIn && (
            <>
              <Route path="/ulubione" element={<Favorites />} />
              <Route path="/profil" element={<Profile />} />
            </>
          )}
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
        />
      </div>
    </BrowserRouter>
  )
}

export default App