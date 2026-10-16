import { Send } from "lucide-react"
import { motion } from "framer-motion"

type ChatInputProps = {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  isDarkMode: boolean
  isTyping?: boolean
}

function ChatInput({
  value,
  onChange,
  onSend,
  isDarkMode,
  isTyping = false,
}: ChatInputProps) {
  return (
    <motion.div
  initial={{
    opacity: 0,
    y: 10,
  }}
  animate={{
    opacity: 1,
    y: 0,
  }}
  transition={{
    duration: 0.4,
  }}
  className={`
    flex items-center gap-3
    p-2
    mt-3 md:mt-4
    rounded-2xl
    shadow-sm
    transition-all
    duration-300
    ${
      isDarkMode
        ? "bg-slate-800/90 border border-slate-700"
        : "bg-white/80 border border-slate-200"
    }
  `}
>
      
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !isTyping) {
            onSend()
          }
        }}
        placeholder="Écrivez votre message..."
        className={`
          flex-1
          px-4 py-3
          bg-transparent
          outline-none
          text-sm
          ${
            isDarkMode
              ? "text-slate-100 placeholder:text-slate-500"
              : "text-slate-700 placeholder:text-slate-400"
          }
        `}
      />

      <motion.button
        onClick={onSend}
        disabled={!value.trim() || isTyping}
        whileHover={value.trim() && !isTyping ? { scale: 1.05 } : {}}
        whileTap={value.trim() && !isTyping ? { scale: 0.95 } : {}}
        className={`w-11 h-11 rounded-xl text-white flex items-center justify-center transition ${
          value.trim() && !isTyping
            ? "bg-teal-500 hover:bg-teal-600 shadow-md shadow-teal-500/20"
            : "bg-slate-200 cursor-not-allowed"
        }`}
      >
        <Send size={18} />
      </motion.button>

    </motion.div>
  )
}

export default ChatInput
