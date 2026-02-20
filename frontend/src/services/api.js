const API_BASE = import.meta.env.VITE_API_BASE || ""

export async function analyzeNotes(notes_text) {
  const res = await fetch(`${API_BASE}/api/analyze/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notes_text }),
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API ${res.status}: ${text}`)
  }

  return res.json()
}
