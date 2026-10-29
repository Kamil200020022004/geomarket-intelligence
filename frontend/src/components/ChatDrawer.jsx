import { useState } from "react"

function ChatDrawer({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      role: "model",
      content:
        "Cześć! Jestem asystentem AI platformy GeoMarket Intelligence. Możesz zapytać mnie o rynki, dane, wydarzenia geopolityczne lub wykresy.",
    },
  ])

  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  if (!isOpen) return null

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      role: "user",
      content: input,
    }

    const updatedMessages = [...messages, userMessage]

    setMessages(updatedMessages)
    setInput("")
    setIsLoading(true)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage.content,
          history: updatedMessages,
        }),
      })

      if (!response.ok) {
        throw new Error("Backend error")
      }

      const data = await response.json()

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "model",
          content: data.response,
        },
      ])
    } catch (error) {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "model",
          content:
            "Nie udało się połączyć z backendem AI. Sprawdź, czy backend działa pod adresem http://127.0.0.1:8000.",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleSend()
    }
  }

  return (
    <div className="fixed bottom-24 right-6 z-50 flex h-[620px] w-[380px] flex-col overflow-hidden rounded-3xl border border-slate-700/80 bg-slate-950 shadow-2xl shadow-cyan-950/50">
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900 px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="relative flex h-11 w-11 items-center justify-center rounded-full bg-cyan-400 text-xl text-slate-950">
            🤖
            <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-slate-900 bg-emerald-400"></span>
          </div>

          <div>
            <p className="font-semibold text-slate-100">
              GeoMarket AI
            </p>

            <p className="text-xs text-slate-400">
              Połączony z backendem AI
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="text-xl text-cyan-400 transition hover:text-cyan-300"
        >
          ×
        </button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto bg-slate-950 px-4 py-5">
        <div className="flex justify-center">
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">
            Dzisiaj
          </span>
        </div>

        {messages.map((message, index) => {
          const isUser = message.role === "user"

          return (
            <div
              key={index}
              className={`max-w-[85%] rounded-3xl px-4 py-3 text-sm leading-6 ${
                isUser
                  ? "ml-auto rounded-br-md bg-cyan-400 font-medium text-slate-950"
                  : "rounded-bl-md bg-slate-800 text-slate-100"
              }`}
            >
              {message.content}
            </div>
          )
        })}

        {isLoading && (
          <div className="max-w-[80%] rounded-3xl rounded-bl-md bg-slate-800 px-4 py-3 text-sm text-slate-400">
            AI analizuje odpowiedź...
          </div>
        )}
      </div>

      <div className="border-t border-slate-800 bg-slate-900 p-3">
        <div className="flex items-center gap-2">
          <button className="flex h-10 w-10 items-center justify-center rounded-full text-cyan-400 transition hover:bg-slate-800">
            +
          </button>

          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Aa"
            className="h-10 flex-1 rounded-full border border-slate-700 bg-slate-800 px-4 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-400"
          />

          <button
            onClick={handleSend}
            disabled={isLoading}
            className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-400 text-slate-950 transition hover:bg-cyan-300 disabled:opacity-50"
          >
            ➤
          </button>
        </div>

        <p className="mt-2 text-center text-[11px] text-slate-500">
          To nie jest porada inwestycyjna. Odpowiedzi mają charakter informacyjny.
        </p>
      </div>
    </div>
  )
}

export default ChatDrawer