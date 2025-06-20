from database import engine
from models import Base

# Cria todas as tabelas definidas com Base
Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso.")
