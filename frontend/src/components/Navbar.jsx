import { NavLink } from "react-router-dom"
import {
  Home,
  Newspaper,
  Bitcoin,
  CandlestickChart,
  Globe2,
  Heart,
  Info,
  LogIn,
  User,
} from "lucide-react"

function Navbar({ isLoggedIn, onLoginClick }) {
  const baseLink =
    "flex items-center gap-2 rounded-full px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800 hover:text-cyan-400"

  const activeLink =
    "flex items-center gap-2 rounded-full bg-cyan-500/10 px-4 py-2 text-sm text-cyan-400 ring-1 ring-cyan-500/30"

  return (
    <header className="sticky top-0 z-30 border-b border-slate-800/80 bg-slate-950/80 px-8 py-4 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-8">
        <div>
          <h1 className="text-xl font-bold tracking-tight">
            GeoMarket Intelligence
          </h1>

          <p className="text-xs text-slate-500">
            Financial & Geopolitical Intelligence Platform
          </p>
        </div>

        <nav className="hidden flex-wrap items-center gap-2 lg:flex">
          <NavLink
            to="/"
            className={({ isActive }) => (isActive ? activeLink : baseLink)}
          >
            <Home size={16} />
            Dashboard
          </NavLink>

          <NavLink
            to="/newsy"
            className={({ isActive }) => (isActive ? activeLink : baseLink)}
          >
            <Newspaper size={16} />
            Newsy
          </NavLink>

          <NavLink
            to="/kryptowaluty"
            className={({ isActive }) => (isActive ? activeLink : baseLink)}
          >
            <Bitcoin size={16} />
            Kryptowaluty
          </NavLink>

          <NavLink
            to="/gielda"
            className={({ isActive }) => (isActive ? activeLink : baseLink)}
          >
            <CandlestickChart size={16} />
            Giełda
          </NavLink>

          <NavLink
            to="/makro"
            className={({ isActive }) => (isActive ? activeLink : baseLink)}
          >
            <Globe2 size={16} />
            Makro
          </NavLink>

          {isLoggedIn && (
            <NavLink
              to="/ulubione"
              className={({ isActive }) => (isActive ? activeLink : baseLink)}
            >
              <Heart size={16} />
              Ulubione
            </NavLink>
          )}

          {isLoggedIn && (
            <NavLink
              to="/profil"
              className={({ isActive }) => (isActive ? activeLink : baseLink)}
            >
              <User size={16} />
              Profil
            </NavLink>
          )}

          <NavLink
            to="/o-projekcie"
            className={({ isActive }) => (isActive ? activeLink : baseLink)}
          >
            <Info size={16} />
            O projekcie
          </NavLink>
        </nav>

        {isLoggedIn ? (
          <button className="flex items-center gap-2 rounded-full border border-slate-700 px-5 py-2 text-sm text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400">
            <User size={16} />
            Wyloguj
          </button>
        ) : (
          <button
            onClick={onLoginClick}
            className="flex items-center gap-2 rounded-full bg-cyan-400 px-5 py-2 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-300"
          >
            <LogIn size={16} />
            Logowanie
          </button>
        )}
      </div>
    </header>
  )
}

export default Navbar