# TRANSURBAN · Guia rápido do auditório

**Preparar antes. Testar no computador da apresentação. Apresentar em até 9 minutos.**

> A API e o site funcionam sem internet depois da instalação, usando PostgreSQL local. O banco precisa permanecer ligado. Publicar no GitHub não hospeda a API.

## 1 · Preparar o computador

Instale **Git, Python 3.13 e VS Code**. Tenha também **PostgreSQL local** ou **Docker Desktop** instalado e em execução.

No terminal do VS Code, confira:

```powershell
git --version
python --version
code --version
```

## 2 · Baixar e abrir o projeto

Em uma pasta de projetos, execute:

```powershell
git clone https://github.com/josehenriquefelix-sketch/TRANSURBAN.git
cd TRANSURBAN
python preparar.py
code TRANSURBAN.code-workspace
```

**A preparação cria a `.venv`, instala dependências e cria o `.env` de exemplo.** Exige internet e preserva um `.env` existente. Não copie a `.venv` de outro PC nem compartilhe a senha do Supabase.

Já tem o projeto? Com a branch `main` sem alterações locais, use `git pull --ff-only` e depois `python preparar.py`.

## 3 · Ligar o banco local

**No PC novo, com Docker Desktop aberto**, execute na raiz do projeto:

```powershell
docker compose up -d banco
docker compose ps
```

Aguarde o estado **healthy**. O `.env` criado do exemplo já aponta para esse banco, na porta **54329**. Se o arquivo já existia, confira privadamente `TEST_DATABASE_URL`: ela precisa apontar para PostgreSQL local.

> **Ensaio necessário:** o caminho com Docker ainda precisa ser testado no PC do auditório. Nesta revisão, API e testes passaram com PostgreSQL local já preparado.

**Somente no computador de José:** se o banco local estiver parado, execute na raiz e mantenha o terminal aberto:

```powershell
.\.local-postgres\runtime\pgsql\bin\postgres.exe -D .\.local-postgres\data -h 127.0.0.1 -p 55439
```

Essa pasta privada não vai para o GitHub. Se esse banco já estiver rodando, use a instância existente.

## 4 · Iniciar a apresentação

No terminal do VS Code:

```powershell
cd backend
.\.venv\Scripts\python.exe executar_auditorio.py --schema transurban_auditorio_palco --vazio
```

Mantenha esse terminal aberto e acesse:

| Tela | Endereço |
|---|---|
| **API · Swagger** | http://127.0.0.1:8001/docs |
| **Site** | http://127.0.0.1:8001/site/ |

**Use um schema novo para os cadastros retornarem 201.** Se já treinou com `palco`, use `palco2`. `--vazio` não apaga registros existentes. No teste de persistência, reinicie com o **mesmo comando e schema**.

No VS Code, selecione o interpretador `backend/.venv/Scripts/python.exe`. O modo auditório usa banco local e mantém o Supabase separado.

## 5 · Conferir antes de entrar no palco

Abra **outro terminal**, entre em `backend` e execute:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe verificar_http.py --base-url http://127.0.0.1:8001
```

| Conferência | Referência desta revisão |
|---|---|
| Testes | **18 aprovados**, um aviso de depreciação |
| Dependências | `No broken requirements found` |
| API, site e arquivos locais | **13 verificações HTTP aprovadas** |

Confira o resultado real no PC do auditório. Antes de começar, `GET /cidades` e `GET /linhas` devem retornar listas vazias no schema novo.

## 6 · Demonstrar na hora

| Pessoa | O que mostrar | Resultado esperado |
|---|---|---|
| **José** | Problema, objetivo e solução; abrir site e Swagger | Apresentar a proposta |
| **Kauan** | Cadastrar Maringá e Sarandi; consultar cidades | **201 / 200**; anotar o ID de Sarandi |
| **Bruno** | Cadastrar e consultar uma linha com esse ID | **201 / 200**; cidade pelo nome |
| **Gustavo** | Repetir cadastro, usar cidade inexistente e ID zero; executar Pytest | **409 / 404 / 422**; conferir testes |
| **Ana Carolina** | Reiniciar só a API com o mesmo schema; consultar; mostrar busca e filtro do site | Registro permanece salvo |

**Tempo previsto: 8min25s, com 35s de margem.** Falas, JSON e cliques estão no [roteiro completo](docs/apresentacao/ROTEIRO_COMPLETO.md). Use sempre o ID retornado pelo seu banco.

## Se algo falhar

| Situação | Ação |
|---|---|
| Falta `.venv` ou dependência | Na raiz, execute `python preparar.py` |
| Banco indisponível ou HTTP 503 | Ligue PostgreSQL e confira `TEST_DATABASE_URL` privadamente |
| Porta 8001 ocupada | Confira a API existente; não inicie dois servidores na mesma porta |
| Cadastro retorna 409 | O registro já existe; consulte-o ou prepare um schema novo antes do ensaio |

**Deixe instalação e configuração prontas antes dos 9 minutos.** Leve vídeo e logs como apoio, identificando-os como gravação se precisar usá-los.

A versão atual cadastra e lista cidades e linhas. GPS, horários ao vivo e autenticação de usuários ficam fora desta entrega. O catálogo do Supabase ainda inclui demonstrações e precisa de conciliação com fontes oficiais. Para o modo Supabase e outros detalhes, consulte [o guia complementar](PUBLICAR_E_BAIXAR_NO_VSCODE.md) e o README.
