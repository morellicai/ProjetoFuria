from enum import EnumCheck
import os
import shutil
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Depends, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Documento, Fan
import pytesseract
from PIL import Image
import pdf2image

router = APIRouter()

# Definindo a rota para o local que ficará salva as imagens
TEMP_UPLOAD_FOLDER = "temp_uploads"
os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)

# Defina a lista de tipos MIME permitidos
ALLOWED_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "application/pdf"
]

@router.post("/upload/{fan_id}")
async def upload_file(
    fan_id: int = Path(..., example=1, description="ID do fã cadastrado anteriormente"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validação do tipo do arquivo upado
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de arquivo não suportado: {file.content_type}. Tipos permitidos: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    fan = db.query(Fan).filter(Fan.id == fan_id).first()
    if not fan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fã com ID {fan_id} não encontrado"
        )

    # Cria um nome único para o arquivo
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = os.path.join(TEMP_UPLOAD_FOLDER, unique_filename)

    # Salva o arquivo
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar o arquivo: {str(e)}"
        )

    extracted_text = None
    try:
        extracted_text = extract_text_from_file(temp_file_path, file.content_type)
    except Exception as e:
        os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar o arquivo: {str(e)}"
        )


    is_valid = validate_document_text(extracted_text, fan.nome)

    new_doc = Documento(
        fan_id=fan_id,
        documento_nome=file.filename,
        validado=is_valid,
        texto_extraido=extracted_text
    )

    try:
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
    except Exception as e:
        os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar o documento: {str(e)}"
        )

    try:
        os.remove(temp_file_path)
        print(f"Arquivo temporário removido: {temp_file_path}")
    except Exception as e:
        print(f"Erro ao remover o arquivo temporário: {str(e)}")

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "fan_id": fan_id,
        "documento_id": new_doc.id,
        "texto_extraido": extracted_text,
        "validado": is_valid,
        "mensagem": "Documento validado com Sucesso!" if is_valid else "O documento não corresponde ao nome cadastrado"
    }

def extract_text_from_file(temp_file_path, content_type):
    pytesseract.pytesseract.tesseract_cmd = r'E:\Tesseract-OCR\tesseract.exe'

    try:
        if content_type.startswith("image/"):
            img = Image.open(temp_file_path)

            img = img.convert('L')

            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)

            custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
            return pytesseract.image_to_string(img, lang='por', config=custom_config)

        elif content_type == "application/pdf":
            poppler_path = r'C:\Program Files\poppler-24.08.0\Library\bin'
            images = pdf2image.convert_from_path(temp_file_path, poppler_path=poppler_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img, lang='por')
            return text
        else:
            return None
    except Exception as e:
        print(f"Erro na extração de texto: {str(e)}")
        return None

def validate_document_text(extracted_text, fan_name):
    if not extracted_text or not fan_name:
        return False

    import re

    def normalize_text(text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    extracted_text = normalize_text(extracted_text)
    fan_name = normalize_text(fan_name)

    print(f"Texto extraído normalizado: {extracted_text}")
    print(f"Nome do fã normalizado: {fan_name}")

    if fan_name in extracted_text:
        return True

    name_parts = fan_name.split()
    matches = 0
    for part in name_parts:
        if len(part) > 2 and part in extracted_text:
            matches += 1
            print (f"Parte encontrada: {part}")

    return matches >= len(name_parts) / 2