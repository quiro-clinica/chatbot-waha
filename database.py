from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL  # Puxando do seu config centralizado

# Cria o motor de conexão com o PostgreSQL
engine = create_engine(DATABASE_URL)

# Cria fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os modelos
Base = declarative_base()
