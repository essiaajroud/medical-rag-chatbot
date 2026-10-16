import json
import requests
import time


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"


#Nettoyer réponse LLM (extra texte → JSON)
def extract_json(text):
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except:
        return None


#  Appel Ollama avec retry
def enrich_entry(q, a, retries=3):
    prompt = f"""
    You are a medical assistant.

    Given:
    Question: {q}
    Answer: {a}

    Generate JSON ONLY with this format:
    {{
        "keywords": ["..."],
        "category": "symptom | disease | emergency | prevention",
        "severity": "low | medium | high",
        "related_questions": ["...", "..."]
    }}
    """

    for attempt in range(retries):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )

            result = response.json()["response"]
            parsed = extract_json(result)

            if parsed:
                return parsed

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(1)

    return {
        "keywords": [],
        "category": "unknown",
        "severity": "unknown",
        "related_questions": []
    }


# Enrich dataset complet
def enrich_dataset(input_file, output_file):
    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    enriched = []

    for i, item in enumerate(data):
        print(f"Processing {i}...")

        enriched_data = enrich_entry(item["question"], item["answer"])

        enriched.append({
            "id": i,
            "question": item["question"],
            "answer": item["answer"],
            "keywords": enriched_data.get("keywords", []),
            "category": enriched_data.get("category", ""),
            "severity": enriched_data.get("severity", ""),
            "related_questions": enriched_data.get("related_questions", [])
        })

        time.sleep(0.5)  # éviter surcharge CPU

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)



if __name__ == "__main__":
    enrich_dataset("conversation.json", "data_enriched.json")