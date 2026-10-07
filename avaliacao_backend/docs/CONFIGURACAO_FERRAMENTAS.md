# Configuração das ferramentas

## VS Code

Abra `TRANSURBAN.code-workspace` na raiz. Selecione o Python da venv pelo comando **Python: Select Interpreter**. Na nuvem, o caminho é `/workspace/.venvs/transurban/bin/python`; no computador pessoal, recrie a `.venv` conforme o README.

Em **Run and Debug**, selecione **TRANSURBAN: API DS + IA** para iniciar Uvicorn ou **TRANSURBAN: análise do CSV** para executar a análise. Os atalhos leem a configuração privada `.env` do pacote. Em **Terminal → Run Task**, há tarefas para instalar dependências e executar os testes.

As configurações JSON foram validadas. O backend e a conexão carregada do `.env` foram executados na nuvem; a interface do VS Code do computador pessoal não foi operada nesta sessão.

## Supabase

Projeto informado: https://supabase.com/dashboard/project/lsnpvokfnvyjkvqzkvof/database/schemas

A conexão remota ainda não está configurada. No painel do projeto, abra **Connect** e obtenha os dados do método de conexão disponível para seu ambiente. O link do painel não é uma string de conexão. Mantenha os dados privados em `avaliacao_backend/.env`, que está ignorado pelo Git:

```dotenv
DATABASE_URL=postgresql+psycopg2://USUARIO:SENHA_CODIFICADA@HOST:PORTA/BANCO
PGSSLMODE=require
```

Use o usuário, host e porta fornecidos pelo próprio painel e codifique os caracteres especiais da senha. Não use a chave anon como senha de PostgreSQL e não publique a conexão. A configuração local preparada na nuvem aponta para PostgreSQL local; ela não comprova acesso ao projeto Supabase.

Antes de modificar tabelas, execute a auditoria de leitura `sql/01_auditar_supabase.sql` e compare PKs, FKs, campos e geração de IDs. A aplicação não cria tabelas PostgreSQL ao iniciar. Não execute o SQL de banco novo sobre um banco existente. Valide `/health`, POST/GET e os mesmos IDs no banco de demonstração autorizado antes de registrar evidência remota.

## GitHub

Código, configurações e evidências estão na branch `entrega/backend-ds-ia-nuvem-2026-10-07` do repositório `josehenriquefelix-sketch/TRANSURBAN`. As mudanças da entrega foram publicadas nessa branch; isso não significa incorporação à `main`.

## brModelo

O modelo lógico editável está em `modelagem/TRANSURBAN_Cidade_Linha.brM3`. Veja `modelagem/README.md` para versão e validação. A extensão nativa do brModelo 3 é `.brM3`.

## Classroom

Atividade informada: https://classroom.google.com/c/Nzk3Njk5MjgxNDA4/a/ODY5OTk0NjE0MzIx/details

O envio ainda não foi realizado. Esta sessão não tem acesso autenticado ao Classroom. Anexe o pacote da entrega e o link da branch na atividade correspondente; confira os anexos antes de concluir o envio. Os relatórios devem distinguir PostgreSQL local validado de Supabase remoto pendente.
