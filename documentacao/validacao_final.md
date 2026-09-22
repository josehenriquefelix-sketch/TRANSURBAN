# Validação Final — Entrega TransUrban

## Identificação

**Projeto:** TransUrban  
**Trecho de estudo:** Maringá ↔ Sarandi  
**Cursos:** Desenvolvimento de Sistemas + Inteligência Artificial

## Checklist de Desenvolvimento de Sistemas

- [x] Problema do projeto documentado.
- [x] DER atualizado.
- [x] Dicionário de dados atualizado.
- [x] DDL PostgreSQL/Supabase.
- [x] Seed acadêmico.
- [x] Consultas DQL.
- [x] Testes CRUD corrigidos.
- [x] Testes de integridade executáveis.
- [x] Tabela elegível `cidade` escolhida para as primeiras rotas.
- [x] Backend FastAPI.
- [x] SQLAlchemy + Psycopg.
- [x] GET `/cidades/`.
- [x] POST `/cidades/` com HTTP 201 em caso de sucesso.
- [x] Rota `/health`.
- [x] Coleção Postman.
- [x] Wireframes de consulta e cadastro.
- [ ] Evidência final em ambiente real: GET → POST → GET → registro visível no Supabase.

## Checklist de Inteligência Artificial

- [x] CSV relacionado ao problema.
- [x] 180 registros acadêmicos.
- [x] Descrição/dicionário das colunas.
- [x] Qualidade e temporalização.
- [x] Estatísticas.
- [x] Agregações.
- [x] Classificação por regras.
- [x] Análise temporal.
- [x] Gráficos.
- [x] Interpretação dos resultados.
- [x] Script Python reproduzível.
- [x] Interface web.
- [x] Chatbot com Flask + Ollama.
- [x] Contexto controlado e orientação para não inventar dados.
- [ ] Evidência final de execução do Ollama na máquina da apresentação, caso o professor exija print/vídeo.

## Números que não devem ser misturados

### Banco Supabase — massa pequena de validação

- 5 registros de atraso.
- média: 12,40 min.
- maior atraso: 22 min.
- menor atraso: 5 min.

### CSV de IA — massa analítica

- 180 registros.
- média: 7,57 min.
- mediana: 8 min.
- moda: 8 min.
- mínimo: 2 min.
- máximo: 12 min.
- desvio padrão: aproximadamente 2,60 min.

Esses conjuntos possuem finalidades diferentes. O banco comprova estrutura, relacionamentos e persistência. O CSV comprova análise de dados e IA.

## Evidência final recomendada

Registrar quatro capturas reais, sem simulação:

1. GET `/cidades/` antes do cadastro;
2. POST `/cidades/` retornando HTTP 201;
3. GET após o POST mostrando a nova cidade;
4. Table Editor do Supabase mostrando o mesmo registro.

Para IA, registrar a interface web respondendo pelo menos uma pergunta cujo resultado possa ser conferido no CSV.

## GitHub

Repositório oficial:

`https://github.com/josehenriquefelix-sketch/TRANSURBAN`
