
const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

export interface MediBotSource {
  name?: string;
  title?: string;
  label?: string;
  url?: string;
  href?: string;
}

export interface MediBotResponse {
  answer: string;
  sources: MediBotSource[];
}

export interface ChatHistoryItem {
  sender: "user" | "bot";
  message: string;
}

export async function askMediBot(
  question: string,
  history: ChatHistoryItem[] = [],
  signal?: AbortSignal
): Promise<MediBotResponse> {
  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      question,
      history: history.slice(-12),
    }),
    signal,
  });

  if (!response.ok) {
    const details = await response.text();

    console.error("Erreur API MediBot :", {
      status: response.status,
      details,
    });

    throw new Error(`http-${response.status}: ${details}`);
  }

  const data: unknown = await response.json();

  if (
    typeof data !== "object" ||
    data === null ||
    !("answer" in data) ||
    typeof data.answer !== "string"
  ) {
    throw new Error("La réponse du serveur MediBot est invalide.");
  }

  const sources =
    "sources" in data && Array.isArray(data.sources)
      ? data.sources
      : [];

  return {
    answer: data.answer,
    sources,
  };
}
