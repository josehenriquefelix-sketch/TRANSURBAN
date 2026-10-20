from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NomeCidade = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
NomeLinha = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
CodigoLinha = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]

class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

class CidadeCreate(Entrada):
    nome: NomeCidade

class CidadeResponse(BaseModel):
    id_cidade: int
    nome: str
    model_config = ConfigDict(from_attributes=True)

class LinhaCreate(Entrada):
    nome: NomeLinha
    codigo: CodigoLinha
    id_cidade: int = Field(gt=0, strict=True)

class LinhaResponse(BaseModel):
    id_linha: int
    codigo: str
    nome: str
    cidade: str
