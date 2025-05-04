from fastapi import APIRouter, HTTPException, Depends, status, Body
from app.models import RedeSocial, Fan, RedesSociaisInput
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database import get_db
import requests
import re
from app.services.ai_validator import extrair_conteudo_do_perfil, validar_conteudo_com_ia

router = APIRouter()

def validar_url(url: str, tipo_rede: str) -> bool:
    padroes = {
        "instagram": r"^https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_\.]+/?$",
        "twitter": r"^https?://(?:www\.)?twitter\.com/[a-zA-Z0-9_]+/?$",
        "steam": r"^https?://(?:www\.)?steamcommunity\.com/(?:id|profiles)/[a-zA-Z0-9_]+/?$",
        "gamersclub": r"^https?://(?:www\.)?gamersclub\.com\.br/player/[a-zA-Z0-9_]+/?$"
    }

    if tipo_rede not in padroes:
        return False

    return bool(re.match(padroes[tipo_rede], url))

def verificar_link_existe(url: str) -> bool:
    try:
        response = requests.head(url, timeout=5)
        return response.status_code < 400
    except:
        return False

@router.post("/redes", status_code=status.HTTP_201_CREATED)
async def adicionar_redes(
    fan_id: int,
    redes_data: RedesSociaisInput,
    db: Session = Depends(get_db)
):
    try:
        fan = db.query(Fan).filter(Fan.id == fan_id).first()
        if not fan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fã com ID {fan_id} não encontrado."
            )
        db.query(RedeSocial).filter(RedeSocial.fan_id == fan_id).delete()

        redes_adicionadas = []
        redes_invalidas = []

        # Converter o modelo Pydantic para dicionário
        redes_dict = redes_data.dict(exclude_unset=True)

        for tipo_rede, url in redes_dict.items():
            if not url:
                continue

            if not validar_url(url, tipo_rede):
                redes_invalidas.append({
                    "tipo": tipo_rede,
                    "url": url,
                    "erro": "Formato de URL inválido"
                })
                continue

            nova_rede = RedeSocial(
                fan_id=fan_id,
                tipo=tipo_rede,
                link=url,
                validado=False
            )

            db.add(nova_rede)
            redes_adicionadas.append({
                "tipo": tipo_rede,
                "url": url
            })

        db.commit()

        return {
            "fan_id": fan_id,
            "redes_adicionadas": redes_adicionadas,
            "redes_invalidas": redes_invalidas,
            "mensagem": "Redes sociais atualizadas com sucesso"
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar redes sociais: {str(e)}"
        )

@router.get("/redes/{fan_id}", response_model=List[Dict])
async def obter_redes(fan_id: int, db: Session = Depends(get_db)):

    redes = db.query(RedeSocial).filter(RedeSocial.fan_id == fan_id).all()

    if not redes:
        return []

    return [
        {
            "id": rede.id,
            "tipo": rede.tipo,
            "link": rede.link,
            "validado": rede.validado
        }
        for rede in redes
    ]

@router.post("/redes/validar/{fan_id}", status_code=status.HTTP_200_OK)
async def validar_redes(
    fan_id: int,
    db: Session = Depends(get_db)
):
    try:
        # Verificar se o fã existe
        fan = db.query(Fan).filter(Fan.id == fan_id).first()
        if not fan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fã com ID {fan_id} não encontrado"
            )

        # Buscar redes sociais do fã
        redes = db.query(RedeSocial).filter(RedeSocial.fan_id == fan_id).all()

        if not redes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nenhuma rede social encontrada para o fã com ID {fan_id}"
            )

        # Extrair interesses do fã
        interesses = []
        if fan.interesses:
            # Converter string de interesses para lista
            interesses = fan.interesses.split(',') if isinstance(fan.interesses, str) else []

        resultados_validacao = []

        # Para cada rede social, fazer a validação com IA
        for rede in redes:
            # Extrair conteúdo do perfil
            conteudo = extrair_conteudo_do_perfil(rede.link, rede.tipo)

            # Validar conteúdo com IA
            resultado = validar_conteudo_com_ia(conteudo, interesses)

            # Atualizar o status de validação
            rede.validado = resultado["relevante"]

            resultados_validacao.append({
                "tipo": rede.tipo,
                "link": rede.link,
                "validado": rede.validado,
                "confianca": resultado["confianca"],
                "motivo": resultado["motivo"]
            })

        db.commit()

        return {
            "fan_id": fan_id,
            "resultados": resultados_validacao,
            "mensagem": "Validação de redes sociais concluída com IA"
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar redes sociais: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro durante a validação: {str(e)}"
        )

@router.delete("/redes/{rede_id}", status_code=status.HTTP_200_OK)
async def deletar_rede(rede_id: int, db: Session = Depends(get_db)):
    try:
        rede = db.query(RedeSocial).filter(RedeSocial.id == rede_id).first()
        if not rede:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rede social com ID {rede_id} não encontrada"
            )
        db.delete(rede)
        db.commit()

        return {
            "mensagem": f"Rede social {rede.tipo} removida com sucesso"
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover rede social: {str(e)}"
        )