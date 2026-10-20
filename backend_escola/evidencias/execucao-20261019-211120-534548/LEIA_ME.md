# Verificação do modo de apresentação — API 1.3.0

Executada na nuvem Linux com Python 3.12 em 19/10/2026. Não substitui ensaio Windows/projetor.

- 29 testes aprovados, nenhuma falha. Um aviso de depreciação Starlette/httpx.
- 22 requisições HTTP reais verificadas em banco SQLite temporário descartável, incluindo roteiro e fonte pública.
- Modo de apresentação real iniciado por iniciar_apresentacao.py: Swagger não lista as rotas sintéticas, preservadas para testes.
- Chromium com conexões externas bloqueadas: /health e resumo público executados; exemplo selecionável de cidade com espaços executado pela interface e respondeu 422; cinco grupos exibidos sem alterar os totais completos. Zero requisições externas e erros JavaScript.
- Atalhos .cmd fornecidos para Windows, não executados neste ambiente Linux. O notebook de destino precisa ser preparado e ensaiado.

Os JSONs publico-*.json são do snapshot público comunitário histórico de Curitiba, com os limites documentados em data/dados_publicos. Os arquivos sem prefixo publico mantêm a validação da base sintética anterior: não são dados de atrasos reais.
