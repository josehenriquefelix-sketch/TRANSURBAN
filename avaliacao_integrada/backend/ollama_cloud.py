"""Envio apenas da pergunta cadastrada e de agregados sem dados pessoais."""
import json
import os
from urllib.request import Request, urlopen


def explicar(pergunta, resultado):
    chave = os.getenv('OLLAMA_API_KEY', '').strip()
    modelo = os.getenv('OLLAMA_MODELO', '').strip()
    if not chave or not modelo:
        raise RuntimeError('Explicação por IA indisponível: configure a chave e o modelo no backend. O resultado do CSV permanece disponível.')
    corpo = {
        'model': modelo, 'stream': False,
        'messages': [
            {'role': 'system', 'content': 'Explique em português em até duas frases. Use somente os agregados recebidos. A fonte é sintética acadêmica. Não invente números, causas, viagens, passageiros ou previsão de chegada.'},
            {'role': 'user', 'content': json.dumps({'pergunta': pergunta, 'resultado': resultado}, ensure_ascii=False)},
        ],
    }
    pedido = Request('https://ollama.com/api/chat', data=json.dumps(corpo).encode('utf8'),
                     headers={'Authorization': f'Bearer {chave}', 'Content-Type': 'application/json'}, method='POST')
    with urlopen(pedido, timeout=30) as resposta:
        # Limite de tamanho evita uma resposta remota ilimitada.
        raw = resposta.read(262145)
        if len(raw) > 262144:
            raise ValueError('Resposta da IA maior que o permitido.')
        texto = json.loads(raw)['message']['content']
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError('A IA não devolveu uma explicação.')
    return texto.strip()[:4000]
