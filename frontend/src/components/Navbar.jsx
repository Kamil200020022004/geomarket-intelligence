import { NavLink } from "react-router-dom"

function Navbar({ isLoggedIn, onLoginClick }) {
  const baseLink = "text-slate-300 hover:text-cyan-400"
  const activeLink = "text-cyan-400"

  return (
    <header className="border-b border-slate-800 bg-slate-950 px-8 py-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            GeoMarket Intelligence
          </h1>

          <p className="text-sm text-slate-400">
            Platforma analizy danych finansowych i geopolitycznych
          </p>
        </div>

        <nav className="flex gap-6 text-sm">
          <NavLink
            to="/"
            className={({ isActive }) => isActive ? activeLink : baseLink}
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/rynki"
            className={({ isActive }) => isActive ? activeLink : baseLink}
          >
            Rynki
          </NavLink>

          <NavLink
            to="/bitcoin"
            className={({ isActive }) => isActive ? activeLink : baseLink}
          >
            Bitcoin
          </NavLink>

          <NavLink
            to="/gielda"
            className={({ isActive }) => isActive ? activeLink : baseLink}
          >
            Giełda
          </NavLink>

          <NavLink
            to="/makro"
            className={({ isActive }) => isActive ? activeLink : baseLink}
          >
            Makro
          </NavLink>

          <NavLink
            to="/newsy"
            className={({ isActive }) => isActive ? activeLink : baseLink}
          >
            Newsy
          </NavLink>

          <NavLink
            to="/o-projekcie"
            className={({ isActive }) => isActive ? activeLink : baseLink}
          >
            O projekcie
          </NavLink>

          {isLoggedIn && (
            <NavLink
              to="/ulubione"
              className={({ isActive }) => isActive ? activeLink : baseLink}
            >
              Ulubione
            </NavLink>
          )}

          {isLoggedIn && (
            <NavLink
              to="/profil"
              className={({ isActive }) => isActive ? activeLink : baseLink}
            >
              Profil
            </NavLink>
          )}
        </nav>

        {isLoggedIn ? (
          <button className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300">
            Wyloguj
          </button>
        ) : (
          <button
            onClick={onLoginClick}
            className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950"
          >
            Logowanie
          </button>
        )}
      </div>
    </header>
  )
}

export default Navbar