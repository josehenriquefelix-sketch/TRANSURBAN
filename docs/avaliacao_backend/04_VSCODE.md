# Uso do VS Code

Abra TRANSURBAN.code-workspace na raiz da entrega, usando File → Open Workspace from File. A pasta correta termina em outputs/TRANSURBAN. Uma cópia antiga em Documents/TRANSURBAN não contém necessariamente esta implementação.

As extensões Python, Pylance e Python Debugger foram encontradas instaladas neste computador. Se o editor mostrar Restricted Mode, a decisão de confiar neste workspace precisa ser confirmada pelo usuário antes de executar tarefas ou depurar.

O projeto inclui:
- .vscode/settings.json com interpretador backend/.venv/Scripts/python.exe.
- .vscode/launch.json com execução do Uvicorn dentro de backend e leitura de backend/.env.
- .vscode/tasks.json com tarefas de instalação e execução.
- .vscode/extensions.json com as extensões recomendadas.

A .venv foi criada dentro de backend e testada com Python 3.13.15. O .env real também existe localmente e é ignorado pelo Git. Não publique nenhum deles. O arquivo .env.example não contém segredos.

Para selecionar o interpretador, abra um arquivo .py, use Ctrl+Shift+P → Python Select Interpreter e selecione backend/.venv/Scripts/python.exe. Para depurar, use Run and Debug → TRANSURBAN API. Pare qualquer outro servidor na porta 8000 antes de iniciar outro.

O terminal novo abre na raiz do workspace. Digite cd backend antes dos comandos do roteiro. Também é possível usar a tarefa TRANSURBAN: iniciar API, cujo diretório já está configurado.

## Ambiente local incluído neste computador

A pasta .local-postgres contém o runtime e os dados privados do PostgreSQL isolado da validação. Ela não faz parte do pacote de código nem do Git. O banco escuta somente 127.0.0.1:55439 e usa senha aleatória local.

Se o banco estiver parado, abra um terminal PowerShell na raiz do workspace e execute:

```powershell
.\.local-postgres\runtime\pgsql\bin\postgres.exe -D .\.local-postgres\data -h 127.0.0.1 -p 55439
```

Mantenha esse terminal aberto. Em outro terminal na raiz:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Site: http://127.0.0.1:8000/site/
Documentação da API: http://127.0.0.1:8000/docs

Para encerrar o banco de forma controlada, em um terceiro terminal na raiz:

```powershell
.\.local-postgres\runtime\pgsql\bin\pg_ctl.exe -D .\.local-postgres\data -m fast -w stop
```

O ZIP do código não inclui esse runtime nem a .venv. Em outro computador, instale PostgreSQL e recrie o ambiente seguindo 01_ROTEIRO.md. A .venv não deve ser copiada entre computadores.

## Conectar ao Supabase sem expor senha no chat

A estrutura do projeto lsnpvokfnvyjkvqzkvof já foi inspecionada pelo painel. Não execute init_db.py nele, pois as tabelas já existem.

Em backend, o utilitário configurar_supabase.py pede host, usuário, porta e senha no próprio terminal. A senha não é exibida durante a digitação. O utilitário codifica a senha para URL e grava somente DATABASE_URL em .env, preservando TEST_DATABASE_URL local:

```powershell
.\.venv\Scripts\python.exe configurar_supabase.py
```

Esse passo deve ser executado pelo usuário para informar a credencial privada. Depois reinicie a API e teste GET /cidades e GET /linhas. A autenticação do painel web não fornece automaticamente a senha de conexão PostgreSQL à API.

## Atalho simples para este projeto

No Explorador de Arquivos, abra a raiz da entrega e dê duplo clique em CONECTAR_SUPABASE.cmd. O atalho executa o utilitário com --transurban e já informa o host, o usuário, a porta e o banco conferidos no painel. Digite somente a senha do banco no prompt oculto e pressione Enter. Se a conexão não for confirmada, o .env é preservado. Se funcionar, DATABASE_URL é atualizada, TEST_DATABASE_URL é mantida e a mensagem pede reiniciar a API. A senha do banco é diferente da senha de login do GitHub. A execução com credencial real continua dependendo do usuário.
