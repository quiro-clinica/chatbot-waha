import redis
from redis_tools.redis_client_history import clear_history

# Conexão com Redis DB 7 para a fila
r = redis.Redis(host="redis", port=6379, db=7, decode_responses=True)

QUEUE_KEY = "chatbot_queue"

def enqueue(chat_id: str):
    """Adiciona o usuário à fila, se ainda não estiver nela"""
    if not r.sismember("chatbot_queue_set", chat_id):
        r.rpush(QUEUE_KEY, chat_id)
        r.sadd("chatbot_queue_set", chat_id)

def is_user_in_queue(chat_id: str) -> bool:
    """Verifica se o usuário está na fila"""
    return r.sismember("chatbot_queue_set", chat_id)

def get_first_in_queue() -> str | None:
    """Retorna o primeiro usuário da fila (ou None se estiver vazia)"""
    return r.lindex(QUEUE_KEY, 0)

def dequeue():
    """Remove o primeiro da fila, limpa o histórico e retorna o próximo (se houver)."""
    # Remove o primeiro da fila
    chat_id = r.lpop(QUEUE_KEY)
    if chat_id:
        print(f"[QUEUE] Removendo {chat_id} da fila e limpando histórico...")
        clear_history(chat_id)  # limpeza de mensagens passadas
    return chat_id

def remove_from_set(chat_id: str):
    r.srem("chatbot_queue_set", chat_id)


