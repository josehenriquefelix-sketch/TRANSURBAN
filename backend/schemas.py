from pydantic import BaseModel, ConfigDict


class CidadeCreate(BaseModel):
    nome: str


class CidadeResponse(BaseModel):
    id_cidade: int
    nome: str

    model_config = ConfigDict(from_attributes=True)
