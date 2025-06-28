import asyncio
from fastapi import FastAPI

from routes.webhook import router as webhook_router
from services.monitor_timeout import monitorar_timeout
from contextlib import asynccontextmanager
from logger_config import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o monitoramento como tarefa de segundo plano
    logger.info("💡 Iniciando monitoramento de timeout...")
    asyncio.create_task(monitorar_timeout())
    yield

app = FastAPI(lifespan=lifespan)

# Inclui as rotas do seu webhook
app.include_router(webhook_router)
