# Matriz de atendimento ao documento original

Fonte: caderno do professor lido integralmente em 20/10/2026. As localizações abaixo usam os títulos e números das seções do documento, não páginas presumidas.

| Requisito do documento | Localização no documento | Arquivo ou entrega correspondente | Forma de verificar | Situação |
|---|---|---|---|---|
| Adaptar o exemplo ao projeto autoral e ao DER | Aviso introdutório ESTE É UM MODELO GENÉRICO | backend/models.py; docs/DER.md; docs/dicionario_dados.md | Cidade sem FK; LinhaOnibus com id_cidade | Atendido |
| Backend executável FastAPI e SQLAlchemy | Missão da revisão; §§1 e 9 | backend/main.py; database.py | Servidor HTTP; testes reais | Implementado e testado |
| PostgreSQL e configuração local | §§5, 8 e 9 | backend/database.py; .env.example | Conexão real com PostgreSQL 17.11 | Testado localmente; conexão e GETs também confirmados no Supabase |
| Ambiente virtual | §§4 e 15 | backend/.venv local; 01_ROTEIRO.md | Interpretador e dependências; testes executados nele | Criado e testado |
| Registrar e reinstalar dependências | §5 | requirements.txt; requirements.lock.txt; requirements-test.lock.txt | Instalação em .venv nova; pip check | Implementado e testado |
| Configurar VS Code | §§4 e 6 | .vscode/; TRANSURBAN.code-workspace; 04_VSCODE.md | Abrir workspace; confirmar Python da .venv | Workspace aberto, confiança confirmada pelo usuário; .venv 3.13.15 selecionada |
| Proteger .env, .venv e cache | §§3, 7 e 8 | .gitignore; backend/.gitignore | git check-ignore | Verificado |
| Arquivos estruturantes | §§3, 9, 10 e 13 | database.py, models.py, schemas.py, main.py | Inspeção e roteiro de explicação | Atendido |
| Primeira entidade com PK automática | §10 | Cidade; CidadeCreate; /cidades | POST sem ID devolve ID; GET confirma | Implementado e testado |
| Entrada e saída Pydantic | §§10.2 e 11.2 | backend/schemas.py | OpenAPI e testes 422 | Implementado e testado |
| Rotas POST e GET | §§10.3 e 11.3 | backend/routes/cidades.py; linhas.py | Testes HTTP 201 e 200 | Implementado e testado |
| Uvicorn e /docs | §10.4 | main.py; 01_ROTEIRO.md | Servidor iniciado; GET /docs | Implementado e testado |
| Entidade dependente com PK e FK | §11.1 | LinhaOnibus e relacionamento cidade | Teste direto de FK PostgreSQL | Implementado e testado |
| FK permanece como ID no banco | §§11.1, 11.3 e 12 | linha_onibus.id_cidade | SELECT em conexão independente | Implementado e testado |
| Consulta apresenta nome relacionado | §§11.2, 11.3 e 12 | LinhaResponse.cidade; representar | GET /linhas e formulário web | Implementado e testado |
| Referência inexistente gera 404 | §§11.3 e 12 passo 5 | criar_linha; services.py | POST com cidade inexistente | Implementado e testado |
| Fechar sessões e confirmar gravação | §§9, 10.3 e 11.3 | database.get_db; services.salvar | Outra conexão lê os registros | Implementado e testado |
| Teste final guiado | §12 | 01_ROTEIRO.md; 03_DEMONSTRACAO.md | Executar sequência com IDs reais | Roteiro entregue; fluxo testado |
| Encerrar API, desativar e retomar | §12.1 | 01_ROTEIRO.md | Ctrl+C; deactivate; reiniciar e consultar | Reinício e persistência verificados |
| Estado final completo dos arquivos | §13 | backend/ e instruções | Comparar arquivos, rotas e dependências | Atendido |
| Evidências e commit funcional | §§6 e 14 | evidencias/; branch local | Testes e histórico Git | Verificações registradas; commit local da entrega |
| Código atualizado no GitHub | §14 e ENTREGA FINAL | Entrega local preparada | Publicação posterior autorizada | Pendente: usuário vedou publicar sem autorização |
| Checklist de aprendizagem | §15 | 03_DEMONSTRACAO.md | Estudante explica cada item | Material entregue; aprendizagem é individual |
| Desafio de compreensão de outra entidade | §16 | 01_ROTEIRO.md §11 | Explicar trecho e suas duas FKs | Exemplo de raciocínio entregue |
| Site integrado | Pedido posterior no chat; não é exigência do caderno | frontend/; /site/ | Cadastro, consulta, duplicidade e console | Implementado e testado no navegador |
| Inspeção e correção do Supabase | Pedido posterior no chat | evidências Supabase; 02_BANCO.md | SQL de metadados e comparação dos registros | Estrutura corrigida; API e site consultando Supabase com dados conferidos |

## Escolhas técnicas necessárias

Estas escolhas não são exigências adicionais do professor: divisão das rotas em módulos para preservar a estrutura existente; HTTP 201 para criação, 409 para duplicidade e 422 para validação; rejeição de campos extras para impedir IDs manuais; join antecipado para consultar nomes; inicialização explícita em banco novo para preservar dados; locks de dependências para reproduzir o ambiente Windows; schema isolado para os testes; hospedagem do site pelo mesmo servidor para dispensar CORS.

O caderno não exige métricas, cálculos, CSV, IA, autenticação, GPS, pagamento, recarga ou frontend. Não foram incorporados à API da avaliação. Os materiais antigos dessas áreas continuam preservados como histórico.
