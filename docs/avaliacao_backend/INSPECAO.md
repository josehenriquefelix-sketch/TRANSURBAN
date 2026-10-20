# Inspeção anterior à implementação

Base: commit dc4c38b do repositório josehenriquefelix-sketch/TRANSURBAN. Clone local preservado na branch refazer-backend-documento-original. A branch original e o histórico Git permanecem disponíveis.

| Área inspecionada | Encontrado | Decisão |
|---|---|---|
| backend/main.py e routes/cidades.py | FastAPI com POST/GET de cidade; sem linha relacionada | Completar o backend principal |
| backend/models.py e schemas.py | ID manual, nome obrigatório e único | Gerar PK em banco novo e manter unicidade |
| backend/database.py | dotenv, engine, sessões SQLAlchemy | Manter tecnologia, ajustar driver ao caderno e rollback |
| backend/requirements.txt | Dependências abertas e análise junto da API | Separar dependências desta avaliação e registrar versões testadas |
| docs/DER.md | Cidade 1:N LinhaOnibus | Usar relação existente para adaptar o exemplo |
| docs/dicionario_dados.md | Cidade nome 100; linha código 20 e nome 120; unicidades | Preservar os campos e as regras |
| database/script_ddl.sql | Seis tabelas; IDs manuais | Preservar arquivo histórico; inicializar recorte em banco novo |
| database/schema.sql | Tabela transporte com estrutura de CSV | Preservar; não usar nesta avaliação relacional |
| avaliacao_backend/ | API paralela com SQLite, análises e roteiros de outra versão | Preservar, sem usar como requisitos ou evidência |
| backend/app.py e legacy_flask/ | Flask/Ollama e contexto de outras etapas | Preservar, sem incorporar à avaliação |
| CSVs, frontend, ia e resultados | Materiais de outras atividades | Preservar dados e arquivos |
| README.md | Caminhos inconsistentes e múltiplos escopos | Criar entrada atual e preservar cópia anterior |

Roteiros antigos não foram utilizados para definir requisitos. O caderno original define o percurso; DER e dicionário definem apenas a adaptação autoral solicitada. Nenhuma credencial privada do usuário foi necessária.
