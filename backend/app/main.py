from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.data.loader import load_data
from app.vectorstore.faiss_store import FAISSStore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://ai-frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 init vector DB
data = load_data("data/data_enriched_v3.json")
store = FAISSStore(data)

# injection (si besoin ailleurs)
import app.api.routes as routes
routes.store_instance = store

# ✅ routes
app.include_router(router)
