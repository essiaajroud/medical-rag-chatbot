import { motion } from "framer-motion"

type TypingIndicatorProps = {
  isDarkMode: boolean
}

function TypingIndicator({
  isDarkMode,
}: TypingIndicatorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex justify-start"
    >
      <div className={`
        flex items-center gap-3
        px-4 py-3
        rounded-2xl
        rounded-tl-md
        shadow-sm
        ${
          isDarkMode
            ? "bg-slate-800/90 border border-slate-700"
            : "bg-white/80 border border-slate-100"
        }
      `}>
        
        <div className="flex gap-1.5">
          {[0, 1, 2].map((index) => (
            <motion.span
              key={index}
              className="w-1.5 h-1.5 rounded-full bg-teal-400"
              animate={{
                y: [0, -4, 0],
                opacity: [0.4, 1, 0.4],
              }}
              transition={{
                duration: 0.8,
                repeat: Infinity,
                delay: index * 0.15,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>

        <span
          className={`text-xs ${
            isDarkMode ? "text-slate-500" : "text-slate-400"
          }`}
        >
          MediBot écrit...
        </span>

      </div>
    </motion.div>
  )
}

export default TypingIndicator