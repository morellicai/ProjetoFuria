from fastapi import APIRouter, File, UploadFile, HTTPException, status
from typing import Annotated

router = APIRouter()

# Defina a lista de tipos MIME permitidos
ALLOWED_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "application/pdf"
]
# Define o tamanho maximo permitido para o arquivo upado
MAX_FILE_SIZE = 10 * 1024 * 1024

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Teste de validação do tipo do arquivo upado
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}. Allowed types are: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    if not file:
        return{"mensagem": "Nenhum arquivo enviado"}
    else:
        return {"filename": file.filename, "content_type": file.content_type}