# TRANSURBAN

Backend acadêmico de transporte de Maringá e Sarandi, adaptado ao caderno **Avaliação geral do backend — Da primeira tabela ao relacionamento Categoria → Produto**.

A entrega atual está em **backend/**. Comece pelo [roteiro completo](docs/avaliacao_backend/01_ROTEIRO.md), depois confira o [banco](docs/avaliacao_backend/02_BANCO.md), a [demonstração](docs/avaliacao_backend/03_DEMONSTRACAO.md), a [matriz](docs/avaliacao_backend/MATRIZ.md) e as [evidências](docs/avaliacao_backend/EVIDENCIAS.md).

| Método | Caminho | Resultado |
|---|---|---|
| GET | / | Mensagem da API |
| POST | /cidades | Cria cidade, ID automático, HTTP 201 |
| GET | /cidades | Consulta cidades, HTTP 200 |
| POST | /linhas | Cria linha vinculada a cidade, HTTP 201 |
| GET | /linhas | Consulta linhas com nome da cidade, HTTP 200 |

O site integrado está em http://127.0.0.1:8000/site/ e oferece cadastro e consulta das duas entidades. Sua integração foi solicitada depois, no chat, e não amplia os endpoints da avaliação. Consulte também [uso do VS Code](docs/avaliacao_backend/04_VSCODE.md).

A implementação usa FastAPI, SQLAlchemy, Pydantic e PostgreSQL com psycopg2-binary. Não cria nem modifica tabelas automaticamente ao iniciar o servidor. Não é necessário frontend para a avaliação.

Os exemplos são demonstrativos, não representam linhas oficiais ou monitoramento real.

As pastas avaliacao_backend/, ia/, data/, database/ e os demais documentos preexistentes foram preservados como histórico de outras etapas. O frontend ativo foi integrado à API; seus arquivos anteriores estão em frontend/historico/. Seus roteiros e resultados antigos não definem os requisitos nem comprovam esta entrega. A versão anterior do README está em docs/historico/README_anterior.md. A fonte de escopo é o documento do professor; o DER e o dicionário definem a adaptação das entidades.

Não houve publicação de código ou deploy. A estrutura do Supabase informado pelo usuário foi auditada e o limite de nome da linha foi corrigido, preservando seus dados. A API está conectada ao Supabase do projeto: GET /cidades e GET /linhas foram comparados com SELECTs diretos e retornaram os mesmos 6 registros de cidades e 4 de linhas. O site também carregou esses registros. A credencial permanece somente no .env local; os testes automatizados usam PostgreSQL local isolado. Consulte o relatório de evidências.
