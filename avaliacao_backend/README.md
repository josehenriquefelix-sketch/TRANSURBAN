# TRANSURBAN — Avaliação Geral do Backend DS + IA

CEEP Maringá • Professor Giuliano Alencar • Preparação em 05/10/2026.

## Estado verificado em 05/10/2026

- 18 testes automatizados aprovados: 9 analíticos e 9 de API/integridade.
- 20 requisições HTTP reais aprovadas em Uvicorn, usando SQLite temporário; respostas e log em evidencias/http.
- CSV idêntico ao arquivo do GitHub no commit 2d3d554e; origem sintética explicitada.
- Cadastro de cidade e linha, consulta com nome relacionado, erros 404/409/422 e indicadores validados.
- Supabase: conexão e persistência no projeto remoto ainda não verificadas. O modo local permite ensaio, mas não substitui a demonstração PostgreSQL exigida em DS.
- GitHub: consulte versionamento/PUBLICACAO.json para o commit publicado desta revisão.
- Capturas de Swagger: quando presentes em evidencias/capturas, são capturas reais; ausência significa que ainda devem ser feitas no computador da apresentação.

## Escolha das tabelas

O exemplo Categoria → Produto foi adaptado para **Cidade → Linha de ônibus**. Uma cidade pode ter várias linhas; cada linha referencia exatamente uma cidade. A API armazena `id_cidade` e devolve também `cidade: "Maringá"`. O recorte atende às duas entidades exigidas e preserva os nomes do modelo acadêmico TRANSURBAN. Os demais relacionamentos estão documentados em `docs/CHAVES_SUPABASE.md`.

Este pacote é uma extensão acadêmica independente para adicionar ao repositório em uma pasta própria. Não substitui o aplicativo mobile V3 nem implementa GPS, bilhetagem ou autenticação de passageiros. Execute em localhost; a API de avaliação não tem autenticação para exposição pública.

## Execução no Windows

Extraia o ZIP e abra a pasta no VS Code. No PowerShell, dentro da pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Abra http://127.0.0.1:8000/docs. Sem DATABASE_URL, o banco SQLite local é criado na pasta do projeto. Nada é enviado ao Supabase. Os atalhos `preparar.cmd`, `iniciar.cmd` e `testar.cmd` também executam essas etapas; preparar não sobrescreve `.env` existente.

Para demonstrar ativação/desativação, no Prompt de Comando (CMD):

```bat
.venv\Scripts\activate.bat
python -m uvicorn backend.main:app --reload
REM Pressione Ctrl+C e espere o servidor encerrar.
deactivate
```

No PowerShell, a ativação equivalente é `.\.venv\Scripts\Activate.ps1`. Se a política bloquear o script, use os executáveis explícitos acima ou o CMD; não é necessário alterar a política de segurança. A pasta `.venv` mantém as bibliotecas mesmo depois de `deactivate`.

## Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
# Encerrar: Ctrl+C; depois deactivate
```

## Supabase existente

1. Abra o projeto correto e execute **somente** `sql/01_auditar_supabase.sql`: é uma consulta de leitura que identifica PK, FK, campos, geração de IDs e estado de RLS.
2. Confira se cidade/linha_onibus e seus campos correspondem ao recorte. O DDL antigo não tinha geração automática; a Sprint 7 tinha SERIAL. Se os IDs já têm sequência/identity válida, não há motivo para adicionar outra.
3. Se o esquema antigo realmente precisar de IDs automáticos, revise `sql/03_ids_automaticos_legado.sql` antes de aplicar. O script preserva registros e chaves, bloqueia escrita durante a migração e sincroniza sequências. Não foi executado ou validado em PostgreSQL nesta sessão.
4. No `.env`, use a conexão PostgreSQL fornecida pelo próprio painel Connect. O modelo está em `.env.example`. Codifique caracteres especiais da senha na URL. A porta deve ser a indicada no painel para o método escolhido. Não exponha a conexão em prints ou commits.
5. Inicie a API e verifique `/health`. O servidor **não cria nem altera tabelas do PostgreSQL** ao iniciar.
6. Faça os testes POST/GET em banco de testes e confira os mesmos IDs no Table Editor. Salve as respostas/capturas. Não desative RLS para solucionar erro de conexão ou de PK.

`sql/02_criar_recorte_em_banco_novo.sql` é apenas para banco de teste vazio. O arquivo `referencia_sprint7_nao_executar_sem_revisao.sql` é uma cópia documental do pacote anterior, não uma migração deste trabalho. Não rode os três scripts de criação/migração em sequência indiscriminadamente.

## Teste guiado DS

1. `POST /cidades`: `{"nome":"Maringá"}` → esperado HTTP 201 e `id_cidade` gerado.
2. `GET /cidades` → esperado o registro cadastrado.
3. `POST /linhas`: `{"id_cidade":ID_RETORNADO,"codigo":"001","nome":"Linha acadêmica"}` → esperado HTTP 201 e nome da cidade. Troque ID_RETORNADO pelo número real, sem aspas.
4. `GET /linhas` → esperado o mesmo registro e `cidade: "Maringá"`.
5. Cidade inexistente no POST de linha → esperado 404. Nome vazio/ID inválido → 422. Duplicidade de cidade ou código na mesma cidade → 409. Esses resultados foram observados nos testes locais; a repetição no Supabase continua pendente.

Coleção pronta: `TRANSURBAN.postman_collection.json`. O POST de cidade armazena o ID em variável e o POST de linha usa esse valor. Ela inclui testes de status e nomes. Use banco de demonstração: os testes POST criam registros.

## Testes e evidências

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\exportar_ia.py
.\.venv\Scripts\python.exe scripts\capturar_http.py
```

`capturar_http.py` inicia um servidor local em banco SQLite temporário, faz requisições HTTP reais, salva respostas e encerra o processo; ignora credenciais do banco externo. Requer as dependências instaladas. A suíte `test_api.py` também usa um banco temporário. O CI fornecido em `integracao_github/avaliacao-backend.yml` só será executado se copiado para `.github/workflows` na raiz do repositório, conforme suas instruções. Nenhuma execução CI é alegada.

## Responsabilidade de cada arquivo

| Arquivo | Responsabilidade |
|---|---|
| `database.py` | Carrega configuração, cria engine e entrega/fecha sessão por requisição. |
| `models.py` | Mapeia tabelas, PK, FK, unicidade e navegação ORM. |
| `schemas.py` | Valida JSON de entrada e define JSON de saída. |
| `main.py` | Registra rotas, orquestra validação, consulta e persistência. |
| `analise.py` | Lê CSV, audita qualidade e calcula indicadores. |
| `.env` | Configuração privada local; não entra no Git. |
| `requirements.txt` | Dependências instaladas e testadas; requirements.lock.txt registra versões utilizadas. |

## Indicadores e próximos passos do dashboard

Veja `docs/IA_E_DASHBOARD.md`. Resultado desta fonte sintética: 180 observações; soma 1.362 minutos; média 7,5667; mediana 8; máximo 12, com 7 observações empatadas. Os números não representam a operação real de Maringá/Sarandi.

## Versionamento no repositório existente

O ZIP pode conter um bundle Git local em `versionamento/`, que comprova apenas commits locais. Não significa publicação no GitHub.

Para integrar sem substituir o histórico, copie esta pasta para `avaliacao_backend` dentro do clone de TransUrban. Não copie `.venv`, `.env` ou banco local. Na raiz do clone:

```bash
git status
git add avaliacao_backend
git diff --cached --stat
git commit -m "Adiciona avaliacao backend DS IA do TRANSURBAN"
git push
```

Confira o commit na página do repositório após o push. Não use `git init` por cima do repositório existente, `--force` ou substituição de sua branch. A pasta avaliacao_backend foi preparada para integração por commit aditivo no repositório. Consulte versionamento/PUBLICACAO.json para a evidência do envio.
