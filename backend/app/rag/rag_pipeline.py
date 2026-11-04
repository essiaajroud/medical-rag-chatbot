from app.llm.llm_service import generate
from app.core.config import TOP_K, RAG_CONTEXT_THRESHOLD
import httpx
from urllib.parse import urlparse
from app.core.language_utils import detect_language, language_name
import json
import re

def _source_from_document(doc):
    """Return a public HTTP(S) citation, or None for missing/untrusted metadata."""
    name = doc.get("source_name")
    url = doc.get("source_url")
    if not isinstance(name, str) or not isinstance(url, str):
        return None
    name = name.strip()
    url = url.strip()
    if not name or name.casefold() in {"to be verified", "unknown", "unverified"}:
        return None
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return None
        if parsed.username or parsed.password:
            return None
    except ValueError:
        return None
    return {"name": name, "url": url}


def _unique_sources(documents):
    """Collecte les sources HTTP(S) valides sans doublons."""
    sources = []
    seen_urls = set()

    for doc in documents:
        source = _source_from_document(doc)

        if not source:
            continue

        url_key = source["url"].casefold()

        if url_key not in seen_urls:
            seen_urls.add(url_key)
            sources.append(source)

    return sources


async def rag_answer(query, store, retrieval=None):
    language_code = detect_language(query)
    response_language = language_name(language_code)
    scores, documents = retrieval if retrieval is not None else store.search(query, TOP_K)
    
    # IndexFlatIP + embeddings normalisés :
    # les scores sont des similarités cosinus.
    relevant_documents = [
        (float(score), doc)
        for score, doc in zip(scores, documents)
        if float(score) >= RAG_CONTEXT_THRESHOLD
    ]

    print("\n========== RAG FILTER ==========")
    print(f"QUESTION: {query}")
    print(f"SEUIL DE CONTEXTE: {RAG_CONTEXT_THRESHOLD}")
    print(f"SCORES: {scores}")
    print(
        "DOCUMENTS RETENUS:",
        [doc.get("id") for _, doc in relevant_documents]
    )
    print("================================")

    
    if not relevant_documents:
        fallback_messages = {
            "French": (
                "Je n’ai pas trouvé suffisamment d’informations "
                "dans ma base médicale pour répondre de façon fiable. "
                "Veuillez consulter un professionnel de santé."
            ),
            "English": (
                "I could not find enough information in my medical "
                "database to answer reliably. Please consult a "
                "healthcare professional."
            ),
            "Arabic": (
                "لم أجد معلومات كافية في قاعدة البيانات الطبية "
                "للإجابة بشكل موثوق. يُرجى استشارة مختص في الرعاية الصحية."
            ),
        }

        return {
            "answer": fallback_messages.get(
                response_language,
                fallback_messages["English"],
            ),
            "sources": [],
        }


    selected_documents = [
        doc for _, doc in relevant_documents
    ]

    context_parts = []

    for i, doc in enumerate(selected_documents, start=1):
        keywords = doc.get("keywords", [])
        related = doc.get("related_questions", [])

        if not isinstance(keywords, list):
            keywords = []
        if not isinstance(related, list):
            related = []

        part = (
            f"[DOCUMENT {i}]\n"
            f"Question : {doc.get('question', '')}\n"
            f"Réponse : {doc.get('answer', '')}\n"
            f"Mots-clés : {', '.join(map(str, keywords))}\n"
            f"Questions liées : {', '.join(map(str, related))}"
        )

        source = _source_from_document(doc)
        if source:
            part += (
                f"\nSource : {source['name']}\n"
                f"URL : {source['url']}"
            )

        context_parts.append(part)

    context = "\n\n".join(context_parts)
    sources = _unique_sources(selected_documents)

    prompt = f"""
        You are MediBot, a medical information assistant.
        Respond entirely in {response_language}.

        Use only medical facts supported by the supplied document answers.

        Rules:
        - Never invent medical facts, sources, titles, or URLs.
        - Never treat symptoms as confirmation of a diagnosis.
        - If the documents do not support an answer, state that clearly.
        - Select only document IDs that directly support the medical
        information in your answer.
        - Related questions and keywords are retrieval aids, not proof.
        - Do not select a document merely because its topic is similar.
        - Do not include a greeting unless the user greeted you.
        - For emergency symptoms, give clear and immediate safety advice.

        Return ONLY a valid JSON object in this exact structure:
        {{
        "answer": "Your complete answer in {response_language}",
        "used_document_ids": [1, 2]
        }}

        Use an empty list for used_document_ids if no document supports
        the answer. IDs must refer to the numbered documents below.

        Documents:
        {context}

        User question:
        {query}
        """

    try:
        raw = await generate(prompt)

        if not isinstance(raw, str) or not raw.strip():
            raise ValueError("Le modèle a retourné une réponse vide.")

        # Tolère les blocs Markdown autour du JSON.
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)

        answer = result.get("answer")
        used_ids = result.get("used_document_ids", [])

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Le JSON ne contient pas de réponse valide.")

        if not isinstance(used_ids, list):
            used_ids = []

        valid_ids = {
            doc_id
            for doc_id in range(1, len(selected_documents) + 1)
        }

        used_ids = list(dict.fromkeys(
            doc_id
            for doc_id in used_ids
            if type(doc_id) is int and doc_id in valid_ids
        ))

        used_documents = [
            selected_documents[doc_id - 1]
            for doc_id in used_ids
        ]
        print("DOCUMENTS UTILISÉS :", [
         doc.get("id") for doc in used_documents
        ])
        print("SOURCES RETOURNÉES :", _unique_sources(used_documents))

        return {
            "answer": answer.strip(),
            "sources": _unique_sources(used_documents),
        }

    except (httpx.TimeoutException, httpx.NetworkError) as exc:
        print(f"RAG NETWORK ERROR: {exc}")

    except Exception as exc:
        print(f"RAG GENERATION ERROR: {exc}")

    failure_messages = {
        "French": "Je ne peux pas générer une réponse fiable pour le moment. Veuillez réessayer plus tard.",
        "English": "I cannot generate a reliable answer right now. Please try again later.",
        "Arabic": "لا أستطيع إنشاء إجابة موثوقة الآن. يُرجى المحاولة مرة أخرى لاحقًا.",
    }
    return {
        "answer": failure_messages.get(response_language, failure_messages["English"]),
        "sources": [],
    }





async def general_answer(query):
    language_code = detect_language(query)
    response_language = language_name(language_code)

    prompt = f"""
    You are MediBot, a medical information assistant.

    LANGUAGE RULES:
    - Respond entirely in {response_language}.
    - Use the same language as the user's latest question.
    - Do not switch to French automatically.

    MEDICAL SAFETY:
    - Provide general medical information, not a definitive diagnosis.
    - Never invent citations or claim to have consulted documents
      that were not provided.
    - Do not recommend personalized medication or dosages without
      appropriate medical context.
    - If you are uncertain, clearly explain your limitations.
    - For potentially life-threatening symptoms, advise seeking
      emergency medical assistance immediately.

    User question:
    {query}

    Answer in {response_language}:
    """

    try:
        answer = await generate(prompt)

        if isinstance(answer, str) and answer.strip():
            return answer.strip()

        raise ValueError("The model returned an empty response.")

    except Exception as exc:
        print(f"GENERAL ANSWER ERROR: {exc}")

        fallback_messages = {
            "French": (
                "Je suis désolé, je ne peux pas générer une réponse "
                "pour le moment."
            ),
            "English": (
                "Sorry, I cannot generate a response right now."
            ),
            "Arabic": (
                "عذرًا، لا أستطيع إنشاء إجابة في الوقت الحالي."
            ),
        }

        return fallback_messages.get(
            response_language,
            fallback_messages["French"],
        )


