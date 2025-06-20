import redis

r = redis.Redis(host="redis", port=6379, db=8, decode_responses=True)

PENDING_MESSAGES_KEY = "pending_messages"

def save_pending_message(chat_id: str, message: str):
    r.hset(PENDING_MESSAGES_KEY, chat_id, message)

def get_pending_message(chat_id: str) -> str | None:
    return r.hget(PENDING_MESSAGES_KEY, chat_id)

def delete_pending_message(chat_id: str):
    r.hdel(PENDING_MESSAGES_KEY, chat_id)
