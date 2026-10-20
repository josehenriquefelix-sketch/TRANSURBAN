from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
NomeCidade = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
NomeLinha = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
CodigoLinha = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]

class CidadeCreate(BaseModel):
    nome: NomeCidade

class CidadeResponse(BaseModel):
    id_cidade: int
    nome: str
    model_config = ConfigDict(from_attributes=True)

class LinhaCreate(BaseModel):
    codigo: CodigoLinha
    nome: NomeLinha
    id_cidade: int = Field(gt=0)

class LinhaResponse(BaseModel):
    id_linha: int
    codigo: str
    nome: str
    id_cidade: int
    cidade: str
