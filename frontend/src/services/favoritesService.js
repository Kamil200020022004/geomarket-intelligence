
const PREFIX = "geomarket:favorites:v1"
const EVENT_NAME = "geomarket:favorites:changed"

const PROVIDER = import.meta.env.VITE_FAVORITES_PROVIDER || "local"

const TYPES = ["stock", "crypto", "macro"]

function getKey(userId, type) {
  if (userId === null || userId === undefined || userId === "") {
    throw new Error("Brak zalogowanego użytkownika.")
  }

  if (!TYPES.includes(type)) {
    throw new Error("Nieprawidłowy typ ulubionych.")
  }

  return `${PREFIX}:${userId}:${type}`
}

function itemId(item) {
  return String(item?.id || item?.symbol || "")
}

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
  localStorage.setItem(
    getKey(userId, type),
    JSON.stringify(items)
  )

  window.dispatchEvent(
    new CustomEvent(EVENT_NAME, {
      detail: {
        userId: String(userId),
        type,
      },
    })
  )
}

function apiNotConfigured() {
  throw new Error(
    "Backend Sebastiana nie został jeszcze podłączony."
  )
}

export async function getFavorites(userId, type) {
  if (PROVIDER === "api") return apiNotConfigured()
  return readLocal(userId, type)
}

export async function addFavorite(userId, type, item) {
  if (PROVIDER === "api") return apiNotConfigured()

  const id = itemId(item)

  if (!id) {
    throw new Error("Element nie ma identyfikatora.")
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
  if (PROVIDER === "api") return apiNotConfigured()

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
