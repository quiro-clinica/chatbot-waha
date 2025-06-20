from fastapi import APIRouter, Request, Depends
from services.evolution_api import send_whatsapp_message
from core.ai_bot import AIBot

from sqlalchemy.orm import Session
from database import SessionLocal

from repositories import chat_id_map_repository
from redis_tools.redis_pending_ids import get_chat_id_from_redis, save_to_redis_if_absent
from redis_tools.redis_queue import enqueue, is_user_in_queue, get_first_in_queue
from services.atendimento import finalizar_atendimento
from redis_tools.redis_pending_messages import save_pending_message


bot = AIBot()
router = APIRouter()

# Função auxiliar para injetar a sessão do banco no endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):

    payload = await request.json()
    data = payload.get("data", {})
    chat_id = data.get("key", {}).get("remoteJid")
    message = data.get("message", {}).get("conversation")
    pushname = data.get("pushName", "Usuário")
    status   = data.get("status", "").upper()

    if status in {"ERROR", "PENDING"}:
        print(f"[IGNORADO] {chat_id}  status={status}  (sem texto)")
        return {"status": "ignored_error_stub"}
    
    if not chat_id or not message or "@g.us" in chat_id:
        return {"status": "ignorado"}
    
    if not chat_id.endswith("@s.whatsapp.net"):
        print("Chat ID fora do padrão, tentando buscar o número real...")
        # 1º Tentativa: banco de dados
        real_chat_id = chat_id_map_repository.get_real_chat_id(db, chat_id)  # Usando o método correto
        
        if real_chat_id:
            print(f"Substituindo chat_id por número real do banco: {real_chat_id}")
            chat_id = real_chat_id

        else:
            print(f"Nenhum número real encontrado para {chat_id}, tentando buscar no Redis...")

            redis_result = get_chat_id_from_redis(chat_id) 

            if not redis_result:
                save_to_redis_if_absent(chat_id, pushname)
                
            else:
                print(f"[Redis DB4] Chat ID {chat_id} já registrado. Ignorando mensagem.")
            
            return {'status': 'ignorado'}
                    

    # Adiciona à fila, se ainda não estiver
    if not is_user_in_queue(chat_id):
        enqueue(chat_id)
        print(f"Usuário {chat_id} adicionado à fila.")

    # Permite atendimento apenas se for o primeiro da fila
    first_in_line = get_first_in_queue()
    if chat_id != first_in_line:
        print(f"Usuário {chat_id} não é o primeiro da fila. Mensagem não será respondida.")
        save_pending_message(chat_id, message)
        
        return {"status": "aguardando_na_fila"}

    resposta_ia = bot.invoke(message, chat_id=chat_id)

    send_whatsapp_message(
        number=chat_id,
        text=resposta_ia
    )
    if bot.contem_palavras_chave(resposta_ia):
        finalizar_atendimento(chat_id)

    return {'status': 'ok'}
