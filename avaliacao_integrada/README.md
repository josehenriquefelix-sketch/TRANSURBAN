# TRANSURBAN — Recuperação DS e integração DS + IA

Entrega acadêmica integrada com FastAPI, pandas, Supabase por HTTPS, HTML, CSS e JavaScript. A documentação cobre o CRUD, a base de Ciência de Dados, as quatro perguntas, o CORS e o roteiro de conferência.

**Projeto da equipe:** sistema acadêmico sobre transporte coletivo de Maringá e Sarandi. **Autor da recuperação:** Erinaldo Sanches Nascimento. **Grupo:** preencher os nomes dos integrantes antes da apresentação.

## Conteúdo

- `backend/`: FastAPI, modelos Pydantic, CRUD de cidade e linha por Supabase Data API HTTPS, leitura/validação do CSV, quatro totalizações e configuração de CORS.
- `database/`: consulta de auditoria e DDLs para uma instância vazia. O backend não cria nem modifica tabelas automaticamente.
- `data/atrasos_analise.csv`: base de demonstração e `ORIGEM_DADOS.txt` com a procedência e os limites.
- `frontend/`: painel web adaptável, CRUD de cidades e linhas, e visualização das totalizações da API.
- `docs/`: explicação sobre linha da base e perguntas, resultados conferidos, verificação local e roteiro de apresentação.

## Escopo do CRUD

Em auditoria somente de leitura do projeto Supabase `transurban`, em 28/10/2026, foram encontradas as tabelas públicas `cidade`, `faixa_exclusiva`, `linha_onibus`, `linha_trecho`, `registro_atraso` e `trecho`. As PKs observadas são `cidade.id_cidade`, `faixa_exclusiva.id_faixa`, `linha_onibus.id_linha` e a PK composta de `linha_trecho` (`id_linha`, `id_trecho`). As FKs observadas incluem `faixa_exclusiva.id_trecho`, `linha_onibus.id_cidade`, `linha_trecho.id_linha`/`id_trecho` e `registro_atraso.id_linha`/`id_trecho`. `trecho` e `registro_atraso` não apresentaram PK nessa auditoria. Assim, **`cidade` é a única tabela observada com PK e sem FK**, e é a única incluída no CRUD da recuperação. `linha_onibus` fica disponível na avaliação integrada e preserva sua FK para cidade. O banco não foi alterado durante a auditoria.

## Requisitos

- Python 3.10 ou superior.
- Projeto Supabase da equipe com Data API habilitada, esquema `public` exposto e tabela `public.cidade` compatível.
- A chave secreta do Supabase deve ficar apenas em `backend/.env`; nunca no HTML/JavaScript ou no GitHub.
- Git não deve receber `.env`, `.venv` ou senhas. O `.env.example` contém apenas valores fictícios.

## Início rápido no Windows

Dê duplo clique em `iniciar_local.cmd`. Se necessário, ele cria `backend/.env`; se a chave estiver vazia ou fictícia, abre o arquivo para você colar a chave secreta do projeto. A URL pública do projeto já está preenchida apenas no arquivo local. Depois, instala as dependências, inicia a API e o frontend em duas janelas e abre `http://127.0.0.1:5500/`. Mantenha as janelas abertas durante a apresentação. Sem a chave secreta, o painel e a análise do CSV podem abrir, mas o CRUD no Supabase não funcionará.
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

Em outro terminal, ainda na raiz, sirva a interface:

```powershell
python -m http.server 5500 --directory frontend
```

Abra `http://127.0.0.1:5500` para a interface e `http://127.0.0.1:8000/docs` para o Swagger. Mantenha a API em `127.0.0.1`; esta versão acadêmica não tem autenticação e não deve ser publicada para acesso público.

No Linux/macOS, crie o ambiente com `python3 -m venv backend/.venv`, instale `backend/requirements.txt`, copie o `.env.example` para `.env` dentro de `backend`, e inicie `uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000` na raiz. O frontend pode ser servido com `python3 -m http.server 5500 --directory frontend`.

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

O frontend chama `http://127.0.0.1:8000`; o middleware do FastAPI permite somente as origens configuradas em `CORS_ORIGINS` (`127.0.0.1:5500` e `localhost:5500`, por padrão), os métodos usados e o cabeçalho JSON. O segredo do Supabase não é entregue ao navegador. Para outra porta/origem local, ajuste `CORS_ORIGINS` em `backend/.env` e reinicie a API.

## Roteiro manual de conferência e evidências

Use apenas nomes fictícios de cidades e confirme os registros no Table Editor do Supabase. No Swagger (`/docs`):

1. `GET /cidades` — confirma conexão e lista inicial.
2. `POST /cidades` com `{"nome":"Cidade de Teste DS"}` — esperado `201` e `id_cidade` gerado.
3. `GET /cidades/{ID}` e depois `GET /cidades` — esperado `200` e registro na lista.
4. `PUT /cidades/{ID}` com `{"nome":"Cidade de Teste DS Atualizada"}` — esperado `200`; consulte novamente.
5. `DELETE /cidades/{ID}` — esperado `204`; `GET /cidades/{ID}` depois retorna `404`. Se estiver referenciada por uma linha, espere `409` e não apague a FK.
6. `POST /cidades` com nome vazio ou `id_cidade` extra — esperado `422`; nenhum cadastro indevido deve ser gravado.
7. Repita o ciclo CRUD para `linha_onibus`: `POST /linhas` com `id_cidade`, `codigo` e `nome`; consulte, edite com `PUT`, exclua e confirme que uma cidade inexistente retorna `404` ao criar linha.
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









