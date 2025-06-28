from fastapi import APIRouter, Request, Depends

from services.waha_api import Waha
from sqlalchemy.orm import Session
from database import SessionLocal

from core.ai_bot import AIBot
from logger_config import logger  # ✅ Importa o logger
from services.atendimento import finalizar_atendimento
from validadores import mensagem_invalida

from redis_tools.redis_queue import enqueue, is_user_in_queue, get_first_in_queue
from redis_tools.redis_pending_messages import save_pending_message
from redis_tools.redis_timeout import salvar_timestamp


waha = Waha()
bot = AIBot()
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):

    payload = await request.json()

    data = payload.get("payload", {})
    chat_id = data.get("from")
    message = data.get("body")

    if mensagem_invalida(chat_id, message):
        return {"status": "ignorado"}  # ⛔️ sem log, sem print

    
    logger.info(f"[Webhook Recebido] {data}")  # ✅ substitui print

    if not is_user_in_queue(chat_id):
        enqueue(chat_id)
        logger.info(f"Usuário {chat_id} adicionado à fila.")

    first_in_line = get_first_in_queue()
    if chat_id != first_in_line:
        logger.info(f"Usuário {chat_id} não é o primeiro da fila. Mensagem não será respondida.")
        save_pending_message(chat_id, message)
        return {"status": "aguardando_na_fila"}

    try:
        resposta_ia = bot.invoke(message, chat_id=chat_id)
        waha.send_whatsapp_message(chat_id, resposta_ia)
        salvar_timestamp(chat_id)
    except Exception as e:
        logger.error(f"[ERRO][IA] Falha ao responder {chat_id}: {e}")
        return {"status": "erro_ia"}

    if bot.contem_palavras_chave(resposta_ia):
        finalizar_atendimento(chat_id)

    return {'status': 'ok'}
