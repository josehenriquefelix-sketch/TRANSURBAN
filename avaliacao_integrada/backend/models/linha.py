"""Contratos Pydantic da entidade linha_onibus, que referencia cidade."""
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LinhaEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_cidade: int = Field(gt=0, strict=True)
    codigo: str = Field(min_length=1, max_length=20)
    nome: str = Field(min_length=2, max_length=120)

    @field_validator("codigo", "nome")
    @classmethod
    def texto_sem_espacos(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("O campo não pode ficar vazio.")
        return valor


class LinhaSaida(LinhaEntrada):
    id_linha: int = Field(gt=0)
    cidade: str
