import { motion } from "framer-motion"
type DoctorIllustrationProps = {
  isDarkMode: boolean
}
function DoctorIllustration({
  isDarkMode,
}: DoctorIllustrationProps) {
  return (
    <motion.div
      className="pointer-events-none absolute right-[4%] bottom-[8%] z-0 hidden lg:block"
      initial={{ opacity: 0, y: 20 }}
      animate={{
        opacity: 0.28,
        y: [0, -8, 0],
      }}
      transition={{
        opacity: {
          duration: 1,
        },
        y: {
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        },
      }}
    >
      <svg
        width="300"
        height="360"
        viewBox="0 0 300 360"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* halo */}
        <circle
          cx="150"
          cy="175"
          r="125"
          stroke="currentColor"
          strokeWidth="2"
          strokeDasharray="8 10"
          className="text-teal-300"
        />

        {/* tête */}
        <circle
          cx="150"
          cy="85"
          r="42"
          stroke="currentColor"
          strokeWidth="4"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* cheveux */}
        <path
          d="M115 78C119 45 143 35 164 45C181 52 190 65 187 82"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* oreille gauche */}
        <path
          d="M109 82C100 80 99 94 108 97"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* oreille droite */}
        <path
          d="M191 82C200 80 201 94 192 97"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* yeux */}
        <circle
          cx="135"
          cy="85"
          r="3"
          fill="currentColor"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        <circle
          cx="165"
          cy="85"
          r="3"
          fill="currentColor"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* sourire */}
        <path
          d="M137 103C145 111 155 111 163 103"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* cou */}
        <path
          d="M136 123V138M164 123V138"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* corps / blouse */}
        <path
          d="M136 136L104 150C91 156 83 170 82 188L75 292"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        <path
          d="M164 136L196 150C209 156 217 170 218 188L225 292"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* col */}
        <path
          d="M136 136L150 158L164 136"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinejoin="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* stéthoscope */}
        <path
          d="M119 153C119 177 129 188 143 188C157 188 166 177 166 153"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-sky-400"}
        />

        <circle
          cx="143"
          cy="188"
          r="7"
          stroke="currentColor"
          strokeWidth="3"
          className={isDarkMode ? "text-teal-300" : "text-sky-400"}
        />

        {/* poche */}
        <path
          d="M174 220H204V255H174"
          stroke="currentColor"
          strokeWidth="3"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* bras gauche */}
        <path
          d="M103 157C88 177 76 198 68 220"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* main gauche */}
        <circle
          cx="67"
          cy="223"
          r="9"
          stroke="currentColor"
          strokeWidth="3"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* bras droit */}
        <path
          d="M197 158C214 176 226 194 236 213"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* tablette */}
        <rect
          x="205"
          y="205"
          width="48"
          height="64"
          rx="5"
          transform="rotate(-8 205 205)"
          stroke="currentColor"
          strokeWidth="3"
          className={isDarkMode ? "text-teal-300" : "text-sky-400"}
        />

        {/* petite croix médicale */}
        <path
          d="M224 220V236M216 228H232"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-sky-400"}
        />

        {/* jambes */}
        <path
          d="M115 292L108 340M185 292L192 340"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />

        {/* petits éléments décoratifs */}
        <path
          d="M38 130V150M28 140H48"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className={isDarkMode ? "text-teal-300" : "text-sky-300"}
        />

        <path
          d="M258 110C258 110 266 118 258 126C250 118 258 110 258 110Z"
          stroke="currentColor"
          strokeWidth="2"
          className={isDarkMode ? "text-teal-300" : "text-teal-400"}
        />
      </svg>
    </motion.div>
  )
}

export default DoctorIllustration