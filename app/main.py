from fastapi import FastAPI
from app.routes import cadastro, upload, redes, dashboard
from app.models import Base
from app.database import engine
from app.middleware.upload_validator import FileUploadMiddleware

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Projeto Furia")

UPLOAD_SIZE_LIMIT = 1024 * 1024 * 2
UPLOAD_ROUTES = ["/upload"]

app.middleware("http")(
    FileUploadMiddleware(
        max_size=UPLOAD_SIZE_LIMIT,
        upload_routes=UPLOAD_ROUTES
    )
)

# Incluir routers
app.include_router(cadastro.router)
app.include_router(upload.router)
app.include_router(redes.router)
app.include_router(dashboard.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)