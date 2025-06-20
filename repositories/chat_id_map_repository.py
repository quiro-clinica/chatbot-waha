from sqlalchemy.orm import Session
from models import ChatIdMap

def get_real_chat_id(db: Session, chat_id_lid: str):
    """Busca no banco o número real baseado no @lid"""
    resultado = db.query(ChatIdMap).filter_by(chat_id_lid=chat_id_lid).first()
    return resultado.chat_id_real if resultado else None
