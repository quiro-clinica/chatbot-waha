from redis import Redis
from datetime import datetime

# DB 10 é exclusivo para controle de timeout
redis_timeout = Redis(host="redis", port=6379, db=10, decode_responses=True)

def salvar_timestamp(chat_id: str):
    """
    Salva o timestamp atual da última interação do usuário.
    """
    now = datetime.utcnow().timestamp()
    redis_timeout.set(f"ultimo_uso:{chat_id}", now)

def obter_timestamp(chat_id: str) -> float | None:
    """
    Recupera o timestamp salvo para um chat_id.
    """
    ts = redis_timeout.get(f"ultimo_uso:{chat_id}")
    return float(ts) if ts else None

def remover_timestamp(chat_id: str):
    """
    Remove o timestamp do usuário após finalizar atendimento.
    """
    redis_timeout.delete(f"ultimo_uso:{chat_id}")
