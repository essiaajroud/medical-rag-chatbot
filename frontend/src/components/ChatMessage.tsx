import { motion } from "framer-motion"
import BotAvatar from "./BotAvatar"

type ChatMessageProps = {
  message: string
  sender: "bot" | "user"
  time?: string
  isDarkMode: boolean
  sources?: unknown[]
}

function ChatMessage({ message, sender, time, isDarkMode, sources = [] }: ChatMessageProps) {
  const isBot = sender === "bot"
  const displaySources = sources.flatMap((source) => {
    if (!source || typeof source !== "object") return []
    const item = source as Record<string, unknown>
    const title = [item.name, item.title, item.label].find((value) => typeof value === "string" && value.trim())
    const rawUrl = item.url ?? item.href
    let url: string | undefined
    if (typeof rawUrl === "string") {
      try {
        const parsed = new URL(rawUrl)
        if (parsed.protocol === "http:" || parsed.protocol === "https:") url = parsed.toString()
      } catch { /* Ignore malformed source URLs. */ }
    }
    if (!title && !url) return []
    return [{ title: typeof title === "string" ? title : url!, url }]
  })

  return (

  <motion.div
    initial={{
      opacity: 0,
      x: isBot ? -15 : 15,
      y: 8,
      scale: 0.98,
    }}
    animate={{
      opacity: 1,
      x: 0,
      y: 0,
      scale: 1,
    }}
    transition={{
      duration: 0.35,
      ease: "easeOut",
    }}
    className={`flex items-end gap-2 ${
      isBot ? "justify-start" : "justify-end"
    }`}
  >
    {isBot && (
      <div className="scale-[0.55] origin-bottom">
        <BotAvatar />
      </div>
    )}

    <div
      className={`max-w-[85%] md:max-w-[70%] px-4 py-3 rounded-2xl ${
        isBot
        ? isDarkMode
          ? "bg-slate-800/90 text-slate-200 border border-slate-700 rounded-tl-md shadow-sm"
          : "bg-white/80 text-slate-700 border border-slate-100 rounded-tl-md shadow-sm"
          : "bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-tr-md shadow-md shadow-teal-500/10"
      }`}
    >
      <p className="text-sm leading-relaxed">
        {message}
      </p>

      {isBot && displaySources.length > 0 && (
        <div className={`mt-3 border-t pt-2 ${isDarkMode ? "border-slate-700" : "border-slate-200"}`}>
          <p className="text-xs font-medium mb-1">Sources</p>
          <ul className="space-y-1">
            {displaySources.map((source, index) => (
              <li key={`${source.url ?? source.title}-${index}`} className="text-xs break-all">
                {source.url ? <a href={source.url} target="_blank" rel="noopener noreferrer" className="underline text-teal-600 dark:text-teal-300">{source.title}</a> : source.title}
              </li>
            ))}
          </ul>
        </div>
      )}

      {time && (
        <span
          className={`block mt-1 text-[10px] ${
            isBot
            ? isDarkMode
              ? "text-slate-500"
              : "text-slate-400"
            : "text-teal-100"
          }`}
        >
          {time}
        </span>
      )}
    </div>
  </motion.div>
)
}

export default ChatMessage
