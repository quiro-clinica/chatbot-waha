from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
from datetime import datetime

class ConversaMetrica(Base):
    __tablename__ = "metricas_conversas"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Text, nullable=False)
    inicio_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    fim_em = Column(DateTime, nullable=True)
    status = Column(String(20))  # finalizado | abandonado
