# Revisão para apresentação no auditório — 19/10/2026

Validação na nuvem Linux, Python 3.12. Não comprova execução no notebook Windows nem conexão ao projetor.

- 23 testes aprovados, nenhuma falha. Um aviso de depreciação Starlette/httpx.
- 16 requisições HTTP reais conferidas pelo gerador em SQLite temporário descartável.
- Swagger local carregado no Chromium com todas as conexões externas bloqueadas: zero tentativas externas e zero erros JavaScript. GET /health e GET /ia/resumo executados pelos botões do Swagger, com resultados esperados.
- Assets Swagger UI 5.17.14 servidos pela API, comparados byte a byte com o tarball obtido pelo npm, com licença incluída e hashes em swagger_static/ORIGEM.json.

Repetir o ensaio no notebook da apresentação, inclusive sem Wi-Fi, e conferir a projeção antes do público entrar. Supabase continua pendente; teste usa SQLite local.
