from fastapi import FastAPI
from app.routes import cadastro
from app.models import Base
from app.database import engine

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Projeto Furia")

# Incluir routers
app.include_router(cadastro.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)