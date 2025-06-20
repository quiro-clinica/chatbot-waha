# redis_client.py
import redis

redis_bot = redis.Redis.from_url("redis://redis:6379/5", decode_responses=True)

def add_to_history(user_id: str, message: str, max_messages: int = 10):
    """Adiciona uma mensagem ao histórico do usuário (lista FIFO)"""
    key = f"{user_id}:history"
    redis_bot.rpush(key, message)
    if redis_bot.llen(key) > max_messages:
        redis_bot.lpop(key)

def get_history(user_id: str):
    """Pega o histórico do usuário"""
    return redis_bot.lrange(f"{user_id}:history", 0, -1)

def clear_history(user_id: str):
    """Limpa o histórico do usuário"""
    redis_bot.delete(f"{user_id}:history")
