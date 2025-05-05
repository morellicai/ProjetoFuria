from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, cast, Integer
from app.database import get_db
from app.models import Fan, RedeSocial, Documento
from typing import List, Optional

router = APIRouter()

def calcular_engajamento(
    redes_validadas: int,
    eventos: int,
    compras: int,
) -> str:
    pontos = redes_validadas * 2 + eventos + compras

    if pontos >= 5:
        return "Alto"
    elif pontos >= 2:
        return "Médio"
    else:
        return "baixo"

@router.get("/dashboard/fans")
async def listar_fans(
    db: Session = Depends(get_db),
    interesse: Optional[str] = Query(None, description="Filtrar por interesse"),
    evento: Optional[str] = Query(None, description="Filtrar por evento"),
    compra: Optional[str] = Query(None, description="Filtrar por compra"),
    engajamento: Optional[str] = Query(None, description="Filtrar por nível de engajamento (Alto, Médio, Baixo)"),
    page: int = Query(1, ge=1, le=100, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):

    query = db.query(Fan)

    if interesse:
        query = query.filter(Fan.interesses.like(f"%{interesse}%"))

    if evento:
        query = query.filter(Fan.interesses.like(f"%{evento}%"))

    if compra:
        query = query.filter(Fan.compras.like(f"%{compra}%"))

    total_fans = query.count()

    offset = (page - 1) * page_size
    fans = query.offset(offset).limit(page_size).all()

    resultados = []

    for fan in fans:
        interesses = fan.interesses.split(',') if fan.interesses else []
        eventos = fan.eventos.split(',') if fan.eventos else []
        compras = fan.compras.split(',') if fan.compras else []

        redes_validadas = db.query(func.count(RedeSocial.id)).filter(
            RedeSocial.fan_id == fan.id,
            RedeSocial.validado == True
        ).scalar() or 0

        nivel_engajamento = calcular_engajamento(
            redes_validadas=redes_validadas,
            eventos=len(eventos),
            compras=len(compras)
        )

        if engajamento and nivel_engajamento.lower() != engajamento.lower():
            continue

        resultados.append({
            "id": fan.id,
            "nome": fan.nome,
            "interesses": interesses,
            "eventos": eventos,
            "compras": compras,
            "redes_validadas": redes_validadas,
            "engajamento": nivel_engajamento
        })

    total_filtrado = len(resultados) if engajamento else total_fans

    return {
        "total": total_filtrado,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_filtrado + page_size - 1) // page_size,
        "fans": resultados
    }

@router.get("/dashboard/stats")
async def estatisticas_dashboard(db: Session = Depends(get_db)):
    total_fans = db.query(func.count(Fan.id)).scalar()

    fans_com_redes = db.query(
        Fan.id,
        func.count(RedeSocial.id).filter(RedeSocial.validado == True).label("redes_validadas")
    ).outerjoin(RedeSocial).group_by(Fan.id).subquery()

    interesses_query = db.query(Fan.interesses).all()
    todos_interesses = []
    for interesses_str in interesses_query:
        if interesses_str[0]:
            todos_interesses.extend(interesses_str[0].split(','))

    interesses_contagem = {}
    for interesse in todos_interesses:
        interesse = interesse.strip()
        if interesse:
            interesses_contagem[interesse] = interesses_contagem.get(interesse, 0) + 1

    top_interesses = sorted(interesses_contagem.items(), key=lambda x: x[1], reverse=True)[:5]

    eventos_query = db.query(Fan.eventos).all()
    todos_eventos = []
    for evento_str in eventos_query:
        if evento_str[0]:
            todos_eventos.extend(evento_str[0].split(','))

    eventos_contagem = {}
    for evento in todos_eventos:
        evento = evento.strip()
        if evento:
            eventos_contagem[evento] = eventos_contagem.get(evento, 0) + 1

    top_eventos = sorted(eventos_contagem.items(), key=lambda x: x[1], reverse=True)[:5]

    compras_query = db.query(Fan.compras).all()
    todas_compras = []
    for compra_str in compras_query:
        if compra_str[0]:
            todas_compras.extend(compra_str[0].split(','))

    compras_contagem = {}
    for compra in todas_compras:
        compra = compra.strip()
        if compra:
            compras_contagem[compra] = compras_contagem.get(compra, 0) + 1

    # Top 5 compras
    top_compras = sorted(compras_contagem.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_fans": total_fans,
        "top_interesses": top_interesses,
        "top_eventos": top_eventos,
        "top_compras": top_compras
    }