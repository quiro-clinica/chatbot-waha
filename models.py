from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base  # importa a Base criada lá no database.py

# Classe que representa a tabela no PostgreSQL
class ChatIdMap(Base):
    __tablename__ = "chat_id_map"  # nome real da tabela no banco

    # Colunas da tabela:
    id = Column(Integer, primary_key=True, index=True)  # Chave primária
    chat_id_lid = Column(String(100), unique=True, nullable=False)  # ID estranho com @lid
    chat_id_real = Column(String(100), unique=True, nullable=False)  # Número real como @c.us
    criado_em = Column(DateTime(timezone=True), server_default=func.now())  # Data/hora automática
