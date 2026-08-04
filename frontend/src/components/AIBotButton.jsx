function AIBotButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="animate-float-soft fixed bottom-6 right-6 z-40 flex h-16 w-16 items-center justify-center rounded-full bg-cyan-400 text-2xl text-slate-950 shadow-2xl shadow-cyan-500/40 ring-4 ring-cyan-400/10 transition hover:scale-110 hover:bg-cyan-300"
    >
      🤖
    </button>
  )
}

export default AIBotButton