"""Chat conforme o guia: resultado disponível mesmo sem Ollama."""
from urllib.error import HTTPError
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict, Field
from backend.chat_dados import CONSULTAS, consultar, encontrar_pergunta
from backend.ollama_cloud import explicar
from backend.auth import limitar

router = APIRouter(prefix='/chat', tags=['Ciência de Dados · Chat'])


class EntradaChat(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    pergunta: str = Field(min_length=1, max_length=300)


@router.get('/perguntas')
def listar_perguntas():
    return list(CONSULTAS)


@router.post('', dependencies=[Depends(limitar)])
def responder(entrada: EntradaChat):
    pergunta = encontrar_pergunta(entrada.pergunta)
    if pergunta is None:
        return {'resultado': None, 'explicacao': None, 'aviso': 'Escolha uma pergunta da lista. A base não permite responder a qualquer pergunta.'}
    try:
        resultado = consultar(pergunta)
    except (OSError, ValueError) as erro:
        raise HTTPException(503, f'Não foi possível validar o CSV: {erro}') from erro
    explicacao, aviso = None, None
    try:
        explicacao = explicar(pergunta, resultado)
    except RuntimeError as erro:
        aviso = str(erro)
    except HTTPError as erro:
        aviso = f'Ollama indisponível (HTTP {erro.code}). O resultado calculado permanece disponível.'
    except (OSError, ValueError, KeyError, TypeError):
        aviso = 'Não foi possível obter a explicação da IA. O resultado calculado permanece disponível.'
    return {'pergunta': pergunta, 'resultado': resultado, 'explicacao': explicacao, 'aviso': aviso,
            'fonte': 'CSV sintético acadêmico', 'unidade': 'Observações de atraso em trechos; não são viagens completas.'}
