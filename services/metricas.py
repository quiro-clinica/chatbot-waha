from sqlalchemy.orm import Session
from models import ConversaMetrica
from datetime import datetime

def registrar_inicio(db: Session, chat_id: str):
    existe = db.query(ConversaMetrica).filter_by(chat_id=chat_id, status=None).first()
    if not existe:
        nova = ConversaMetrica(chat_id=chat_id)
        db.add(nova)
        db.commit()

def atualizar_status(db: Session, chat_id: str, status: str):
    metrica = db.query(ConversaMetrica).filter_by(chat_id=chat_id, status=None).first()
    if metrica:
        metrica.fim_em = datetime.utcnow()
        metrica.status = status
        db.commit()
