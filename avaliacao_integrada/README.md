# TRANSURBAN — Recuperação DS e integração DS + IA

## Ficiências 2026

O [guia do evento](docs/FICIENCIAS_2026.md) descreve a preparação do computador e o percurso pelo sistema. Na raiz do repositório, `INICIAR_TRANSURBAN.cmd` abre a aplicação e `VERIFICAR_TRANSURBAN.cmd` confere dependências, configuração, tabelas, arquivos da interface e documentação. O verificador realiza somente consultas.

## Portal de mobilidade — atualização de novembro de 2026

O produto é destinado à população de Maringá e Sarandi. A interface pública apresenta informações de mobilidade com fonte e data. Os indicadores sintéticos e as operações de teste ficaram restritos à conta da equipe na interface. A consulta operacional de horários, o envio de avaliações sobre veículos reais e a recarga efetiva dependem de integração e validação com a operadora. Essas pendências são informadas nas respectivas telas. As atividades e evidências acadêmicas abaixo documentam o desenvolvimento do sistema.

O portal inclui telas de login por e-mail ou CPF, cadastro de conta, recuperação de senha, início, dashboard, cidades, linhas, trajetos/horários, avaliações e passe demonstrativo. A interface usa HTML, CSS e JavaScript. A API usa Python/FastAPI e o banco usa Supabase/PostgreSQL por HTTPS.

- Site em `http://127.0.0.1:8000/`.
- Swagger de Desenvolvimento de Sistemas em `/docs`. As totalizações de IA foram retiradas desse Swagger.
- Swagger de Ciência de Dados em `/dados/docs`. Os endpoints `/ia/*` continuam disponíveis para a atividade acadêmica e o dashboard.
- O dashboard apresenta documentos oficiais com links e datas, seguidos das quatro totalizações do CSV sintético.
- Passageiros e motoristas consultam cidades e linhas cadastradas. Alterações exigem sessão e e-mail autorizado em `ADMIN_EMAILS` no `.env` do backend.
- Contas e senhas são administradas pelo Supabase Auth. A sessão fica em cookies HttpOnly. O CPF é validado e seu resumo SHA-256 é gravado para a busca de login.
- Avaliações e carteira são vinculadas ao usuário autenticado. Os endpoints filtram os dados pelo usuário validado pelo Supabase.
- Os trajetos, horários, veículos e motoristas do módulo de consulta são demonstrativos. A recarga é fictícia, sem integração com pagamento ou bilhetagem da operadora. Cada operação usa uma chave única e uma transação no PostgreSQL para evitar duplicação.

### Preparar o banco e as contas

No projeto Supabase da equipe a migração `database/05_portal.sql` já foi aplicada. Ao usar esse mesmo projeto em outro computador, não é necessário executá-la novamente. Em um banco novo, prepare primeiro as tabelas de cidades e linhas e depois execute `05_portal.sql` no SQL Editor. O script é transacional e pode ser repetido.

Em Authentication → URL Configuration, configure o Site URL como `http://127.0.0.1:8000` e autorize o retorno para `http://127.0.0.1:8000/**`. Essas URLs já foram configuradas no projeto da equipe. Para hospedagem, use a URL HTTPS do site, ajuste `APP_URL` e configure `COOKIE_SECURE=true`.

O cadastro público solicita confirmação de e-mail conforme a configuração do Supabase. Entrega de mensagens depende da configuração e dos limites do serviço de e-mail do projeto. Valide o recebimento com o endereço real que será usado antes da apresentação. Para envio a público externo, configure o SMTP do projeto.

Uma conta fictícia da equipe foi preparada para os testes de apresentação. Suas credenciais estão apenas no `.env` privado deste computador, nos campos `DEMO_EMAIL`, `DEMO_PASSWORD` e `DEMO_CPF`. Os e-mails com acesso aos cadastros ficam em `ADMIN_EMAILS`. Novas contas recebem acesso de passageiro. Credenciais de apresentação também devem ser transferidas por meio privado.

### Abrir no computador da escola

1. No VS Code, use Git → Clonar Repositório com o endereço deste repositório, ou execute `git pull` se o projeto já estiver clonado.
2. Abra a pasta `avaliacao_integrada`.
3. Configure `backend/.env` usando `backend/.env.example` como referência. Use o mesmo projeto Supabase e os e-mails autorizados da equipe. O arquivo privado não vem pelo GitHub.
4. Execute `iniciar_local.cmd`. Ele prepara o ambiente e abre o site. O link da API está no menu do site.

O Windows precisa ter Python 3.10 ou superior disponível no PATH e acesso à internet para instalar dependências e consultar o Supabase. Mantenha o servidor aberto durante o uso. O endereço `127.0.0.1` representa o próprio computador.

### Verificação desta atualização

Os 12 testes automatizados, incluindo seis de regressão e seis de autenticação/permissão/documentação, passaram. Foram realizadas 42 verificações adicionais com FastAPI TestClient e Supabase real, registradas em `docs/EVIDENCIAS_PORTAL_20261110.json`, incluindo login por e-mail/CPF, sessão, logout, restrição de acesso, avaliação, CRUD/FK e recarga idempotente. As duas recargas de demonstração somam R$ 15 na conta fictícia. O teste pela interface também registrou uma avaliação de demonstração. Consulte `docs/EVIDENCIAS_INTERFACE_20261111.json`. O recebimento de e-mail em caixa postal real precisa de validação com o endereço da equipe.

Consulte `docs/PORTAL_E_APRESENTACAO.md` para o roteiro e os limites da demonstração.

Entrega acadêmica integrada com FastAPI, pandas, Supabase por HTTPS, HTML, CSS e JavaScript. A documentação cobre o CRUD, a base de Ciência de Dados, as quatro perguntas, o CORS e o roteiro de conferência.

**Projeto da equipe:** sistema acadêmico sobre transporte coletivo de Maringá e Sarandi. **Professor responsável:** Erinaldo Sanches Nascimento. **Grupo:** preencher os nomes dos integrantes antes da apresentação.

## Conteúdo

- `backend/`: FastAPI, modelos Pydantic, CRUD de cidade e linha por Supabase Data API HTTPS, leitura/validação do CSV, quatro totalizações e configuração de CORS.
- `database/`: consulta de auditoria e DDLs para uma instância vazia. O backend não cria nem modifica tabelas automaticamente.
- `data/atrasos_analise.csv`: base de demonstração e `ORIGEM_DADOS.txt` com a procedência e os limites.
- `frontend/`: painel web adaptável, CRUD de cidades e linhas, e visualização das totalizações da API.
- `docs/`: explicação sobre linha da base e perguntas, resultados conferidos, verificação local e roteiro de apresentação.

## Escopo do CRUD

Em auditoria somente de leitura do projeto Supabase `transurban`, em 28/10/2026, foram encontradas as tabelas públicas `cidade`, `faixa_exclusiva`, `linha_onibus`, `linha_trecho`, `registro_atraso` e `trecho`. As PKs observadas são `cidade.id_cidade`, `faixa_exclusiva.id_faixa`, `linha_onibus.id_linha` e a PK composta de `linha_trecho` (`id_linha`, `id_trecho`). As FKs observadas incluem `faixa_exclusiva.id_trecho`, `linha_onibus.id_cidade`, `linha_trecho.id_linha`/`id_trecho` e `registro_atraso.id_linha`/`id_trecho`. `trecho` e `registro_atraso` não apresentaram PK nessa auditoria. Assim, **`cidade` é a única tabela observada com PK e sem FK**, e é a única incluída no CRUD da recuperação. `linha_onibus` fica disponível na avaliação integrada e preserva sua FK para cidade. O banco não foi alterado durante a auditoria.

## Atividade de chave estrangeira (DS)

O relacionamento autoral aplicado é `cidade` → `linha_onibus`: `cidade.id_cidade` é PK; `linha_onibus.id_linha` é PK e `linha_onibus.id_cidade` é FK. O endpoint `/linhas` guarda o ID da cidade e inclui seu nome consultado na resposta. O CRUD de linhas valida a cidade e a FK do banco impede excluir uma cidade que ainda tenha linhas vinculadas. Consulte o [passo a passo e roteiro de teste da atividade](docs/RELACIONAMENTO_FK_CIDADE_LINHA.md).

No Supabase atual essas tabelas já existem. Não execute DDL de criação sobre elas; os scripts em `database/` são para uma base de demonstração vazia e devem ser revisados após a auditoria.

## Requisitos

- Python 3.10 ou superior.
- Projeto Supabase da equipe com Data API habilitada, esquema `public` exposto e tabela `public.cidade` compatível.
- A chave secreta do Supabase deve ficar apenas em `backend/.env`; nunca no HTML/JavaScript ou no GitHub.
- Git não deve receber `.env`, `.venv` ou senhas. O `.env.example` contém apenas valores fictícios.

## Início rápido no Windows

Guia passo a passo para clonar pelo VS Code, configurar o Supabase e iniciar o site no computador do auditório: [GUIA_RAPIDO_AUDITORIO.md](GUIA_RAPIDO_AUDITORIO.md).

Dê duplo clique em `iniciar_local.cmd` (ou no atalho `ABRIR TRANSURBAN`, se já tiver sido criado). Na primeira execução, o iniciador cria o ambiente, instala as dependências e abre a configuração local se detectar uma URL ou chave de exemplo. Preencha os dados do Supabase neste computador. O iniciador sobe um único serviço que entrega a interface, a API e o Swagger. O painel abre em `http://127.0.0.1:8000/`; a documentação fica em `/docs`. Mantenha a janela da API aberta durante a apresentação. Enquanto o serviço estiver ativo, ele solicita ao Windows que não suspenda o sistema; ao encerrar a API, a solicitação é liberada.

Para usar no computador da escola ou do auditório, atualize ou clone o repositório, abra `avaliacao_integrada` no VS Code e execute o mesmo `iniciar_local.cmd`. Cada computador precisa de sua própria configuração em `backend/.env`; esse arquivo privado não é transferido pelo GitHub. O repositório fornece apenas o `.env.example` fictício.
## Preparação no Windows (PowerShell)

Abra o terminal na pasta `TRANSURBAN_ENTREGA`:

```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

Edite `backend/.env` com a Project URL e a chave secreta do **projeto Supabase correto**. Não use a senha PostgreSQL como chave da API. Em um terminal, na raiz do projeto, inicie o backend:

```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

A FastAPI serve também a interface no mesmo endereço. Abra `http://127.0.0.1:8000/`; o Swagger fica em `http://127.0.0.1:8000/docs`. Mantenha o serviço em `127.0.0.1`; esta versão acadêmica não tem autenticação e não deve ser publicada para acesso público.

No Linux/macOS, crie o ambiente com `python3 -m venv backend/.venv`, instale `backend/requirements.txt`, copie o `.env.example` para `.env` dentro de `backend` e inicie `uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000` na raiz. A própria API serve a interface em `/`.

## Supabase: auditar antes de alterar

1. No projeto correto, abra **SQL Editor** e execute `database/01_auditar_esquema.sql`. Ele somente lê metadados de `public`.
2. Confirme que `cidade` tem `id_cidade` como PK gerada automaticamente e `nome` como texto obrigatório e único. A consulta também lista chaves estrangeiras do esquema.
3. **Não execute DDL de criação em tabela existente.** Se as tabelas não existirem em uma instância vazia de demonstração, revise e então execute `database/02_criar_cidade_banco_novo.sql` seguido de `database/03_criar_linha_banco_novo.sql`. Se a auditoria mostrar uma PK existente sem `IDENTITY` e sem `DEFAULT`, revise o script `database/04_ids_automaticos_existentes.sql`; ele bloqueia escrita durante a sincronização e deve ser executado em período sem alterações.
4. Mantenha RLS habilitada e use a chave secreta só no backend local. O script concede privilégios a `service_role`; não crie política pública `anon` nem desative RLS para esconder erro de configuração.
5. Se a tabela atual usar nomes/tipos/IDs diferentes, pare e adapte o modelo e as rotas ao resultado real. O projeto anterior registra divergências históricas entre versões do DER; este DDL não deve ser aplicado sem auditoria.

## Rotas de Ciência de Dados

| Método | Rota | Pergunta |
|---|---|---|
| GET | `/ia/resumo` | Quantas observações válidas há, qual o período e quais os limites da base? |
| GET | `/ia/totalizacao/cidade` | Quanto atraso foi observado em cada cidade? |
| GET | `/ia/totalizacao/periodo` | Como total e média se distribuem por período do dia? |
| GET | `/ia/totalizacao/transito` | Qual total e média para cada condição de trânsito? |
| GET | `/ia/totalizacao/clima` | Qual total e média para cada condição de clima? |

Todas as respostas são JSON. Cada agrupamento apresenta contagem de observações, soma, média, mediana e máximo em minutos. O script `backend/analise.py` valida campos, datas, números, consistência de atrasos, ausentes e duplicatas antes de calcular.

## Modelo da base e contagem sem duplicidade

Cada linha do CSV representa uma observação acadêmica de atraso em um trecho, em determinada data e contexto. Não representa necessariamente uma viagem completa, um ônibus ou uma pessoa. O identificador composto para reconhecer uma linha de ônibus é `cidade + codigo_linha`; o código isolado pode se repetir entre cidades ou observações. Como não há `id_viagem` nem identificador único da observação, não é correto chamar a contagem de viagens distintas. As rotas somam minutos observados e não estimam atraso de passageiros. A base é sintética, como descreve `data/ORIGEM_DADOS.txt`; não representa telemetria real.

## CORS e comunicação

A tela e a API usam a mesma origem local (`127.0.0.1:8000`), então a abertura padrão não depende de um segundo servidor nem de CORS no navegador. O middleware CORS permanece configurável para desenvolvimento com frontend separado. O segredo do Supabase não é entregue ao navegador.

## Roteiro manual de conferência e evidências

Confira a [verificação atualizada](docs/VERIFICACAO_LOCAL.md) e o [relatório das 37 verificações com Supabase real](docs/EVIDENCIAS_FK_20261106.json).

Use apenas nomes fictícios de cidades e confirme os registros no Table Editor do Supabase. No Swagger (`/docs`):

1. `GET /cidades` — confirma conexão e lista inicial.
2. `POST /cidades` com `{"nome":"Cidade de Teste DS"}` — esperado `201` e `id_cidade` gerado.
3. `GET /cidades/{ID}` e depois `GET /cidades` — esperado `200` e registro na lista.
4. `PUT /cidades/{ID}` com `{"nome":"Cidade de Teste DS Atualizada"}` — esperado `200`; consulte novamente.
5. `DELETE /cidades/{ID}` — esperado `204`; `GET /cidades/{ID}` depois retorna `404`. Se estiver referenciada por uma linha, espere `409` e não apague a FK.
6. `POST /cidades` com nome vazio ou `id_cidade` extra — esperado `422`; nenhum cadastro indevido deve ser gravado.
7. Repita o ciclo CRUD para `linha_onibus`: `POST /linhas` com `id_cidade`, `codigo` e `nome`; consulte, edite com `PUT`, exclua e confirme que uma cidade inexistente retorna `400` ao criar linha.
8. Abra as cinco rotas `/ia` e confira o JSON com os valores apresentados na interface.
9. Salve capturas do Swagger e do Table Editor antes/depois. Os espaços reservados desta pasta não afirmam que testes remotos foram executados; preencha seu relatório com capturas obtidas no seu projeto.

### Testes locais reproduzíveis

Os testes automatizados usam uma tabelas em memória para o CRUD, sem alterar o Supabase. Com as dependências instaladas, execute na raiz: `backend\.venv\Scripts\python.exe -m unittest discover -s tests -v`. Eles verificam o fluxo CRUD, as validações, as quatro totalizações sobre o CSV e o preflight CORS. Isso não substitui os testes no Swagger/Supabase do roteiro acima.

## Apresentação em equipe

- **HTML:** estrutura, campos, navegação, acessibilidade e tabelas.
- **CSS:** cores, tipografia, responsividade e leitura em celular/computador.
- **JavaScript:** chamadas `fetch`, validações visuais, CRUD de cidades e linhas, consulta da API de dados e exibição das totalizações.
- **API/CORS:** FastAPI, Pydantic, rotas, variáveis privadas, comunicação HTTPS com Supabase e origens autorizadas.
- **Ciência de Dados:** significado de cada linha, chave usada para distinguir linhas, limitações da fonte e interpretação das quatro perguntas.

A distribuição depende do tamanho do grupo. Com duas pessoas, combinar HTML/CSS e JavaScript/CORS. Com três, dividir HTML, CSS e JavaScript/CORS. Todos devem acompanhar o teste integrado e explicar a própria parte.

## Repositório da equipe

Repositório identificado no material local: [github.com/josehenriquefelix-sketch/TRANSURBAN](https://github.com/josehenriquefelix-sketch/TRANSURBAN). O pacote está pronto localmente. O link de entrega do GitHub será a branch publicada para revisão; confira também as instruções de integração da pasta no repositório.








