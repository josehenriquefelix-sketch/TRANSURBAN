"""Contrato JSON e validação das entradas; IDs são gerados pelo banco."""
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Nome = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
Codigo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]

class Entrada(BaseModel):
    model_config = ConfigDict(extra='forbid')

class CidadeCreate(Entrada):
    nome: Nome

class CidadeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_cidade: int
    nome: str

class LinhaCreate(Entrada):
    id_cidade: int = Field(gt=0, strict=True)
    codigo: Codigo
    nome: Nome

class LinhaResponse(BaseModel):
    id_linha: int
    id_cidade: int
    codigo: str
    nome: str
    cidade: str
