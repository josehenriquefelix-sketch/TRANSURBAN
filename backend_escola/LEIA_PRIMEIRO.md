# TRANSURBAN — backend da avaliação

Adaptação: Categoria → Cidade; Produto → Linha de ônibus.
Não é necessário construir frontend nesta avaliação.

| Tabela | PK | FK | Relação |
|---|---|---|---|
| cidade | id_cidade | nenhuma | Uma cidade possui várias linhas |
| linha_onibus | id_linha | id_cidade → cidade.id_cidade | Cada linha referencia uma cidade |

A API grava id_cidade na linha e devolve também cidade: "Maringá".

## 1. Baixar e organizar no VS Code

Extraia o ZIP. A pasta TRANSURBAN_BACKEND contém o backend e este guia.
No seu repositório TRANSURBAN, crie uma pasta chamada backend_revisao_ds na raiz. Copie para ela os arquivos do pacote. Essa pasta separa esta revisão do backend e da avaliação já existentes nos prints. Não substitua nem apague essas pastas.
Se ainda não tem uma cópia do repositório, no terminal da pasta onde guarda seus projetos execute:

```bash
git clone https://github.com/josehenriquefelix-sketch/TRANSURBAN.git
cd TRANSURBAN
code .
```

Se já tem a cópia local, use-a. O clone requer acesso ao repositório.
No VS Code: Arquivo → Abrir Pasta → selecione TRANSURBAN; Terminal → Novo Terminal.
Entre na nova pasta: `cd backend_revisao_ds`.

## 2. Criar ambiente e instalar

Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Se o PowerShell bloquear a ativação, é possível usar o Python do ambiente diretamente, sem mudar políticas:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```
No VS Code: Ctrl+Shift+P → Python: Select Interpreter → escolha o Python de .venv.
O .env inicial usa SQLite local para demonstração. Para a entrega com Supabase, siga a etapa 3 antes de iniciar o servidor.

## 3. Configurar Supabase

Abra https://supabase.com/dashboard e entre no projeto TRANSURBAN chamado transurban, conforme seu print.
Clique em Connect → escolha a URI do Session pooler, porta 5432. Esse modo atende redes IPv4; a conexão direta pode exigir IPv6.
Copie a URI mostrada pelo SEU projeto. Não invente host, região ou identificador.
Substitua o marcador de senha pela senha do banco (não pela chave anon, service_role ou senha da conta).
No .env, deixe apenas a linha DATABASE_URL com a URI real, usando o formato:

```dotenv
DATABASE_URL=postgresql+psycopg2://postgres.REFERENCIA:SENHA_CODIFICADA@HOST_DO_SESSION_POOLER:5432/postgres?sslmode=require
```

Os valores acima são placeholders. Preserve usuário e host da URI copiada. Se a URI já tiver parâmetros, acrescente `&sslmode=require` em vez de outro `?`.
Se a senha contém @, #, /, %, :, ou outros caracteres especiais, codifique apenas a senha na URI. Você pode gerar o valor sem exibi-la na entrada do terminal:

```bash
python -c 'from getpass import getpass; from urllib.parse import quote; print(quote(getpass("Senha do banco: "), safe=""))'
```

Copie o resultado para a parte da senha no .env; não compartilhe a URI nem prints desse arquivo.
Não acrescente `pgbouncer=true`: esse parâmetro não é uma opção de conexão do psycopg2.

No Table Editor confira as tabelas existentes no schema public:
- cidade: id_cidade (PK inteira, com geração automática) e nome.
- linha_onibus: id_linha (PK inteira, com geração automática), id_cidade (FK), codigo e nome.

O backend cria essas duas tabelas se elas não existirem. `create_all` NÃO altera tabelas existentes nem corrige campos, PKs ou FKs. Se seu banco possui uma estrutura diferente, compare o DER e ajuste o código antes de usar; não apague tabelas para tentar resolver.
Para inspecionar sem modificar dados, use o SQL Editor:

```sql
select table_name, column_name, data_type, is_nullable, column_default
from information_schema.columns
where table_schema = 'public' and table_name in ('cidade', 'linha_onibus')
order by table_name, ordinal_position;

select tc.table_name, tc.constraint_name, tc.constraint_type,
       kcu.column_name, ccu.table_name as tabela_referenciada,
       ccu.column_name as coluna_referenciada
from information_schema.table_constraints tc
join information_schema.key_column_usage kcu
  on tc.constraint_name = kcu.constraint_name
 and tc.constraint_schema = kcu.constraint_schema
left join information_schema.constraint_column_usage ccu
  on tc.constraint_name = ccu.constraint_name
 and tc.constraint_schema = ccu.constraint_schema
where tc.table_schema = 'public'
  and tc.table_name in ('cidade', 'linha_onibus')
  and tc.constraint_type in ('PRIMARY KEY', 'FOREIGN KEY')
order by tc.table_name, tc.constraint_type;
```

## 4. Iniciar API

Na pasta onde main.py está e com ambiente ativo:
```bash
python -m uvicorn main:app --reload
```
Abra http://127.0.0.1:8000/docs no mesmo computador.
Se aparecer `Attribute app not found`, confira que main.py foi salvo e que está na pasta correta.
Se ocorrer `Network is unreachable`, confira se você está usando Session pooler, e não o host de conexão direta IPv6.
Se houver erro de autenticação, confira senha, codificação, usuário e host sem publicar a URI.

## 5. Testar em /docs

1. Execute primeiro GET /cidades. Se Maringá já existe, use seu id_cidade e pule o cadastro. Seu print mostra uma restrição UNIQUE no nome da cidade; repetir um nome existente pode retornar HTTP 409. Se não existir, abra POST /cidades → Try it out → envie:
```json
{"nome": "Maringá"}
```
2. Execute. Espere HTTP 201 e anote o id_cidade real retornado.
3. Execute GET /cidades. A cidade deve aparecer na lista.
4. Abra POST /linhas. Substitua 1 pelo id_cidade realmente retornado:
```json
{"codigo": "TESTE-01", "nome": "Linha de demonstração", "id_cidade": 1}
```
Os dados da linha são fictícios, usados só para evidência acadêmica.
5. Espere HTTP 201 com id_linha, codigo, nome, id_cidade e cidade: "Maringá".
6. Execute GET /linhas e confirme que o nome da cidade aparece.
7. Teste um id_cidade positivo comprovadamente inexistente, por exemplo 999999 após conferir que não está cadastrado:
```json
{"codigo": "TESTE-ERRO", "nome": "Linha inválida", "id_cidade": 999999}
```
Espere HTTP 404 e `{"detail":"Cidade não encontrada"}`. Esse cadastro não deve ser inserido.
8. No Supabase → Table Editor confira que a linha válida armazena o id_cidade. Faça prints das respostas e do relacionamento, sem mostrar senhas.

## 6. O que explicar na apresentação

- database.py: lê .env, cria engine, Base e SessionLocal.
- models.py: mapeia tabelas, PK, FK e relationship.
- schemas.py: valida entradas e define formato das respostas; rejeita nomes vazios e IDs não positivos.
- main.py: cria app, abre/fecha sessões, valida a cidade, cadastra e consulta.
- PK identifica um registro; FK liga uma linha a uma cidade existente.
- ForeignKey é a regra no banco; relationship permite acessar linha.cidade.nome em Python.
- POST cadastra; GET consulta. O banco guarda ID; a API acrescenta o nome compreensível.

## 7. GitHub — repositório já existente

Pare a API com Ctrl+C. No terminal vá à raiz do repositório (`cd ..` se estiver diretamente dentro do backend).
```bash
git status
git remote -v
git branch --show-current
```
Se já existe origin, não use `git remote add origin` novamente. Confira se é o repositório TRANSURBAN.
Prepare apenas a pasta desta revisão:
```bash
git add backend_revisao_ds/
git diff --cached --stat
git diff --cached
```
Confira que .env e .venv NÃO aparecem. Você pode verificar a regra:
```bash
git check-ignore -v backend_revisao_ds/.env
```
Se o .env já estiver rastreado por um commit anterior, .gitignore não remove esse rastreamento. Retire-o do índice com `git rm --cached backend_revisao_ds/.env`, mantendo o arquivo local. Se uma senha real já foi publicada, troque-a no Supabase.
Depois de testar e revisar:
```bash
git commit -m "backend TRANSURBAN com cidades e linhas relacionadas"
git push
```
Se o Git informar que a branch não tem upstream, use `git push -u origin NOME_DA_BRANCH`, substituindo pela branch real. Faça login pelo fluxo oferecido pelo VS Code/Git; não use a senha da conta GitHub como token.
Se o push for recusado porque existem mudanças remotas, execute `git fetch origin`, revise as mudanças e integre-as antes de repetir. Não use force push.
Abra o repositório no GitHub e confirme os arquivos na pasta do backend. Não envie .env nem .venv.

Para um repositório novo e vazio, em vez disso: crie-o no GitHub sem README inicial; use git init, git add, git commit, git branch -M main, git remote add origin URL_REAL e git push -u origin main. Não execute esse percurso dentro de uma cópia que já possui Git.

## 8. Teste automatizado e encerramento

Os testes usam banco SQLite temporário separado, sem alterar o Supabase:
```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```
Para encerrar: Ctrl+C e depois `deactivate` (se ativou o ambiente).
Para retomar: ative .venv e execute novamente Uvicorn.

## Estado real da entrega

Código criado e testado no ambiente de preparação, com SQLite temporário.
Inclui configuração para PostgreSQL/Supabase, mas a conexão com seu projeto Supabase NÃO foi executada aqui. Os arquivos NÃO foram instalados no seu PC nem enviados ao GitHub.
A conclusão da entrega depende de executar as etapas com sua conexão real, guardar evidências e fazer o push.

Referências oficiais:
- https://fastapi.tiangolo.com/tutorial/sql-databases/
- https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
- https://supabase.com/docs/guides/database/connecting-to-postgres
- https://docs.github.com/pt/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github
