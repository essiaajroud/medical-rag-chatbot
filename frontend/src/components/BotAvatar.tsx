import { HeartPulse } from "lucide-react"
import { motion } from "framer-motion"

function BotAvatar() {
  return (
    <div className="relative w-14 h-14">
      
      <motion.div
        className="absolute inset-0 rounded-2xl bg-gradient-to-br from-teal-400 to-sky-500 blur-md"
        animate={{
          opacity: [0.2, 0.45, 0.2],
          scale: [0.95, 1.05, 0.95],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <div className="relative w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-400 to-sky-500 flex items-center justify-center shadow-lg">
        
        <motion.div
          animate={{
            scale: [1, 1.08, 1],
          }}
          transition={{
            duration: 2.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <HeartPulse
            size={28}
            strokeWidth={2}
            className="text-white"
          />
        </motion.div>

      </div>

      <motion.span
        className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-400 border-[3px] border-white"
        animate={{
          scale: [1, 1.15, 1],
          opacity: [0.8, 1, 0.8],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

    </div>
  )
}

export default BotAvatar