from fastapi import APIRouter, Request, HTTPException, status, Path, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db, engine
from ..models import Fan, FanCadastro, Base

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Rota para exibir a tela de cadastro
@router.get("/cadastro")
def tela_cadastro(request: Request):
    return templates.TemplateResponse("cadastro.html", {"request": request})

# Rota responsável por cadastrar um novo fã no sistema
@router.post("/cadastro")
def cadastro_fan(fan: FanCadastro, request: Request, db: Session = Depends(get_db)):
    try:
        db_fan = Fan(
            nome = fan.nome,
            endereco = fan.endereco,
            cpf = fan.cpf.replace(".", "").replace("-", ""),
            atividades = ",".join(fan.atividades) if fan.atividades else "",
            interesses = ",".join(fan.interesses) if fan.interesses else "",
            eventos = ",".join(fan.eventos) if fan.eventos else "",
            compras = ",".join(fan.compras) if fan.compras else ""
        )
        db.add(db_fan)
        db.commit()
        db.refresh(db_fan)

        accept = request.headers.get("accept", "")
        if "application/json" in accept:
            return {
                "id": db_fan.id,
                "mensagem": "Cadastro realizado com sucesso!",
                "proxima_etapa": f"/upload/{db_fan.id}"
            }
        else:
            return RedirectResponse(f"/upload/{db_fan.id}", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Erro ao cadastrar: {str(e)}"
        )