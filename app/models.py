from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

class FanCadastro(BaseModel):
    nome: str = Field(..., example = "João da Silva", min_length = 3, max_length = 50, description="Nome completo do fã")
    email: Optional[str] = None
    endereco: str = Field(..., example = "Rua das Flores, 123")
    cpf: str = Field(..., example = "123.456.789-00",pattern=r"\d{3}\.\d{3}\.\d{3}-\d{2}")
    atividades: List[str] = Field(default_factory=list, example=["Streaming", "Cosplay"])
    interesses: List[str] = Field(..., default_factory=list, example=["CS:GO", "LoL"])
    eventos: List[str] = Field(default_factory=list, example=["CBLOL 2023"])
    compras: List[str] = Field(default_factory=list, example=["Camiseta FURIA"])

class FanRedes(BaseModel):
    redes_sociais: List[str] = Field(
        default_factory=list,
        example=["https://twitter.com/joaosilva"]
    )
    perfis_esports: List[str] = Field(
        default_factory=list,
        example=["https://hltv.org/user/joaosilva"]
    )

class RedesSociaisInput(BaseModel):
    instagram: Optional[str] = Field(None, example="https://instagram.com/seuperfil", description="Perfil do Instagram")
    twitter: Optional[str] = Field(None, example="https://twitter.com/seuperfil", description="Perfil do Twitter")
    steam: Optional[str] = Field(None, example="https://steamcommunity.com/id/seuperfil", description="Perfil da Steam")
    gamersclub: Optional[str] = Field(None, example="https://gamersclub.com.br/player/seuperfil", description="Perfil da Gamers Club")

    class Config:
        json_schema_extra = {
            "example": {
                "instagram": "https://instagram.com/seuperfil",
                "twitter": "https://twitter.com/seuperfil",
                "steam": "https://steamcommunity.com/id/seuperfil",
                "gamersclub": "https://gamersclub.com.br/player/seuperfil"
            }
        }

class FanDocumento(BaseModel):
    documento_nome: str = Field(..., example="rg_joao.jpg")
    validado: bool = Field(..., example=False)
    texto_extraido: Optional[str] = Field(None, example="João da Silva")

Base = declarative_base()

class Fan(Base):
    __tablename__ = "fans"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    endereco = Column(String(255), nullable=False)
    cpf = Column(String(11), nullable=False)
    atividades = Column(Text)
    interesses = Column(Text)
    eventos = Column(Text)
    compras = Column(Text)

class Documento(Base):
    __tablename__ = "documentos"
    id = Column(Integer, primary_key=True, index=True)
    fan_id = Column(Integer, ForeignKey('fans.id'))
    documento_nome = Column(String(100), nullable=False)
    validado = Column(Boolean, default=False)
    texto_extraido = Column(Text)

class RedeSocial(Base):
    __tablename__ = "redes_sociais"
    id = Column(Integer, primary_key=True, index=True)
    fan_id = Column(Integer, ForeignKey('fans.id'), nullable=False)
    link = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    validado = Column(Boolean, default=False)
