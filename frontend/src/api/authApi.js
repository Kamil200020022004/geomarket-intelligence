const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
const TOKEN_KEY = "geomarket_auth_token"

async function request(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY)
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = typeof data.detail === "string"
      ? data.detail
      : "Wystąpił błąd. Spróbuj ponownie."
    throw new Error(message)
  }
  return data
}

export async function loginUser(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  })
  localStorage.setItem(TOKEN_KEY, data.access_token)
  return data.user
}

export async function registerUser(name, email, password) {
  const data = await request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  })
  localStorage.setItem(TOKEN_KEY, data.access_token)
  return data.user
}

export async function getCurrentUser() {
  if (!localStorage.getItem(TOKEN_KEY)) return null
  try {
    const data = await request("/auth/me")
    return data.user
  } catch {
    localStorage.removeItem(TOKEN_KEY)
    return null
  }
}

export async function logoutUser() {
  try {
    await request("/auth/logout", { method: "POST" })
  } finally {
    localStorage.removeItem(TOKEN_KEY)
  }
}

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY)
}
