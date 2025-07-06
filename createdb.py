# createdb.py
from database import engine
from models import Base

if __name__ == "__main__":
    print("📦 Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
