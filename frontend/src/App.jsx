import { useState } from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom"

import Navbar from "./components/Navbar"
import AIBotButton from "./components/AIBotButton"
import LoginDrawer from "./components/LoginDrawer"

import Dashboard from "./pages/Dashboard"
import Markets from "./pages/Markets"
import Bitcoin from "./pages/Bitcoin"
import StockMarket from "./pages/StockMarket"
import Macro from "./pages/Macro"
import News from "./pages/News"
import AboutProject from "./pages/AboutProject"
import Favorites from "./pages/Favorites"
import Profile from "./pages/Profile"

function App() {
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const isLoggedIn = false

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 text-white">
        <Navbar
          isLoggedIn={isLoggedIn}
          onLoginClick={() => setIsLoginOpen(true)}
        />

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/rynki" element={<Markets />} />
          <Route path="/bitcoin" element={<Bitcoin />} />
          <Route path="/gielda" element={<StockMarket />} />
          <Route path="/makro" element={<Macro />} />
          <Route path="/newsy" element={<News />} />
          <Route path="/o-projekcie" element={<AboutProject />} />

          {isLoggedIn && (
            <>
              <Route path="/ulubione" element={<Favorites />} />
              <Route path="/profil" element={<Profile />} />
            </>
          )}
        </Routes>

        <AIBotButton />

        <LoginDrawer
          isOpen={isLoginOpen}
          onClose={() => setIsLoginOpen(false)}
        />
      </div>
    </BrowserRouter>
  )
}

export default App