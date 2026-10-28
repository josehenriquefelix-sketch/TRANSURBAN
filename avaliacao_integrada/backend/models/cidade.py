"""Modelos Pydantic da API."""
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CidadeEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(min_length=2, max_length=100)

    @field_validator("nome")
    @classmethod
    def nome_sem_espacos(cls, valor: str) -> str:
        valor = valor.strip()
        if len(valor) < 2:
            raise ValueError("Informe um nome de cidade com pelo menos 2 caracteres.")
        return valor


class CidadeSaida(CidadeEntrada):
    id_cidade: int = Field(gt=0)
