from pydantic import BaseModel, ConfigDict, Field


class CidadeCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nome: str = Field(min_length=1, max_length=100)


class CidadeResponse(BaseModel):
    id_cidade: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class LinhaOnibusCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nome: str = Field(min_length=1, max_length=120)
    codigo: str = Field(min_length=1, max_length=20)
    id_cidade: int = Field(gt=0)


class LinhaOnibusResponse(BaseModel):
    id_linha: int
    codigo: str
    nome: str
    cidade: str


class ErroResponse(BaseModel):
    detail: str
