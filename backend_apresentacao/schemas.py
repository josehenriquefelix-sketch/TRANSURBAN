"""Validação das entradas JSON antes da gravação."""
from datetime import date
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Nome = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Positivo = Annotated[int, Field(gt=0, strict=True)]
class Entrada(BaseModel):
    model_config = ConfigDict(extra='forbid')
class CidadeIn(Entrada):
    nome: Nome
class LinhaIn(Entrada):
    id_cidade: Positivo
    codigo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
class TrechoIn(Entrada):
    id_cidade_origem: Positivo
    id_cidade_destino: Positivo
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    distancia_km: float = Field(gt=0, le=9999.99, allow_inf_nan=False)
    @model_validator(mode='after')
    def cidades_diferentes(self):
        if self.id_cidade_origem == self.id_cidade_destino:
            raise ValueError('O modelo acadêmico exige cidades de origem e destino diferentes.')
        return self
class PercursoIn(Entrada):
    id_linha: Positivo
    id_trecho: Positivo
    ordem: Positivo
class FaixaIn(Entrada):
    id_trecho: Positivo
    tipo: Literal['EXCLUSIVA', 'PREFERENCIAL']
    status: Literal['ATIVA', 'INATIVA', 'PLANEJADA']
class AtrasoIn(Entrada):
    id_linha: Positivo
    id_trecho: Positivo
    data_registro: date
    minutos_atraso: int = Field(ge=0, strict=True)
    observacao: str = Field(default='', max_length=255)

