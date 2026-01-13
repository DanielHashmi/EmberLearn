# Routers package
from .auth import router as auth_router
from .chat import router as chat_router
from .progress import router as progress_router
from .exercises import router as exercises_router
from .execute import router as execute_router

__all__ = [
    "auth_router",
    "chat_router", 
    "progress_router",
    "exercises_router",
    "execute_router",
]
