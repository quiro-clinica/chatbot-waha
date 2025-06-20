import redis
import os
import json

redis_pending = redis.Redis.from_url("redis://redis:6379/4", decode_responses=True)

def get_chat_id_from_redis(chat_id_lid: str) -> str | None:
    """
    Busca o nome salvo no Redis DB4 baseado no chat_id @lid.
    """
    try:
        data = redis_pending.get(chat_id_lid)
        if data:
            info = json.loads(data)
            return info.get("pushname")
    except Exception as e:
        print(f"[Redis DB4] Erro ao buscar: {e}")
    return None

def save_to_redis_if_absent(chat_id_lid: str, pushname: str):
    """
    Salva no Redis DB4 se ainda não existir.
    """
    try:
        if not redis_pending.exists(chat_id_lid):
            redis_pending.set(chat_id_lid, json.dumps({"pushname": pushname}))
            print(f"[Redis DB4] Salvo: {chat_id_lid} -> {pushname}")
        else:
            print(f"[Redis DB4] Já existe: {chat_id_lid}")
    except Exception as e:
        print(f"[Redis DB4] Erro ao salvar: {e}")

#Da interface:
def get_all_chat_ids():
    """
    Lista todas as chaves (chat_ids) salvas no Redis DB4.
    """
    try:
        return redis_pending.keys("*")
    except Exception as e:
        print(f"[Redis DB4] Erro ao buscar chaves: {e}")
        return []

def delete_chat_id(chat_id: str):
    """
    Remove uma chave específica do Redis DB4.
    """
    try:
        redis_pending.delete(chat_id)
        print(f"[Redis DB4] Deletado: {chat_id}")
    except Exception as e:
        print(f"[Redis DB4] Erro ao deletar: {e}")

