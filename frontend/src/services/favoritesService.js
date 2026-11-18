// Adapter ulubionych — przygotowany przez Sebastiana do podmiany pliku
// frontend/src/services/favoritesService.js. Sygnatury funkcji bez zmian.
//
// VITE_FAVORITES_PROVIDER=local → jak dotąd: localStorage (bez backendu),
// VITE_FAVORITES_PROVIDER=api   → baza MySQL przez bramkę Sebastiana:
//   GET    /api/favorites/{type}            → tablica elementów
//   POST   /api/favorites/{type}  (obiekt)  → aktualna tablica
//   DELETE /api/favorites/{type}/{id}       → aktualna tablica
//
// W trybie "api" właściciela ulubionych backend ustala z tokenu logowania
// (nagłówek Authorization), a nie z argumentu userId — argument zostaje tylko
// dla zgodności sygnatur i do kluczy w trybie "local".

const PREFIX = "geomarket:favorites:v1"
const EVENT_NAME = "geomarket:favorites:changed"

const PROVIDER = import.meta.env.VITE_FAVORITES_PROVIDER || "local"
const API_URL = (
  import.meta.env.VITE_AUTH_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "")
// Ten sam klucz, pod którym App.jsx zapisuje token po zalogowaniu.
const TOKEN_KEY = "token"

const TYPES = ["stock", "crypto", "macro"]

function validate(userId, type) {
  if (userId === null || userId === undefined || userId === "") {
    throw new Error("Brak zalogowanego użytkownika.")
  }

  if (!TYPES.includes(type)) {
    throw new Error("Nieprawidłowy typ ulubionych.")
  }
}

function getKey(userId, type) {
  validate(userId, type)
  return `${PREFIX}:${userId}:${type}`
}

function itemId(item) {
  return String(item?.id || item?.symbol || "")
}

function notify(userId, type) {
  window.dispatchEvent(
    new CustomEvent(EVENT_NAME, {
      detail: {
        userId: String(userId),
        type,
      },
    })
  )
}

// ----------------------------------------------------------------------------
// Tryb "local" (localStorage) — bez zmian względem poprzedniej wersji
// ----------------------------------------------------------------------------

function readLocal(userId, type) {
  try {
    const saved = localStorage.getItem(getKey(userId, type))
    const result = saved ? JSON.parse(saved) : []
    return Array.isArray(result) ? result : []
  } catch {
    return []
  }
}

function saveLocal(userId, type, items) {
  localStorage.setItem(getKey(userId, type), JSON.stringify(items))
  notify(userId, type)
}

// ----------------------------------------------------------------------------
// Tryb "api" (backend)
// ----------------------------------------------------------------------------

async function apiRequest(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY)

  if (!token) {
    throw new Error("Zaloguj się, aby korzystać z ulubionych.")
  }

  let response

  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    })
  } catch {
    throw new Error("Nie można połączyć się z serwerem.")
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Sesja wygasła. Zaloguj się ponownie.")
    }

    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : "Nie udało się zapisać ulubionych."
    )
  }

  return Array.isArray(data) ? data : []
}

// ----------------------------------------------------------------------------
// Publiczne funkcje (sygnatury bez zmian)
// ----------------------------------------------------------------------------

export async function getFavorites(userId, type) {
  if (PROVIDER === "api") {
    validate(userId, type)
    return apiRequest(`/api/favorites/${type}`)
  }

  return readLocal(userId, type)
}

export async function addFavorite(userId, type, item) {
  const id = itemId(item)

  if (!id) {
    throw new Error("Element nie ma identyfikatora.")
  }

  if (PROVIDER === "api") {
    validate(userId, type)
    const updated = await apiRequest(`/api/favorites/${type}`, {
      method: "POST",
      body: JSON.stringify(item),
    })
    notify(userId, type)
    return updated
  }

  const current = readLocal(userId, type)

  if (current.some((entry) => itemId(entry) === id)) {
    return current
  }

  const updated = [...current, item]
  saveLocal(userId, type, updated)

  return updated
}

export async function removeFavorite(userId, type, id) {
  if (PROVIDER === "api") {
    validate(userId, type)
    const updated = await apiRequest(
      `/api/favorites/${type}/${encodeURIComponent(String(id))}`,
      { method: "DELETE" }
    )
    notify(userId, type)
    return updated
  }

  const updated = readLocal(userId, type).filter(
    (entry) => itemId(entry) !== String(id)
  )

  saveLocal(userId, type, updated)

  return updated
}

export function subscribeToFavorites(callback) {
  const handleChange = (event) => callback(event.detail)

  const handleStorage = (event) => {
    if (event.key?.startsWith(PREFIX)) {
      callback(null)
    }
  }

  window.addEventListener(EVENT_NAME, handleChange)
  window.addEventListener("storage", handleStorage)

  return () => {
    window.removeEventListener(EVENT_NAME, handleChange)
    window.removeEventListener("storage", handleStorage)
  }
}

export function getFavoriteId(item) {
  return itemId(item)
}
