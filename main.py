from fastapi import FastAPI
from routes.webhook import router as webhook_router

from threading import Thread
from services.monitor_timeout import monitorar_timeout

Thread(target=monitorar_timeout, daemon=True).start()

app = FastAPI()
app.include_router(webhook_router)