import os
import shutil
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Documento, Fan

router = APIRouter()

# Definindo a rota para o local que ficará salva as imagens
UPLOAD_FOLDER = "../../ uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Defina a lista de tipos MIME permitidos
ALLOWED_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "application/pdf"
]
# Define o tamanho maximo permitido para o arquivo upado
MAX_FILE_SIZE = 10 * 1024 * 1024

@router.post("/upload/{fan_id}")
async def upload_file(
    fan_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validação do tipo do arquivo upado
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de arquivo não suportado: {file.content_type}. Tipos permitidos: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    fan = db.query(Fan). filter(Fan.id == fan_id). first()
    if not fan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fã com ID {fan_id} não encontrado"
        )

    # Cria um nome único para o arquivo
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Salva o arquivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar o arquivo: {str(e)}"
        )

    new_doc = Documento(
        fan_id=fan_id,
        documento_nome=file.filename,
        validado=False,
        texto_extraido=None
    )

    try:
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar o documento: {str(e)}"
        )

    return {
        "filename": file.filename,
        "saved_as": unique_filename,
        "content_type": file.content_type,
        "fan_id": fan_id,
        "documento_id": new_doc.id
    }