import { useState, useEffect, useRef } from "react";
import "./App.css";
import ChatHeader from "./components/ChatHeader";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import TypingIndicator from "./components/TypingIndicator";
import SuggestionChips from "./components/SuggestionChips";
import { motion } from "framer-motion";
import DoctorIllustration from "./components/DoctorIllustration"
import type { Message } from "./types/chat";  
import { askMediBot } from "./services/mediBotApi";

  const getCurrentTime = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
function App() {
  
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: "bot" as const,
      message:
        "Bonjour 👋 Je suis MediBot. Comment puis-je vous aider aujourd'hui ?",
      time: getCurrentTime(),
    },
  ]);

  const [isTyping, setIsTyping] = useState(false);
  const requestInFlight = useRef(false);
  const activeRequest = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
  messagesEndRef.current?.scrollIntoView({
    behavior: "smooth",
  })
}, [messages, isTyping])

const clearConversation = () => {
  activeRequest.current?.abort();
  activeRequest.current = null;
  requestInFlight.current = false;
  setIsTyping(false);
  setMessages([
    {
      id: Date.now(),
      sender: "bot" as const,
      message:
        "Bonjour 👋 Je suis MediBot. Comment puis-je vous aider aujourd'hui ?",
      time: getCurrentTime(),
    },
  ])
}

const sendMessage = async () => {
  const userMessage = message.trim();

  if (!userMessage || requestInFlight.current) return;

  requestInFlight.current = true;

  const controller = new AbortController();
  activeRequest.current = controller;

  
  const history = messages
    .slice(-12)
    .map((item) => ({
      sender: item.sender,
      message: item.message,
    }))
    .filter(
      (item) => item.sender === "user" || item.sender === "bot"
    );


  setMessages((current) => [
    ...current,
    {
      id: Date.now(),
      sender: "user",
      message: userMessage,
      time: getCurrentTime(),
    },
  ]);

  setMessage("");
  setIsTyping(true);

  const timeout = window.setTimeout(() => {
    controller.abort();
  }, 60000);

  try {
    // Appel du service API MediBot
    const data = await askMediBot(
      userMessage,
      history,
      controller.signal
    );

    // Ajouter la réponse et les sources au chat
    const botMessage: Message = {
      id: Date.now(),
      sender: "bot",
      message: data.answer,
      time: getCurrentTime(),
      sources: data.sources,
    };

    setMessages((current) => [...current, botMessage]);
  } catch (error) {
    // Si la conversation a été effacée pendant la requête,
    // ne pas ajouter une erreur à la nouvelle conversation.
    if (controller.signal.aborted && activeRequest.current !== controller) {
      return;
    }

    const errorMessage = controller.signal.aborted
      ? "La demande a pris trop de temps. Veuillez réessayer."
      : error instanceof TypeError
        ? "Impossible de joindre MediBot. Vérifiez que le serveur est démarré puis réessayez."
        : error instanceof Error && error.message.startsWith("http-")
          ? "Le serveur MediBot a rencontré une erreur. Veuillez réessayer."
          : "La réponse du serveur est invalide. Veuillez réessayer.";

    setMessages((current) => [
      ...current,
      {
        id: Date.now(),
        sender: "bot",
        message: errorMessage,
        time: getCurrentTime(),
      },
    ]);
  } finally {
    window.clearTimeout(timeout);

    if (activeRequest.current === controller) {
      activeRequest.current = null;
      requestInFlight.current = false;
      setIsTyping(false);
    }
  }
};

const [isDarkMode, setIsDarkMode] = useState(() => {
  return localStorage.getItem("medibot-theme") === "dark"
})
useEffect(() => {
  localStorage.setItem(
    "medibot-theme",
    isDarkMode ? "dark" : "light"
  )
}, [isDarkMode])
return (
  <main
    className={`
        h-dvh
        w-full
        flex
        items-center
        justify-center
        relative
        overflow-hidden
        p-3
        md:p-6
        transition-colors
        duration-500
        ${
          isDarkMode
            ? "bg-gradient-to-br from-slate-950 via-slate-900 to-teal-950 text-slate-100"
            : "bg-gradient-to-br from-sky-100 via-white to-teal-100 text-slate-800"
        }
      `}
    >
      <DoctorIllustration isDarkMode={isDarkMode}/>
      <motion.div
        className="absolute top-20 left-20 w-20 h-20 rounded-full bg-teal-200/40 blur-2xl"
        animate={{
          y: [0, -20, 0],
          x: [0, 10, 0],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <div className="absolute bottom-20 right-20 w-32 h-32 rounded-full bg-sky-300/40 blur-3xl" />

      <motion.div
        className="absolute top-1/3 right-10 w-4 h-4 rounded-full bg-teal-400/60"
        animate={{
          y: [0, -15, 0],
          x: [0, -8, 0],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
/>

      <motion.div className="absolute bottom-1/3 left-10 w-3 h-3 rounded-full bg-sky-400/60" 
      animate={{
          y: [0, -30, 0],
          x: [0, 15, 0],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        }}/>
      <motion.div
        className="absolute w-[500px] h-[500px] bg-teal-300/20 rounded-full blur-3xl -top-40 -left-40"
        animate={{
          x: [0, 30, 0],
          y: [0, 20, 0],
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute w-[450px] h-[450px] bg-sky-300/20 rounded-full blur-3xl"
        animate={{
          x: [0, -25, 0],
          y: [0, -20, 0],
          scale: [1, 1.06, 1],
        }}
        transition={{
          duration: 14,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute w-3 h-3 bg-white/70 rounded-full top-[20%] left-[25%] shadow-lg"
        animate={{
          y: [0, -12, 0],
          opacity: [0.5, 1, 0.5],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute w-2 h-2 bg-white/80 rounded-full top-[65%] right-[20%] shadow-lg"
        animate={{
          y: [0, 15, 0],
          opacity: [0.4, 0.9, 0.4],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute w-4 h-4 bg-teal-200/60 rounded-full bottom-[15%] left-[18%]"
        animate={{
          y: [0, -18, 0],
          x: [0, 8, 0],
          opacity: [0.4, 0.8, 0.4],
        }}
        transition={{
          duration: 7,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <div className="w-full max-w-4xl">
        <div
          className={`
            relative
            w-full
            h-[calc(100dvh-1.5rem)]
            md:h-[calc(100dvh-3rem)]
            max-h-[850px]
            rounded-[2rem]
            backdrop-blur-2xl
            border
            shadow-[0_30px_80px_rgba(15,118,110,0.15)]
            overflow-hidden
            flex
            flex-col
            transition-all
            duration-500
            ${
              isDarkMode
                ? "bg-slate-900/75 border-slate-700/60 shadow-black/30"
                : "bg-white/65 border-white/80"
            }
          `}
        >
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-transparent via-teal-400/50 to-transparent rounded-full" />
          <ChatHeader onClear={clearConversation} isDarkMode={isDarkMode} onToggleDarkMode={() => setIsDarkMode((current) => !current)} />
          <div className="flex-1 min-h-0 px-4 pb-4 md:px-6 md:pb-6 flex flex-col">
            <div className="flex-1 min-h-0 flex flex-col gap-4 overflow-y-auto pr-1">
              {messages.map((item) => (
                <ChatMessage
                  key={item.id}
                  sender={item.sender}
                  message={item.message}
                  time={item.time}
                  sources={item.sources}
                  isDarkMode={isDarkMode}
                />
              ))}
              {isTyping && <TypingIndicator isDarkMode={isDarkMode}/>}
              <div ref={messagesEndRef} />
            </div>
            {messages.length <= 3 && (  
              <SuggestionChips
                onSelect={(value) => {
                  setMessage(value);
                }}
                isDarkMode={isDarkMode}
              />)}
            <ChatInput
              value={message}
              onChange={setMessage}
              onSend={sendMessage}
              isDarkMode={isDarkMode}
              isTyping={isTyping}
            />
          </div>
        </div>
      </div>
    </main>
  );
}

export default App;
