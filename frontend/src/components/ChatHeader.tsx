import { ShieldCheck, MoreVertical, Trash2, Moon, Info } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import BotAvatar from "./BotAvatar"
import { useState } from "react"

type ChatHeaderProps = {
  onClear: () => void
  isDarkMode: boolean
  onToggleDarkMode: () => void
}
function ChatHeader({ onClear, isDarkMode, onToggleDarkMode }: ChatHeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isAboutOpen, setIsAboutOpen] = useState(false)

  return (
    <motion.header
      initial={{
        opacity: 0,
        y: -10,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.4,
      }}
      className="relative flex items-center justify-between px-4 py-4 md:px-7 md:py-6 shrink-0"
    >
      <div className="flex items-center gap-4">
        <BotAvatar />

        <div>
          <h1
            className={`text-[15px] font-semibold tracking-tight ${
              isDarkMode ? "text-white" : "text-slate-800"
            }`}
          >
            MediBot
          </h1>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs font-medium text-emerald-600">
              <ShieldCheck size={14} />
              <span>Assistant médical</span>
            </div>

            <span className="w-1 h-1 rounded-full bg-slate-300" />

            <div className="flex items-center gap-1.5">
              <span className="relative flex w-2 h-2">
                <span className="absolute inline-flex w-full h-full rounded-full bg-emerald-400 opacity-60 animate-ping" />
                <span className="relative inline-flex w-2 h-2 rounded-full bg-emerald-500" />
              </span>

              <span className="text-xs text-slate-400">
                En ligne
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="relative">
        <motion.button
          onClick={() => setIsMenuOpen((current) => !current)}
          whileHover={{
            scale: 1.05,
            backgroundColor: "rgba(241,245,249,0.8)",
          }}
          whileTap={{
            scale: 0.95,
          }}
          className="w-10 h-10 rounded-xl transition flex items-center justify-center"
        >
          <MoreVertical
            size={20}
            className="text-slate-500"
          />
        </motion.button>

        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{
                opacity: 0,
                y: -5,
                scale: 0.95,
              }}
              animate={{
                opacity: 1,
                y: 0,
                scale: 1,
              }}
              exit={{
                opacity: 0,
                y: -5,
                scale: 0.95,
              }}
              transition={{
                duration: 0.15,
              }}
              className={`
                absolute
                right-0
                top-12
                z-50
                w-52
                p-2
                rounded-2xl
                backdrop-blur-xl
                shadow-xl
                ${
                  isDarkMode
                    ? "bg-slate-900/95 border border-slate-700"
                    : "bg-white/90 border border-slate-200"
                }
              `}
            >
              <button
                onClick={() => {
                  onClear()
                  setIsMenuOpen(false)
                }}
                className={`
                  w-full
                  flex
                  items-center
                  gap-3
                  px-3
                  py-2.5
                  rounded-xl
                  text-sm
                  transition
                  ${
                    isDarkMode
                      ? "text-slate-300 hover:bg-slate-800 hover:text-white"
                      : "text-slate-600 hover:bg-slate-100"
                  }
                `}
              >
                <Trash2 size={16} />
                <span>Effacer la conversation</span>
              </button>

              <button 
              onClick={() => {
                onToggleDarkMode()
                setIsMenuOpen(false)
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition ${
                isDarkMode
                  ? "text-slate-300 hover:bg-slate-800 hover:text-white"
                  : "text-slate-600 hover:bg-slate-100"
              }`}>
                <Moon size={16} />
                <span>{isDarkMode ? "Mode clair" : "Mode sombre"}</span>
              </button>

             <button
              onClick={() => {
                setIsAboutOpen(true)
                setIsMenuOpen(false)
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition ${
                isDarkMode
                  ? "text-slate-300 hover:bg-slate-800 hover:text-white"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              <Info size={16} />
              <span>À propos de MediBot</span>
            </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <AnimatePresence>
  {isAboutOpen && (
    <motion.div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/20 backdrop-blur-sm p-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={() => setIsAboutOpen(false)}
    >
      <motion.div
        initial={{
          opacity: 0,
          scale: 0.9,
          y: 20,
        }}
        animate={{
          opacity: 1,
          scale: 1,
          y: 0,
        }}
        exit={{
          opacity: 0,
          scale: 0.9,
          y: 20,
        }}
        transition={{
          duration: 0.25,
          ease: "easeOut",
        }}
        onClick={(event) => event.stopPropagation()}
        className={`
          w-full
          max-w-md
          rounded-3xl
          backdrop-blur-xl
          shadow-2xl
          p-7
          transition-colors
          ${
            isDarkMode
              ? "bg-slate-900/95 border border-slate-700"
              : "bg-white/95 border border-white"
          }
        `}
      >
        <div className="flex items-center gap-4 mb-5">
          <BotAvatar />

          <div>
            <h2
              className={`text-lg font-semibold ${
                isDarkMode ? "text-white" : "text-slate-800"
              }`}
            >
              MediBot
            </h2>

            <p className="text-sm text-teal-600">
              Assistant médical intelligent
            </p>
          </div>
        </div>

        <p
          className={`text-sm leading-6 mb-6 ${
            isDarkMode ? "text-slate-400" : "text-slate-500"
          }`}
        >
          MediBot est un assistant conversationnel conçu pour
          vous aider à comprendre vos symptômes et obtenir des
          informations générales sur votre santé.
        </p>

        <div className={`
          rounded-2xl
          p-4
          mb-6
          ${
            isDarkMode
              ? "bg-slate-800/80 border border-slate-700"
              : "bg-slate-50 border border-slate-100"
          }
        `}>
          <p
            className={`text-xs leading-5 ${
              isDarkMode ? "text-slate-400" : "text-slate-400"
            }`}
          >
            ⚠️ MediBot ne remplace pas un médecin ou un professionnel
            de santé. En cas d'urgence ou de symptômes graves,
            contactez immédiatement un professionnel de santé.
          </p>
        </div>

        <button
          onClick={() => setIsAboutOpen(false)}
          className="
            w-full
            py-3
            rounded-xl
            bg-gradient-to-r
            from-teal-500
            to-sky-500
            text-white
            text-sm
            font-medium
            hover:opacity-90
            transition
          "
        >
          Fermer
        </button>
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
    </motion.header>
  )
}

export default ChatHeader