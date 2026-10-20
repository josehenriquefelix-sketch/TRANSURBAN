# Roteiro da avaliação de backend do TRANSURBAN

## Fonte e objetivo

Fonte lida integralmente em 20/10/2026: [caderno do professor](https://docs.google.com/document/d/1I6Eh3J15ieVGsnb_DJX6qNugWwOU5nu3qyLK-XR2RNw/edit).
O caderno é genérico e manda adaptar Categoria e Produto ao DER autoral. O [DER](../DER.md) e o [dicionário](../dicionario_dados.md), seções 2 e 3, sustentam Cidade → LinhaOnibus. Cidade não tem FK; LinhaOnibus possui id_cidade. A consulta devolve cidade como nome. As demais entidades do DER não são exigidas neste exercício de duas tabelas.

O código entregue contém o estado final. Os marcos abaixo seguem a ordem didática do caderno e permitem verificar primeiro Cidade e depois Linha. Não é preciso apagar a segunda tabela para demonstrar o primeiro marco.

## 1 Preparar ambiente no Windows PowerShell

Pré-requisitos: Python 3.13 (versão usada na verificação), Git e acesso a um banco PostgreSQL novo de desenvolvimento. Extraia a entrega em uma pasta TRANSURBAN. Abra essa pasta no VS Code. No terminal, confirme que está na raiz, onde aparecem backend e docs.

Execute na raiz:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Se a ativação estiver bloqueada pela política do PowerShell, use o interpretador diretamente, sem mudar a política:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
```

Todos os comandos seguintes são executados em backend. Sem ativação, substitua python por .\.venv\Scripts\python.exe. No VS Code, selecione esse mesmo interpretador em Python Select Interpreter.

Neste computador o .env já existe com a configuração local de desenvolvimento: não o sobrescreva. Em uma instalação nova, copie .env.example e edite .env com a conexão do seu banco. Consulte [02_BANCO.md](02_BANCO.md) antes de criar tabelas. A senha deve ser codificada para URL se contiver caracteres reservados. Nunca copie sua conexão real para documentos, Postman, commits ou capturas públicas.

## 2 Criar as tabelas em banco novo

Depois de configurar .env para um banco novo:

```powershell
python init_db.py
```

Resultado: duas tabelas criadas com PK automática e FK. Se uma das tabelas já existir, o script recusa a operação. Consulte o roteiro de banco; não apague tabelas para contornar a recusa.

## 3 Entender os arquivos estruturantes

| Arquivo dentro de backend | Função |
|---|---|
| database.py | Carrega .env, valida PostgreSQL, cria engine e fornece sessões fechadas ao final |
| models.py | Mapeia cidade e linha_onibus, PK, FK, UNIQUE e relationship |
| schemas.py | Define entrada, saída, limites e validação |
| main.py | Cria FastAPI, registra rotas e trata indisponibilidade do banco |
| routes/cidades.py | POST e GET da entidade sem FK |
| routes/linhas.py | POST e GET da entidade dependente |
| services.py | Confirma transação e trata conflitos com rollback |
| init_db.py | Cria explicitamente as duas tabelas em banco novo |

ForeignKey mantém a integridade no banco. relationship permite navegar de linha para cidade no Python. O Pydantic transforma a resposta em JSON e valida entradas; não substitui as restrições do PostgreSQL.

## 4 Iniciar

Na pasta backend:

```powershell
python -m uvicorn main:app --reload
```

Abra http://127.0.0.1:8000/docs. A API deve apresentar Cidades, Linhas e Sistema. GET / apenas confirma que a aplicação responde; os testes de cadastro e consulta comprovam a conexão com o banco.

## 5 Marco 1 Cidade com PK

Em /docs, use POST /cidades, Try it out, envie:

```json
{"nome":"Maringá"}
```

Espere HTTP 201 e um corpo como:

```json
{"id_cidade":1,"nome":"Maringá"}
```

O ID mostrado é ilustrativo: anote o ID real. Execute GET /cidades e confira o cadastro. Repita com Sarandi para demonstrar outra cidade. Não envie id_cidade no POST: o banco o gera.

## 6 Marco 2 Linha com FK

Em POST /linhas, substitua 1 pelo ID real de Maringá:

```json
{"codigo":"TESTE-001","nome":"Linha acadêmica Maringá Sarandi","id_cidade":1}
```

Espere HTTP 201 e:

```json
{"id_linha":1,"codigo":"TESTE-001","nome":"Linha acadêmica Maringá Sarandi","cidade":"Maringá"}
```

Execute GET /linhas. O nome da cidade deve aparecer. O banco guarda id_cidade; a API consulta o relacionamento e retorna cidade. O ID da linha também é apenas ilustrativo.

## 7 Erros e persistência

- Envie linha com id_cidade positivo que não exista, por exemplo 999999 após conferir a lista. Espere 404 e {"detail":"Cidade não encontrada"}.
- Envie cidade com nome composto só por espaços: 422.
- Envie linha sem código ou com id_cidade igual a zero: 422.
- Repita o mesmo nome de cidade: 409.
- Repita o mesmo código na mesma cidade: 409. O mesmo código em outra cidade é permitido pelo dicionário.
- Pare e reinicie a API. Consulte GET /cidades e GET /linhas: os registros devem permanecer. Confira também o SELECT do roteiro de banco.

## 8 Testes automatizados

Use um PostgreSQL exclusivo de testes. A suíte cria um schema aleatório por caso e remove somente esse schema ao final. Ela não usa SQLite. Não aponte para produção nem copie DATABASE_URL para TEST_DATABASE_URL.

Na entrega desta máquina, backend/.env já mantém TEST_DATABASE_URL no PostgreSQL local isolado, mesmo com DATABASE_URL apontando para o Supabase. Em outra instalação, configure TEST_DATABASE_URL com uma conexão exclusiva de testes antes de executar. O arquivo .env é carregado pelo código, sem imprimir sua senha.

Na pasta backend, com o ambiente ativo:

```powershell
python -m pip install -r requirements-test.lock.txt
python -m pytest tests -v
```

Se houver TEST_DATABASE_URL exportada no ambiente do terminal, confira privadamente se ela corresponde ao banco de testes. Não publique seu valor. Variáveis do ambiente têm prioridade sobre as variáveis carregadas do .env.

## 9 Encerrar e retomar

No terminal do servidor, pressione Ctrl+C e espere o prompt voltar. Se ativou a .venv, execute deactivate. O PostgreSQL e os registros continuam salvos. Para retomar, abra backend, ative a .venv e execute novamente python -m uvicorn main:app --reload.

## 10 Versionar após conferir

Na raiz do repositório:

```powershell
git status --short
git check-ignore backend/.env backend/.venv/
git diff --check
git diff
```

Confira se não há segredos e se as verificações passaram. Prepare somente os arquivos desta entrega e faça um commit local. Não use git add . sem revisar o conteúdo. O envio por git push é uma etapa separada, que não foi executada nesta entrega, pois o usuário vedou publicação sem autorização.

## 11 Desafio de compreensão

Sem implementar novas rotas, explique a entidade trecho do DER: id_trecho é PK; id_cidade_origem e id_cidade_destino são FKs de cidade. O banco guarda IDs; uma futura resposta poderia mostrar os nomes das cidades. Isso responde à seção 16 do caderno sem ampliar o escopo da API.

## Site integrado solicitado posteriormente

Com o mesmo Uvicorn em execução, abra http://127.0.0.1:8000/site/. Cadastre uma cidade, selecione-a para cadastrar uma linha e confira as tabelas. Atualizar consultas recarrega o banco. Documentação da API abre /docs. Não abra index.html diretamente pelo sistema de arquivos, porque a página utiliza rotas HTTP relativas.
