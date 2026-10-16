import {
  Activity,
  Brain,
  Pill,
  Stethoscope,
} from "lucide-react"
import { motion } from "framer-motion"

const suggestions = [
  { label: "Mes symptômes", icon: Stethoscope },
  { label: "Médicaments", icon: Pill },
  { label: "Conseils santé", icon: Activity },
  { label: "Santé mentale", icon: Brain },
]

type SuggestionChipsProps = {
  onSelect: (value: string) => void
  isDarkMode: boolean
}

function SuggestionChips({
  onSelect,
  isDarkMode
}: SuggestionChipsProps) {
  return (
    <motion.div
      className="flex flex-wrap gap-2"
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren: 0.08,
          },
        },
      }}
    >
      {suggestions.map((suggestion) => {
        const Icon = suggestion.icon

        return (
          <motion.button
            key={suggestion.label}
            onClick={() => onSelect(suggestion.label)}
            variants={{
              hidden: {
                opacity: 0,
                y: 8,
              },
              visible: {
                opacity: 1,
                y: 0,
              },
            }}
            whileHover={{
              y: -2,
              scale: 1.02,
            }}
            whileTap={{
              scale: 0.97,
            }}
            className={`
              flex items-center gap-2
              px-3 md:px-4
              py-2 md:py-2.5
              rounded-xl
              text-sm
              transition
              ${
                isDarkMode
                  ? "bg-slate-800/80 border border-slate-700 text-slate-300 hover:bg-slate-700 hover:border-teal-500 hover:text-teal-300"
                  : "bg-white/70 border border-slate-200 text-slate-600 hover:bg-white hover:border-teal-300 hover:text-teal-600"
              }
            `}
          >
            <Icon size={16} />
            {suggestion.label}
          </motion.button>
        )
      })}
    </motion.div>
  )
}

export default SuggestionChips