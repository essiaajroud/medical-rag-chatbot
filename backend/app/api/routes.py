from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent import run_agent
from app.core.language_utils import get_greeting

router = APIRouter()
store_instance = None


class ChatTurn(BaseModel):
    sender: str
    message: str = Field(max_length=2000)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=12)


async def _process_question(question: str, history=None):
    question = question.strip()

    if not question:
        return {"answer": "Veuillez saisir une question.", "sources": []}

    greeting = get_greeting(question)
    if greeting:
        return {"answer": greeting, "sources": []}

    if history:
        result = await run_agent(
            question,
            store_instance,
            history=history,
        )
    else:
        result = await run_agent(question, store_instance)

    if isinstance(result, dict):
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        return {
            "answer": answer if isinstance(answer, str) else "",
            "sources": sources if isinstance(sources, list) else [],
        }

    return {"answer": str(result), "sources": []}


# Ancien endpoint : GET /ask?question=...
@router.get("/ask")
async def ask(question: str):
    return await _process_question(question)


# Nouvel endpoint : POST /ask avec historique
@router.post("/ask")
async def ask_with_history(request: AskRequest):
    history = [
        turn.model_dump()
        for turn in request.history
        if turn.sender in {"user", "bot"}
    ]

    return await _process_question(request.question, history)
