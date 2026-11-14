from fastapi import APIRouter
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.comparative import router as comparative_router
from backend.app.api.v1.summary import router as summary_router
from backend.app.api.v1.sessions import router as sessions_router

api_router = APIRouter()
api_router.include_router(documents_router)
api_router.include_router(chat_router)
api_router.include_router(comparative_router)
api_router.include_router(summary_router)
api_router.include_router(sessions_router)

