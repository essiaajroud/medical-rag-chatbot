import re
import unicodedata
from typing import TypedDict

from langgraph.graph import StateGraph
from app.core.config import SIM_THRESHOLD, TOP_K

from app.rag.rag_pipeline import rag_answer, general_answer
from app.core.language_utils import detect_language




class AgentState(TypedDict):
    question: str
    store: object
    decision: str
    emergency_type: str
    response: object
    retrieval: object
    history: list[dict]
    clarification: str




def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^\w']+", " ", text, flags=re.UNICODE).strip()


_EMERGENCY_PATTERNS = {
    "breathing_arrest": (
        r"\b(not breathing normally|not breathing|isn't breathing|stopped breathing|abnormal breathing)\b",
        r"\b(ne respire pas normalement|ne respire plus|respiration anormale|respiration arretee)\b",
    ),
    "cardiac": (
        r"\b(chest pain|chest discomfort|chest pressure|tightness in (my |the )?chest|suspected heart attack|having a heart attack)\b",
        r"\b(douleur (thoracique|dans la poitrine)|oppression thoracique|serrement (dans la poitrine|thoracique)|suspicion d'infarctus|je fais un infarctus)\b",
    ),
    
    "breathing": (
        r"\b(can't breathe|cannot breathe|unable to breathe|struggling to breathe|severe shortness of breath|severe difficulty breathing|difficulty breathing|shortness of breath)\b",
        r"\b(ne peux pas respirer|n'arrive pas a respirer|difficulte respiratoire severe|difficulte a respirer|respiration tres difficile|essoufflement severe|grandes difficultes a respirer|difficultes severes a respirer)\b",
    ),

    "breathing_ar": (
        r"(?!)",
        r"(صعوبة\s+(شديدة\s+|حادة\s+|بالغة\s+)?في التنفس|ضيق\s+(شديد\s+|حاد\s+)?التنفس|لا\s+أستطيع\s+التنفس|لا\s+استطيع\s+التنفس|أعاني\s+من\s+صعوبة\s+في\s+التنفس|اعاني\s+من\s+صعوبة\s+في\s+التنفس)",
    ),

    "stroke": (
        r"\b(face is drooping|facial drooping|face drooping|sudden (slurred speech|speech (problem|difficulty)|weakness on one side)|suspected (a )?stroke|possible (a )?stroke)\b",
        r"\b(visage (qui s'affaisse|s'affaisse)|bouche (deformee|qui tombe)|difficulte soudaine a parler|du mal a parler|trouble soudain de la parole|faiblesse soudaine d'un (bras|cote)|suspicion d'avc|avc suspect)\b",
    ),
    "unconsciousness": (
        r"\b(unconscious|unresponsive|passed out|fainted|not waking up)\b",
        r"\b(perte de connaissance|perdu connaissance|inconscient|inconsciente|ne repond plus|ne se reveille pas|evanoui|evanouie)\b",
    ),
    "other": (
        r"\b(uncontrolled bleeding|severe bleeding|severe allergic reaction|swelling of (the )?(tongue|throat)|overdose|poisoning|seizure|convulsion)\b",
        r"\b(saignement abondant|hemorragie|reaction allergique grave|gonflement (de la langue|de la gorge)|surdose|empoisonnement|convulsion)\b",
    ),
    
    "cardiac_ar": (
        r"(?!)",
        r"(ألم|وجع)( شديد| حاد| قوي)? (في )?(الصدر|صدري)"
        r"|ضيق في الصدر|ضغط في الصدر|ألم صدري",
    ),
    "stroke_ar": (
    r"(?!)",
    r"(هبوط|تدل[يّ]?)\s*(في\s*)?(الوجه|وجهي)"
    r"|اعوجاج\s*(في\s*)?(الوجه|الفم)"
    r"|صعوبة\s*(مفاجئة\s*)?(في\s*)?(الكلام|التكلم|النطق)"
    r"|ثقل\s*(في\s*)?(اللسان|الكلام)"
    r"|ضعف\s*(مفاجئ\s*)?(في\s*)?(الذراع|اليد|الساق|الرجل)"
    r"|خدر\s*(مفاجئ\s*)?(في\s*)?(الوجه|الذراع|اليد|الساق)"
    r"|فقدان\s*(مفاجئ\s*)?(للتوازن|للنظر)"
    ),

}


def detect_emergency_type(query: str) -> str | None:
    normalized = _normalize(query)
    for emergency_type, patterns in _EMERGENCY_PATTERNS.items():
        if any(re.search(pattern, normalized) for pattern in patterns):
            return emergency_type
    return None


def is_emergency_question(query: str) -> bool:
    """Keep the existing helper API while detecting English and French emergencies."""
    return detect_emergency_type(query) is not None


_OUT_OF_SCOPE_PATTERNS = (
    r"\b(roman empire|history of (the )?roman|python (program|script|code)|write (a )?(python )?(program|script|code)|debug (my )?code|javascript|programming|computer code|capital of|football|movie review)\b",
    r"\b(empire romain|histoire (de l'empire romain|romaine)|programme python|code python|ecris (un )?(programme|script|code)|programmation|javascript|informatique|football|critique de film)\b",
    r"(?:اكتب|اكتبلي|اكتب لي|أنشئ|اعطني|أعطني).{0,40}(?:بايثون|بايثون|برمجة|كود|سكريبت)",
    r"(?:برنامج|كود|سكريبت).{0,40}(?:بايثون|برمجة|ترتيب قائمة)",
)

_SOURCE_REQUEST_PATTERNS = (
    r"\b(give|show|provide|list|share|send).{0,50}\b(sources?|references?|citations?)\b",
    r"\b(sources?|references?|citations?)\b.{0,30}\b(for|of) (your|the) answer\b",
    r"\b(donne|affiche|fournis|liste|partage).{0,50}\b(sources?|references?|citations?)\b",
    r"\b(sources?|references?|citations?)\b.{0,30}\b(de|pour) (ta|votre|la) reponse\b",
)


def is_source_request(query: str) -> bool:
    normalized = _normalize(query)
    return any(re.search(pattern, normalized) for pattern in _SOURCE_REQUEST_PATTERNS)

_MEDICAL_TERMS = (
    "medical", "health", "symptom", "pain", "fever", "cough", "flu", "cold", "infection", "sepsis",
    "medicine", "medication", "drug", "dose", "pregnan", "allerg", "disease", "illness", "stroke",
    "doctor", "hospital", "treatment", "wound", "rash", "headache", "stomach", "heart", "sick", "dizzy", "injury", "injured", "bleeding", "sore throat", "throat",
    "sante", "medical", "symptome", "douleur", "fievre", "toux", "grippe", "rhume",
    "infection", "medicament", "traitement", "dose", "enceinte", "grossesse", "allergie",
    "maladie", "docteur", "medecin", "hopital", "plaie", "eruption", "maux", "coeur",
    "respirer", "respiration", "sang", "vomissement", "diarrhee", "enfant", "vaccin", "avc",
    "malade", "mal", "gorge", "ventre", "tete", "vertige", "fatigue", "poitrine", "blesse",
    "dehydration", "dehydrated", "hydration", "fluid loss",
    "thirst", "urination", "urine", "blood pressure",
    "hypertension", "diabetes", "glucose", "blood sugar","diabetes",
    "diabetic","blood glucose","blood sugar","glucose","hypertension",
    "high blood pressure","blood pressure","dehydration","dehydrated",
    "hydration","thirst","urination","urine","vomiting",
    "diarrhea","diarrhoea","nausea","drink fluids","oral rehydration","high blood sugar",
    "blood glucose","frequent urination","thirsty","pee","urinate","hypertension",
    "hyperglycemia","hyperglycaemia","high blood sugar","high blood glucose","elevated blood sugar",
    "elevated blood glucose","blood glucose","blood sugar","glucose level",
    "glycemia","glycémie élevée","hyperglycémie",
    "glycemie", "glycemie elevee", "hyperglycemie", "diabete", "soif",
    "mictions frequentes", "uriner", "diabetique", "glycemie",
    "lupus", "cancer", "tumor", "tumour", "exhaust", "tiredness", "tired",
    "ارتفاع السكر", "ارتفاع السكر في الدم", "السكري", "أعراض", "العطش", "التبول",
    "مرض", "ألم", "حمى", "سعال", "دواء", "علاج", "صداع", "ضغط الدم",
)



_AMBIGUOUS_FOLLOW_UP_PATTERNS = (
    # English
    r"\bbetween them\b",
    r"\bbetween these two\b",
    r"\bbetween those two\b",
    r"\bbetween these things\b",
    r"\bbetween those things\b",
    r"\bbetween the two\b",
    r"\brelationship between them\b",
    r"\bconnection between them\b",

    # French
    r"\b(lien|relation|rapport)\b.{0,30}\b(entre eux|entre elles|entre les deux|entre ces deux)\b",
    r"\b(existe t il|y a t il)\b.{0,20}\b(un lien|une relation|un rapport)\b.{0,30}\b(entre eux|entre elles|entre les deux|entre ces deux)\b",

    # Arabic
    r"هل\s+(توجد|هناك|يوجد)\s+(علاقة|صلة)\s+بينهما",
    r"ما\s+(العلاقة|الصلة)\s+بينهما",
    r"هل\s+بينهما\s+(علاقة|صلة)",
)



def is_ambiguous_follow_up(query: str) -> bool:
    normalized = _normalize(query)
    return any(
        re.search(pattern, normalized)
        for pattern in _AMBIGUOUS_FOLLOW_UP_PATTERNS
    )


def is_context_dependent_follow_up(query: str) -> bool:
    normalized = _normalize(query)

    patterns = (
        # English
        r"^(and|what about|does it|can it|is it|do they|"
        r"does this|can this|what if)\b",
        r"\b(the same symptoms|those symptoms|these symptoms)\b",
        r"\b(what about it|how about it)\b",
        r"^(does|do|can|could|is|are)\b.{0,80}\b(the same|same symptoms)\b",
        # French
        r"^(et|qu'en est-il|qu'en est il|est-ce que|"
        r"est ce que|cela|ça|il|elle)\b",
        r"\b(les mêmes symptômes|les memes symptomes)\b",

        # Arabic
        r"^(وماذا عن|هل يسبب|هل تسبب|هل يمكن أن|"
        r"هل يمكن ان|وهل)\b",
        r"\bنفس الأعراض\b",
    )

    return any(re.search(pattern, normalized) for pattern in patterns)



_CONTEXT_TOPICS = {
    "diabetes": (
        "diabetes", "diabetic", "diabete",
        "السكري", "مرض السكري", "داء السكري",
    ),
    "dehydration": (
        "dehydration", "dehydrated", "deshydratation",
        "الجفاف", "جفاف", "نقص السوائل",
    ),
    "flu": (
        "influenza", "flu", "grippe",
        "الإنفلونزا", "الانفلونزا",
    ),
    "common cold": (
        "common cold", "rhume",
        "الزكام", "نزلة البرد", "الرشح",
    ),
    "hypertension": (
        "hypertension", "high blood pressure",
        "ضغط الدم", "ارتفاع ضغط الدم",
    ),
    "chest pain": (
        "chest pain", "chest pains", "pain in my chest",
        "ألم في الصدر", "ألم الصدر", "وجع الصدر",
    ),
    "stroke": (
        "stroke", "signs of a stroke", "warning signs of a stroke",
        "السكتة الدماغية", "الجلطة الدماغية", "أعراض السكتة الدماغية",
    ),
}

_TOPIC_LABELS = {
    "diabetes": {
        "en": "diabetes", "fr": "le diabète", "ar": "السكري",
    },
    "dehydration": {
        "en": "dehydration", "fr": "la déshydratation", "ar": "الجفاف",
    },
    "flu": {
        "en": "the flu", "fr": "la grippe", "ar": "الإنفلونزا",
    },
    "common cold": {
        "en": "the common cold", "fr": "le rhume", "ar": "الزكام",
    },
    "hypertension": {
        "en": "high blood pressure", "fr": "l’hypertension", "ar": "ضغط الدم",
    },
    "chest pain": {
        "en": "chest pain",
        "fr": "douleur thoracique", "ar": "ألم في الصدر",
    },
    "stroke": {
        "en": "stroke",
        "fr": "AVC", "ar": "السكتة الدماغية",
    },
}

missing_labels = set(_CONTEXT_TOPICS) - set(_TOPIC_LABELS)

if missing_labels:
    print("Topics missing labels:", missing_labels)

def _mentioned_topics(text: str) -> set[str]:
    normalized = _normalize(text)
    found = set()

    for topic, aliases in _CONTEXT_TOPICS.items():
        for alias in aliases:
            alias_normalized = _normalize(alias)
            pattern = rf"(?<!\w){re.escape(alias_normalized)}(?!\w)"

            if re.search(pattern, normalized):
                found.add(topic)
                break

    return found



def _resolve_follow_up(query: str, history: list[dict]):
    """
    Resolve short follow-up questions using recent conversation context.
    If the intended medical topic remains ambiguous, ask for clarification.
    """
    # An explicit topic in the current question takes priority.
    current_topics = _mentioned_topics(query)
    if current_topics:
        return query, None

    if not is_context_dependent_follow_up(query):
        return query, None

    language = detect_language(query)

    # Search backwards for the most recent user message that explicitly
    # mentions a supported medical topic.
    recent_topics = set()

    for turn in reversed(history):
        if not isinstance(turn, dict):
            continue

        if turn.get("sender") != "user":
            continue

        message = turn.get("message", "")
        if not isinstance(message, str):
            continue

        topics = _mentioned_topics(message)

        if topics:
            recent_topics = topics
            break

    # No previous medical topic was found.
    if not recent_topics:
        clarification = {
            "en": "Which medical condition are you referring to?",
            "fr": "De quelle maladie ou situation médicale parlez-vous ?",
            "ar": "إلى أي مرض أو حالة طبية تشير؟",
        }
        return None, clarification.get(language, clarification["en"])

    # The most recent relevant user message itself mentioned multiple topics.
    if len(recent_topics) > 1:
        labels = [
            _TOPIC_LABELS.get(topic, {}).get(language, topic)
            for topic in sorted(recent_topics)
        ]

        if language == "ar":
            clarification = "للتأكد، هل تقصد " + " أم ".join(labels) + "؟"
        elif language == "fr":
            clarification = (
                "Pour éviter toute confusion, parlez-vous de "
                + " ou de ".join(labels)
                + " ?"
            )
        else:
            clarification = (
                "To avoid confusion, are you referring to "
                + " or ".join(labels)
                + "?"
            )

        return None, clarification

    topic = next(iter(recent_topics))
    label = _TOPIC_LABELS.get(topic, {}).get(language, topic)

    # Keep the user's wording and add the missing topic for retrieval.
    prefixes = {
        "en": f"Regarding {label}: ",
        "fr": f"Concernant {label} : ",
        "ar": f"بخصوص {label}: ",
    }

    return prefixes.get(language, prefixes["en"]) + query, None



def classify_question(query: str) -> str:
    """Classify before retrieval so urgent and non-medical input cannot reach the LLM."""
    normalized = _normalize(query)

    if detect_emergency_type(query):
        return "emergency"

    if not normalized:
        return "unclear"

    if is_source_request(query):
        return "sources_request"

    if is_ambiguous_follow_up(query):
        return "unclear"

    if any(re.search(pattern, normalized) for pattern in _OUT_OF_SCOPE_PATTERNS):
        return "out_of_scope"

    # Arabic medical questions must be classified before generic
    # out-of-scope and random-text heuristics.
    is_arabic = any("\u0600" <= char <= "\u06ff" for char in query)

    if is_arabic:
        arabic_medical_terms = (
            "مرض", "أمراض", "طبي", "الصحة", "صحة",
            "أعراض", "عرض", "الجفاف", "السكري", "الإنفلونزا",
            "الزكام", "ضغط الدم", "ألم", "وجع", "حمى",
            "سعال", "صداع", "دوخة", "دوار", "علاج",
            "دواء", "أدوية", "التنفس", "ضيق التنفس",
            "القلب", "الصدر", "نزيف", "سكتة دماغية",
            "الجفاف", "العطش", "التبول", "القيء", "الإسهال",
        )

        if any(term in query for term in arabic_medical_terms):
            return "medical"

        return "unclear"

    words = normalized.split()

    if len(words) < 2:
        return "unclear"

    tokens = set(words)

    if any(
        term in tokens if len(term) <= 3 else term in normalized
        for term in _MEDICAL_TERMS
    ):
        return "medical"

    if len(words) <= 3:
        return "unclear"

    # Reject likely unintelligible Latin-script input.
    vowel_count = sum(char in "aeiouy" for char in normalized)
    letter_count = sum(char.isalpha() for char in normalized)

    if (
        len(words) >= 3
        and sum(any(vowel in word for vowel in "aeiouy") for word in words)
        / len(words) < 0.4
    ) or (
        letter_count >= 7
        and vowel_count / letter_count < 0.2
    ):
        return "unclear"

    return "out_of_scope"





async def router_node(state):
    original_query = state.get("question", "").strip()

    # 1. Emergency detection always uses the original user message.
    emergency_type = detect_emergency_type(original_query)
    if emergency_type:
        return {
            **state,
            "decision": "emergency",
            "emergency_type": emergency_type,
        }
    print("ORIGINAL QUESTION:", original_query)
    print("CONVERSATION HISTORY:", state.get("history", []))
    print("PREVIOUS TOPICS:", [
        _mentioned_topics(turn.get("message", ""))
        for turn in state.get("history", [])
        if isinstance(turn, dict) and turn.get("sender") == "user"
    ])

    # 2. Resolve context-dependent follow-ups conservatively.
    resolved_query, clarification = _resolve_follow_up(
        original_query,
        state.get("history", []),
    )
    print("RESOLVED QUERY:", resolved_query)
    print("CLARIFICATION:", clarification)

    if clarification:
        return {
            **state,
            "decision": "unclear",
            "clarification": clarification,
        }

    # Use the resolved question for classification and retrieval.
    query = resolved_query.strip()

    updated_state = {
        **state,
        "question": query,
    }

    intent = classify_question(query)

    if intent == "emergency":
        return {
            **updated_state,
            "decision": "emergency",
            "emergency_type": detect_emergency_type(query),
        }

    if intent == "sources_request":
        return {**updated_state, "decision": "sources_request"}

    if intent in {"out_of_scope", "unclear"}:
        return {**updated_state, "decision": intent}

    store = state.get("store")
    if store is None:
        return {**updated_state, "decision": "llm"}

    scores, docs = store.search(query, TOP_K)

    print("\n========== RAG ROUTER ==========")
    print(f"QUESTION: {query}")
    print(f"SEUIL ROUTEUR: {SIM_THRESHOLD}")

    for score, doc in zip(scores, docs):
        print(
            f"RAG CANDIDATE | score={float(score):.4f} "
            f"| id={doc.get('id')} "
            f"| question={doc.get('question', '')!r}"
        )

    print("================================")

    if (
        len(scores) > 0
        and len(docs) > 0
        and float(scores[0]) >= SIM_THRESHOLD
    ):
        return {
            **updated_state,
            "decision": "rag",
            "retrieval": (scores, docs),
        }

    return {**updated_state, "decision": "llm"}



def route_decision(state):
    return state["decision"]


_EMERGENCY_MESSAGES = {
    "breathing_arrest": (
        "Appelez immédiatement le numéro d’urgence local. Mettez le téléphone en haut-parleur et suivez sans délai les instructions du régulateur, notamment celles concernant la réanimation. Ne retardez pas l’appel."
    ),
    "cardiac": (
        "Une douleur thoracique peut signaler une urgence grave. Appelez immédiatement le numéro d’urgence local ou demandez à quelqu’un de le faire. Ne conduisez pas vous-même et ne retardez pas la demande d’aide."
    ),
    "breathing": (
        "Une difficulté respiratoire sévère est une urgence. Appelez immédiatement le numéro d’urgence local ou demandez à quelqu’un de le faire."
    ),
    "stroke": (
        "Un visage qui s’affaisse ou une difficulté soudaine à parler peut être un signe d’AVC. Appelez immédiatement le numéro d’urgence local, même si les symptômes s’atténuent."
    ),
    "unconsciousness": (
        "Une perte de connaissance ou une personne qui ne répond pas nécessite une aide immédiate. Appelez maintenant le numéro d’urgence local."
    ),
    "other": (
        "Ces symptômes peuvent nécessiter une aide médicale immédiate. Appelez le numéro d’urgence local ou demandez à quelqu’un de le faire."
    ),
}


async def rag_node(state):
    return {
        **state,
        "response": await rag_answer(
            state["question"], state["store"], retrieval=state.get("retrieval")
        ),
    }



async def llm_node(state):
    answer = await general_answer(state["question"])
    return {
        **state,
        "response": {"answer": answer, "sources": []},
    }



async def emergency_node(state):
    language = detect_language(state["question"])
    emergency_type = state.get("emergency_type")
    if language == "en":
        answer = "These symptoms may be a medical emergency. Call your local emergency number now."
        if emergency_type == "cardiac":
            answer = "Chest pain can signal a serious emergency. Call your local emergency number now. Do not drive yourself."
        elif emergency_type == "breathing":
            answer = "Severe difficulty breathing is an emergency. Call your local emergency number now."
        elif emergency_type == "stroke":
            answer = "A drooping face or sudden speech difficulty can be signs of a stroke. Call your local emergency number now."
    
    elif language == "ar":
        if emergency_type == "cardiac":
            answer = (
                "قد يشير ألم الصدر إلى حالة طبية خطيرة. "
                "اتصل فورًا برقم الطوارئ المحلي أو اطلب من شخص "
                "آخر الاتصال. لا تقد السيارة بنفسك."
            )
        elif emergency_type == "breathing":
            answer = (
                "صعوبة التنفس الشديدة حالة طارئة. "
                "اتصل فورًا برقم الطوارئ المحلي."
            )
        elif emergency_type == "stroke":
            answer = (
                "قد يكون تدلّي الوجه أو صعوبة الكلام المفاجئة "
                "علامة على سكتة دماغية. اتصل فورًا برقم الطوارئ "
                "لا تنتظر تحسن الأعراض، حتى لو اختفت."
            )
        elif emergency_type == "unconsciousness":
            answer = (
                "فقدان الوعي أو عدم الاستجابة يستدعي مساعدة فورية. "
                "اتصل الآن برقم الطوارئ المحلي."
            )
        else:
            answer = (
                "قد تتطلب هذه الأعراض مساعدة طبية فورية. "
                "اتصل برقم الطوارئ المحلي الآن."
            )

    else:
        answer = _EMERGENCY_MESSAGES.get(emergency_type, _EMERGENCY_MESSAGES["other"])
    return {**state, "response": answer}


async def out_of_scope_node(state):
    language = detect_language(state["question"])
    messages = {
        "fr": "Je suis MediBot, un assistant d’information médicale. Je peux vous aider pour une question liée à la santé, mais pas pour ce sujet.",
        "en": "I'm MediBot, a medical information assistant. I can help with health-related questions, but not this topic.",
        "ar": "أنا MediBot، مساعد للمعلومات الطبية. يمكنني المساعدة في الأسئلة الصحية، وليس في هذا الموضوع.",
    }
    return {**state, "response": messages[language]}





async def unclear_node(state):
    print("UNCLEAR NODE ENTERED")
    print("CLARIFICATION RECEIVED:", state.get("clarification"))

    clarification = state.get("clarification")

    if clarification:
        return {
            **state,
            "decision": "unclear",
            "response": clarification,
        }

    language = detect_language(state.get("question", ""))

    messages = {
        "en": (
            "I did not understand your message. "
            "Could you rephrase your question or clarify "
            "whether you mean diabetes, dehydration, "
            "or another medical condition?"
        ),
        "fr": (
            "Pouvez-vous préciser votre question ? "
            "Parlez-vous du diabète, de la déshydratation "
            "ou d'une autre situation médicale ?"
        ),
        "ar": (
            "هل يمكنك توضيح سؤالك؟ "
            "هل تقصد مرض السكري أم الجفاف أم حالة طبية أخرى؟"
        ),
    }

    return {
        **state,
        "response": messages.get(language, messages["en"]),
    }





async def sources_request_node(state):
    language = detect_language(state["question"])
    messages = {
        "fr": "Je n’ai pas accès aux sources d’une réponse précédente dans cette requête. Renvoyez la question médicale d’origine pour que je relance la recherche et fournisse les références disponibles.",
        "en": "I do not have access to sources from an earlier answer in this request. Send the original medical question again so I can search and provide available references.",
        "ar": "لا يمكنني الوصول إلى مصادر إجابة سابقة ضمن هذا الطلب. أرسل السؤال الطبي الأصلي مجددًا لأبحث وأقدم المراجع المتاحة.",
    }
    return {
        **state,
        "response": messages[language],
    }


builder = StateGraph(AgentState)
builder.add_node("router", router_node)
builder.add_node("rag", rag_node)
builder.add_node("llm", llm_node)
builder.add_node("emergency", emergency_node)
builder.add_node("out_of_scope", out_of_scope_node)
builder.add_node("unclear", unclear_node)
builder.add_node("sources_request", sources_request_node)
builder.set_entry_point("router")
builder.add_conditional_edges("router", route_decision, {
    "rag": "rag", "llm": "llm", "emergency": "emergency",
    "out_of_scope": "out_of_scope", "unclear": "unclear",
    "sources_request": "sources_request",
})
for node in ("rag", "llm", "emergency", "out_of_scope", "unclear", "sources_request"):
    builder.set_finish_point(node)
graph = builder.compile()



async def run_agent(query, store, history=None):
    result = await graph.ainvoke({
        "question": query,
        "store": store,
        "history": history or [],
    })

    response = result.get(
        "response",
        "Je ne peux pas répondre pour le moment."
    )

    if isinstance(response, dict):
        answer = response.get("answer")
        sources = response.get("sources", [])

        answer = (
            answer
            if isinstance(answer, str)
            else "Je ne peux pas répondre de façon fiable pour le moment."
        )
        sources = sources if isinstance(sources, list) else []

    else:
        answer = (
            response
            if isinstance(response, str)
            else str(response)
        )
        sources = []

    print("FINAL AGENT ANSWER:", answer)

    return {
        "answer": answer,
        "sources": sources,
    }
