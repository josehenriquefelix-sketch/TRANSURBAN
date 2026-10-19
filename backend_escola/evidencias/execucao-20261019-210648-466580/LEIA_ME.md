# Validação da revisão com fonte pública — 19/10/2026

Executada na nuvem Linux com Python 3.12. Não comprova ensaio no notebook Windows nem projeção.

- 27 testes aprovados, nenhuma falha; um aviso de depreciação Starlette/httpx.
- Novos testes comparam todos os 71.086 IDs, códigos, nomes e categorias do CSV aos arquivos GTFS incluídos; reconciliam contagens e rejeitam snapshot adulterado.
- 21 requisições HTTP reais verificadas pelo gerador em SQLite temporário, incluindo cinco endpoints da fonte pública.
- Chromium com acesso externo bloqueado: Swagger local carregou e executou /health e /ia/dados-publicos/resumo; zero requisições externas e zero erros JavaScript.

Arquivos publico-*.json são da fonte pública de Curitiba. resumo.json/qualidade.json/linhas.json/datas.json são da base sintética anterior, preservada como teste e explicitamente separada na API. Não apresentar 7,57 minutos como dado real.

Snapshot comunitário de programação de Curitiba, período declarado 28/09–05/10/2026. Não é feed oficial URBS, não é telemetria e não mede atrasos. Proveniência e transformações em data/dados_publicos/fonte.json e LEIA_ME.md.
