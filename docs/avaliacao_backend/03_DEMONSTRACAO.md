# Roteiro de demonstração do TRANSURBAN

## Preparação

Siga 01_ROTEIRO.md e 02_BANCO.md. Use um banco de desenvolvimento. Os nomes e códigos de linhas dos exemplos são acadêmicos. Não apresente resultados de outros diretórios como evidência desta execução.

## Sequência da apresentação

1. Abra o documento do professor e explique a adaptação pedida: Categoria → Produto virou Cidade → LinhaOnibus, conforme o DER.
2. Mostre database.py, models.py, schemas.py e main.py. Explique conexão, persistência, validação e HTTP.
3. Mostre em models.py a PK de Cidade e a ausência de FK nessa entidade.
4. Inicie python -m uvicorn main:app --reload na pasta backend e abra /docs.
5. Cadastre Maringá com POST /cidades. Anote o ID real. Consulte GET /cidades.
6. Mostre a PK de LinhaOnibus e a FK id_cidade. Diferencie ForeignKey e relationship.
7. Cadastre a linha demonstrativa do roteiro, usando o ID anotado. Mostre HTTP 201.
8. Consulte GET /linhas e destaque cidade com o nome. Mostre no SQL que a FK armazenada continua sendo o ID.
9. Envie uma linha com cidade inexistente. Mostre HTTP 404 e confirme que não apareceu novo registro.
10. Mostre 422 para entrada inválida e 409 para duplicidade.
11. Encerre a API com Ctrl+C, reinicie e consulte os dados para demonstrar persistência. Mostre as evidências de testes reais.
12. Explique deactivate, revisão no Git e a diferença entre salvar, testar, commit e push.

## Explicação em português claro

O TRANSURBAN organiza informações do transporte entre Maringá e Sarandi. Nesta avaliação implementamos o cadastro e a consulta de cidades e de linhas associadas. Uma linha só pode referenciar uma cidade existente. O PostgreSQL guarda essa ligação por ID; a API usa o relacionamento para mostrar o nome da cidade. Esta demonstração não depende de frontend nem de dados reais de operação.

## Conferência final

Confirme que consegue explicar ambiente virtual, dependências, os quatro arquivos estruturantes, Uvicorn, /docs, PK, FK, armazenamento do identificador, nome relacionado na saída, erro de referência inexistente, persistência e proteção do .env. Confira a matriz de requisitos e as pendências em EVIDENCIAS.md antes de apresentar.
