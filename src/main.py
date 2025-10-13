from fastapi import FastAPI
from .router.chat_router import router as chat_router
from .router.notification_router import router as notification_router

app = FastAPI()

app.include_router(chat_router)
app.include_router(notification_router)