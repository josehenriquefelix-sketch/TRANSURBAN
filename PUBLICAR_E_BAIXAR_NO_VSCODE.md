# Publicar no GitHub e abrir no PC do auditório pelo VS Code

São duas etapas em computadores diferentes. Primeiro publique a revisão preparada. Só depois baixe no PC do auditório. Enquanto isso não acontecer, o repositório remoto pode continuar com a versão anterior.

## 1. Neste computador: publicar a revisão pronta

No VS Code, abra o workspace `TRANSURBAN.code-workspace` da entrega atual. O caminho nesta máquina é:

```text
C:\Users\josep\Documents\Codex\2026-10-20\quero-refazer-a-api-e-os\outputs\TRANSURBAN\TRANSURBAN.code-workspace
```

Abra Terminal → New Terminal. O terminal deve estar na raiz TRANSURBAN, onde aparecem backend, frontend e GUIA_AUDITORIO.md.

Confira:

```powershell
git status
git log -1 --oneline
git remote -v
```

O origin precisa ser `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`. O commit da revisão preparada descreve a API, o site responsivo e o ensaio local para o auditório.

O código foi revisado e o commit local está preparado. Para enviá-lo para a branch principal:

```powershell
git push origin HEAD:main
```

Se abrir uma autenticação, conclua o login do GitHub pelo navegador/VS Code. Não envie senha nem token em mensagens. Não use `--force`. Esse comando envia a revisão atual para main, mesmo que o nome da branch local seja refazer-backend-documento-original.

Nesta sessão, a tentativa de publicação não foi concluída porque o terminal não conseguiu acessar o gerenciador de credenciais do Windows. O comando deve ser executado pelo usuário no terminal normal do VS Code, com sua autenticação. Não confunda ter um commit local com ter publicado no GitHub.

Depois do sucesso, abra o repositório no GitHub, selecione main e confirme que existem `GUIA_AUDITORIO.md`, `preparar.py` e `backend/executar_auditorio.py`. Se o push for rejeitado por alterações remotas ou proteção de branch, preserve o trabalho e resolva a atualização/PR antes de continuar; não force sobrescrita.

## 2. No PC do auditório: conferir os programas

Faça isso antes do dia, com internet e tempo para corrigir a instalação.

É necessário Git, Python 3.13, VS Code e PostgreSQL. Para a opção de banco em container, também é necessário Docker Desktop instalado e em execução.

No terminal do VS Code:

```powershell
git --version
python --version
code --version
```

`python --version` precisa mostrar 3.13.x. Se algum comando não existir, prepare o programa antes de continuar. Não tente instalar tudo durante a apresentação.

## 3. Baixar o código atualizado

Escolha uma pasta para os projetos no PC do auditório e abra um terminal nela:

```powershell
git clone https://github.com/josehenriquefelix-sketch/TRANSURBAN.git
cd TRANSURBAN
python preparar.py
code TRANSURBAN.code-workspace
```

O comando de clonagem funciona para a revisão nova somente depois da etapa 1. Se `preparar.py` não estiver presente, pare e confira se a publicação correta chegou a main.

`preparar.py` cria backend/.venv, instala as dependências e cria .env a partir do exemplo somente se ele não existir. Não leva a senha do Supabase para outro computador.

Se já houver uma cópia no PC do auditório, dentro dela confira `git status`. Com a main limpa:

```powershell
git switch main
git pull --ff-only
python preparar.py
code TRANSURBAN.code-workspace
```

Não execute clone dentro de uma pasta TRANSURBAN que já contenha outra cópia. Não descarte alterações locais para fazer o pull.

## 4. Preparar PostgreSQL local no PC do auditório

Com Docker Desktop instalado e aberto, execute na raiz do projeto:

```powershell
docker compose up -d banco
docker compose ps
```

Aguarde o banco ficar saudável. O exemplo de .env aponta para esse container local, na porta 54329. Se já existir um .env com outra configuração, ele é preservado; ajuste TEST_DATABASE_URL privadamente para um PostgreSQL local.

A instalação com Docker ainda precisa ser ensaiada no computador que terá Docker. Na máquina usada nesta revisão, os testes e a API foram executados com um PostgreSQL local já preparado. O Git não instala PostgreSQL nem substitui esse requisito. Veja GUIA_AUDITORIO.md para os dois caminhos.

## 5. Iniciar um ensaio manual novo

Dentro de backend:

```powershell
cd backend
.\.venv\Scripts\python.exe executar_auditorio.py --schema transurban_auditorio_palco --vazio
```

Mantenha esse terminal aberto. `--vazio` significa não cadastrar cidades automaticamente; ele não apaga dados existentes. Se já usou esse schema em um treino, escolha palco2 para um novo ensaio. No teste de persistência, reinicie com o MESMO nome que foi usado no início.

Abra:

- Swagger: http://127.0.0.1:8001/docs
- Site: http://127.0.0.1:8001/site/

## 6. Conferir antes da apresentação

Em OUTRO terminal do VS Code, dentro de backend:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe verificar_http.py --base-url http://127.0.0.1:8001
```

Conferir a própria execução: referência desta revisão é 18 testes aprovados, um aviso de depreciação sem falha, nenhuma dependência quebrada e 13 verificações HTTP aprovadas. Depois, ensaiar o roteiro manual de POST/GET, 409, 404, 422 e persistência em docs/apresentacao/ROTEIRO_COMPLETO.md.

Os 9 minutos são para explicar e demonstrar os testes. Instalação, publicação, download e configuração do banco ficam fora desse tempo.
