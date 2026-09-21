from pydantic import BaseModel, ConfigDict, Field, field_validator


class CidadeCreate(BaseModel):
    # No DDL atual do TransUrban, id_cidade não é IDENTITY/SERIAL.
    # Por isso, o identificador precisa ser informado no POST.
    id_cidade: int = Field(gt=0)
    nome: str = Field(min_length=1, max_length=100)

    @field_validator("nome")
    @classmethod
    def normalizar_nome(cls, valor: str) -> str:
        nome = valor.strip()
        if not nome:
            raise ValueError("O nome da cidade não pode ficar vazio.")
        return nome


class CidadeResponse(BaseModel):
    id_cidade: int
    nome: str
    model_config = ConfigDict(from_attributes=True)
