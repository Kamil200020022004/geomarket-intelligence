const API_URL = (
  import.meta.env.VITE_AI_API_URL ||
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8001"
).replace(/\/$/, "")

export async function apiGet(endpoint) {
  const response = await fetch(`${API_URL}${endpoint}`)

  if (!response.ok) {
    throw new Error(`API error: ${endpoint} (${response.status})`)
  }

  return response.json()
}

export async function apiPost(endpoint, body) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`API error: ${endpoint} (${response.status})`)
  }

  return response.json()
}