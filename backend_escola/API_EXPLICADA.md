# API TRANSURBAN — guia para executar, entender e apresentar

Esta é a API Python do pacote `TRANSURBAN_BACKEND.zip` enviado para a revisão da escola. Ela cadastra e consulta **cidades** e **linhas de ônibus**. Foi adaptada do exemplo Categoria → Produto para o domínio do TRANSURBAN.

**Atualização de 19/10:** a versão 1.1 integra também a análise do CSV, `/health` e o dashboard `/painel/` no mesmo servidor. Os cadastros já existentes e o `.env` local são preservados. Veja `FINALIZAR_ENTREGA.md` para o roteiro atualizado de DS + IA e a auditoria privada do Supabase.

## 1. API, site e banco: quem faz o quê?

O site é a interface que uma pessoa vê e usa. A API recebe pedidos HTTP e devolve dados JSON. O banco guarda os registros. Swagger, em `/docs`, é uma interface para testar a API; não é o site final para passageiros.

```mermaid
flowchart LR
    U[Site ou Swagger] -->|Pedido GET ou POST| A[FastAPI]
    A -->|Valida entrada| S[Schema Pydantic]
    S -->|Operação com sessão| O[SQLAlchemy e models]
    O <-->|Consulta ou gravação| B[(SQLite ou PostgreSQL)]
    O -->|Resultado| A
    A -->|Resposta JSON e status HTTP| U
```

O site V2 em `site_v2/` tem um servidor próprio. Colocar ambos no mesmo GitHub não conecta automaticamente esse site a esta API Python. O painel DS/IA em `avaliacao_backend/` também é um pacote separado, com suas próprias instruções.

## 2. A relação Cidade → Linha de ônibus

| Tabela | Campo | Responsabilidade |
|---|---|---|
| cidade | id_cidade | PK: identifica uma cidade; gerada pelo banco quando o esquema oferece autoincremento |
| cidade | nome | Nome da cidade, obrigatório, até 100 caracteres |
| linha_onibus | id_linha | PK: identifica uma linha |
| linha_onibus | id_cidade | FK obrigatória que aponta para cidade.id_cidade |
| linha_onibus | codigo | Código textual, até 20 caracteres; pode preservar zeros como 001 |
| linha_onibus | nome | Nome da linha, obrigatório, até 150 caracteres |

Uma cidade pode ter zero ou várias linhas. Cada linha precisa de exatamente uma cidade existente. O cadastro da linha usa o ID da cidade; a consulta devolve também seu nome.

**ForeignKey** estabelece a referência no banco. **relationship** permite navegar entre objetos Python: `linha.cidade.nome`. Uma coisa não substitui a outra.

Este pacote não declara unicidade do nome da cidade nem do par cidade/código. Portanto, nomes e códigos repetidos podem ser cadastrados. Não apresente proteção contra duplicidade como uma funcionalidade desta versão; o pacote DS/IA separado tem regras diferentes.

## 3. Responsabilidade dos arquivos

| Arquivo | O que faz |
|---|---|
| database.py | Lê `.env`, obtém DATABASE_URL, cria engine, fábrica de sessões e Base; habilita FK no SQLite |
| models.py | Representa as tabelas e seus relacionamentos com SQLAlchemy |
| schemas.py | Valida o JSON de entrada e define os dados de saída com Pydantic |
| main.py | Cria o app FastAPI, registra rotas e coordena consulta, cadastro e resposta |
| requirements.txt | Fixa versões das dependências de execução |
| requirements-dev.txt | Acrescenta ferramentas de teste |
| test_backend.py | Exercita o fluxo completo em SQLite temporário |
| .env.example | Exemplo de configuração, sem credencial real |
| .env | Configuração privada local; não deve ser versionada |
| iniciar-linux.sh | Prepara a venv da escola e inicia a API ou os testes |

Uma sessão de banco é fornecida por `get_db` para cada requisição e fechada em `finally`. A engine administra o acesso ao banco; a sessão administra o trabalho de uma requisição.

## 4. Iniciar no computador Linux da escola

Abra a pasta `backend_escola` no VS Code. No terminal dessa pasta, execute:

```bash
bash iniciar-linux.sh
```

O script cria `.venv-escola`, instala as dependências fixadas e mantém seu `.env` existente. Se não houver configuração, prepara SQLite em `transurban_escola.db`. Não altera o backend antigo do computador.

Espere `Application startup complete` e deixe o terminal aberto. Abra no mesmo computador:

```text
http://127.0.0.1:8000/docs
```

`127.0.0.1` significa o computador em que o navegador está aberto. Um processo iniciado na nuvem não aparece nesse endereço no computador da escola.

Se já estiver instalado, também pode iniciar diretamente:

```bash
./.venv-escola/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

`main` é o arquivo `main.py`; `app` é a instância FastAPI dentro dele. `--reload` reinicia o servidor quando o código muda. Use Ctrl+C para encerrar. Na próxima vez, execute novamente o script. Como o iniciador usa o Python da venv diretamente, não precisa ativar ou desativar o ambiente no terminal.

Se a porta estiver ocupada, encerre somente seu servidor antigo no terminal correspondente ou use `--port 8001` e abra `/docs` nessa porta. Não apague bancos ou ambientes para resolver erro de porta.

## 5. Todas as rotas desta API

| Método | Rota | Entrada | Resposta esperada |
|---|---|---|---|
| GET | / | Nenhuma | 200, mensagem de funcionamento |
| POST | /cidades | nome | 201, id_cidade e nome |
| GET | /cidades | Nenhuma | 200, lista de cidades por ID |
| POST | /linhas | codigo, nome, id_cidade | 201, linha com nome da cidade |
| GET | /linhas | Nenhuma | 200, lista de linhas com nome da cidade |
| GET | /docs | Nenhuma | Documentação interativa Swagger |
| GET | /openapi.json | Nenhuma | Contrato das rotas e schemas |
| GET | /health | Nenhuma | Verifica conexão com o banco e identifica o modo local/PostgreSQL |
| GET | /ia/resumo | Nenhuma | Contagem, soma, média, mediana e limites da fonte |
| GET | /ia/qualidade | Nenhuma | Auditoria do CSV |
| GET | /ia/agrupamentos/{dimensao} | Dimensão na URL | Indicadores por linha, data, cidade, período, trânsito, clima ou trecho |
| GET | /ia/maiores-atrasos | Nenhuma | Todos os registros empatados no maior atraso |
| GET | /painel/ | Nenhuma | Dashboard e formulários integrados à API |

A API não possui GPS real ou autenticação de passageiros. GET `/` comprova que o servidor responde; GET `/health`, `/cidades` e `/linhas` também exercitam a conexão ao banco. O dashboard usa as rotas desta mesma API; o site V2 e o `frontend-app` do computador da escola continuam componentes distintos.

## 6. Demonstração passo a passo no Swagger

### A. Cadastrar a cidade

Abra POST `/cidades`, clique em **Try it out**, informe o JSON e clique em **Execute**:

```json
{"nome":"Maringá"}
```

Espere 201 e anote o `id_cidade` retornado. O ID pode variar conforme o conteúdo do banco.

### B. Consultar a cidade

Execute GET `/cidades`. A lista deve incluir a cidade recém-criada com o mesmo ID.

### C. Cadastrar uma linha relacionada

Em POST `/linhas`, use o ID realmente retornado na etapa A. O valor 1 abaixo é somente um exemplo:

```json
{"codigo":"001","nome":"Linha de demonstração","id_cidade":1}
```

Espere 201. A resposta terá `id_linha`, `codigo`, `nome`, `id_cidade` e `cidade`. O campo `cidade` deve mostrar `Maringá` quando a FK aponta para ela.

### D. Consultar a relação

Execute GET `/linhas`. Confira o código, o nome da linha, a FK e o nome da cidade. A consulta usa o relacionamento ORM e carrega a cidade junto da linha.

### E. Testar erro de referência

Escolha um ID de cidade que você confirmou não existir e tente cadastrar outra linha. A API deve responder 404, `Cidade não encontrada`. Faça GET `/linhas` e confira que a tentativa não inseriu a linha.

### F. Testar entrada inválida

Tente POST `/cidades` com `{"nome":"   "}` ou POST `/linhas` com `id_cidade` igual a 0. Espere 422. Os schemas retiram espaços nas extremidades e impõem campos obrigatórios e limites de tamanho.

Esses POSTs criam registros reais no banco configurado. Faça a demonstração em banco de testes autorizado.

## 7. Entender os status e a gravação

| Status | Significado neste projeto |
|---|---|
| 200 | Consulta ou resposta básica concluída |
| 201 | Registro cadastrado |
| 404 | Cidade referenciada não encontrada |
| 409 | O banco rejeitou o cadastro por uma restrição de integridade |
| 422 | O corpo recebido não atende ao schema |

`db.add` coloca o objeto na sessão. `db.commit` confirma a transação. `db.refresh` relê o objeto depois de salvar, incluindo o ID gerado. Em `IntegrityError`, a aplicação faz `rollback` e responde 409. Outros erros de conexão não são automaticamente tratados como 409.

## 8. SQLite local e Supabase

SQLite é um banco em arquivo para ensaio local. Supabase oferece PostgreSQL remoto. Testar SQLite não comprova que a conexão do Supabase funciona.

Para Supabase, use a URI do método de conexão informado pelo painel **Connect** do seu projeto e configure `.env` privadamente. Exemplo de formato, com placeholders:

```dotenv
DATABASE_URL=postgresql+psycopg2://USUARIO:SENHA_CODIFICADA@HOST:PORTA/BANCO?sslmode=require
```

Não use chave anon como senha. Preserve usuário, host e porta do painel. Codifique caracteres especiais da senha na URI e nunca publique `.env` nem fotos dessa configuração. O arquivo `.env` só é lido ao iniciar o processo; reinicie a API depois de alterá-lo.

Na versão 1.1, o `lifespan` cria tabelas automaticamente somente no SQLite local. A inicialização não cria nem migra tabelas remotas. Use `bash iniciar-linux.sh --supabase` para informar a URI em entrada oculta e auditar conexão, campos, tipos, PKs e FK por leitura. A configuração só é salva se a auditoria passar. Um esquema incompatível precisa de revisão separada; não apague tabelas para tentar fazer uma conexão funcionar.

## 9. Testes e evidências

```bash
bash iniciar-linux.sh --testar
```

O teste fornecido usa um banco SQLite temporário e sobrescreve DATABASE_URL apenas no processo de teste. Confere servidor, documentação, POST/GET, ID persistido, nome relacionado, 404, 422 e rejeição de FK inválida por SQL direto.

Na preparação inicial de 19/10/2026, o pacote original passou em **1 teste de integração**, e as cinco consultas HTTP foram executadas com 200. A versão 1.1 possui testes adicionais de IA, dashboard e configuração privada; os resultados atuais estão em `evidencias/integracao-ds-ia-2026-10-19/` e `FINALIZAR_ENTREGA.md`. Os 18 testes da entrega antiga pertencem ao pacote separado `avaliacao_backend`.

Para a apresentação, registre capturas de rota, status e JSON, sem credenciais. A comprovação remota exige que os mesmos registros apareçam no PostgreSQL/Supabase realmente configurado.

## 10. Explicação curta para a apresentação

“A API TRANSURBAN usa Python, FastAPI e SQLAlchemy. Primeiro cadastramos uma cidade com chave primária. Depois cadastramos uma linha de ônibus com sua própria chave primária e uma chave estrangeira para a cidade. Antes de salvar a linha, verificamos se a cidade existe. O banco armazena o ID, enquanto a resposta JSON também apresenta o nome da cidade. Os schemas validam os dados e a sessão é fechada ao final da requisição. Fizemos testes de cadastro, consulta, persistência e entradas inválidas. Nesta preparação a validação foi local; a conexão remota precisa ser comprovada separadamente.”
