# Roteiros de apresentação — TRANSURBAN

Apresentação prevista para a manhã de 21/10/2026. Tempo sugerido: 5 a 7 minutos. As falas podem ser divididas entre os integrantes na ordem abaixo.

## Antes de começar

Abra o workspace novo do TRANSURBAN. Na pasta `backend`, ative a `.venv` e inicie a API:

```bat
.venv\Scripts\activate
python -m uvicorn main:app --port 8091
```

Se a API já estiver respondendo nessa porta, use a execução aberta. Acesse http://127.0.0.1:8091/docs e confira `GET /`. A API usa PostgreSQL no Supabase; confirme a conexão com a internet antes da aula. Mantenha `.env` fechado durante a apresentação.

Deixe também abertos `models.py`, `schemas.py`, `main.py` e `database.py`. As fontes estão em `FONTES.md` e as evidências em `evidencias/`.

No ensaio já foram cadastradas Maringá, Sarandi e Paiçandu, além de quatro linhas. Marialva foi conferida como opção real para um novo cadastro e ainda não estava na base durante a revisão. Não é necessário apagar os registros do ensaio.

## Roteiro principal — 5 a 7 minutos

### 1. Apresentar o projeto — 40 segundos

**Mostrar:** `/docs`, com as rotas recolhidas.

**Fala:** “Nosso projeto é o TRANSURBAN. Ele tem como contexto a organização de informações do transporte coletivo, principalmente entre Maringá e Sarandi. Nesta avaliação, implementamos a API de cidades e linhas de ônibus. Seguimos o caderno começando por uma tabela com chave primária e depois adicionando outra tabela relacionada por chave estrangeira.”

### 2. Explicar a estrutura — 50 segundos

**Mostrar:** os quatro arquivos no VS Code, sem abrir `.env`.

**Fala:** “O `database.py` configura a conexão com o PostgreSQL e as sessões. O `models.py` representa as tabelas e seus relacionamentos. O `schemas.py` define os dados que a API recebe e devolve. O `main.py` cria a aplicação FastAPI e as rotas. O Uvicorn executa o servidor, e usamos o Swagger em `/docs` para testar as requisições.”

### 3. Demonstrar Cidade e a PK — 1 minuto

**Mostrar:** `GET /cidades`, depois `POST /cidades`.

Execute o GET primeiro. Se Marialva ainda não estiver cadastrada, envie:

```json
{
  "nome": "Marialva"
}
```

Observe o `id_cidade` retornado e anote esse número. Execute `GET /cidades` para conferir a gravação.

**Fala:** “Cidade é a tabela sem chave estrangeira. No cadastro enviamos apenas o nome. O banco gera o identificador automaticamente, e esse identificador é a chave primária. Depois consultamos a lista para confirmar que o registro ficou salvo.”

Se o cadastro retornar 409 porque o exemplo já foi ensaiado, consulte a cidade existente e use seu ID. Explique que a API bloqueou a repetição conforme a regra de unicidade do projeto.

### 4. Demonstrar Linha de Ônibus e a FK — 1 minuto e 20 segundos

**Mostrar:** `models.py`, depois `POST /linhas` e `GET /linhas`.

No model, aponte a FK `id_cidade` e os dois lados de `relationship`.

Em `POST /linhas`, preencha `nome` com `Maringá - Marialva`, `codigo` com `001.0224-400` e `id_cidade` com o número realmente obtido na etapa anterior. Não use o código IBGE como ID interno da API.

**Fala:** “A linha possui sua própria chave primária e o campo `id_cidade` como chave estrangeira. Esse campo aponta para uma cidade existente. A relação é de uma cidade para várias linhas. No banco guardamos o identificador; na resposta usamos o relacionamento para mostrar o nome da cidade.”

Execute o POST uma vez. A resposta deve trazer `cidade: Marialva`. Execute `GET /linhas` e localize o mesmo registro. Se a linha já existir, o retorno 409 é esperado; mostre-a na consulta.

### 5. Demonstrar a proteção do relacionamento — 50 segundos

**Mostrar:** `POST /linhas` com uma cidade inexistente.

```json
{
  "nome": "Teste de cidade inexistente",
  "codigo": "TESTE-404",
  "id_cidade": 999999
}
```

**Fala:** “Antes de cadastrar a linha, a API procura a cidade informada. Como essa cidade não existe, ela devolve 404 com a mensagem ‘Cidade não encontrada’. O registro não é salvo. Isso evita que uma linha fique apontando para uma cidade inválida.”

Se houver tempo, repita um cadastro existente para mostrar o 409. Um nome ou código vazio, só com espaços ou acima do limite devolve 422.

### 6. Explicar dados, testes e GitHub — 50 segundos

**Mostrar:** `FONTES.md`, `REVISAO_FINAL.md` e o repositório.

**Fala:** “Os nomes das cidades foram conferidos no IBGE. Os códigos e nomes das linhas foram conferidos nos documentos oficiais do DER do Paraná. Eles são dados cadastrais e horários planejados; não estamos apresentando medições de atraso em tempo real. Revisamos os cadastros, as consultas, a persistência e as respostas de erro. Os arquivos do código estão no GitHub, enquanto o `.env` e a `.venv` ficam apenas na máquina.”

### 7. Encerramento — 20 segundos

**Fala:** “Com isso, demonstramos o fluxo completo: a requisição chega à API, os dados são validados, o SQLAlchemy grava no PostgreSQL e a resposta volta em JSON. O principal resultado é cadastrar uma linha ligada a uma cidade válida e consultar o nome dessa cidade pela API.”

Depois da demonstração, se for encerrar a execução iniciada no seu terminal, pressione `Ctrl+C` e execute `deactivate`, conforme o caderno.

## Versão curta — aproximadamente 2 minutos

“Nosso projeto é o TRANSURBAN. Nesta etapa fizemos uma API com FastAPI, SQLAlchemy e PostgreSQL no Supabase para cadastrar e consultar cidades e linhas de ônibus.

Começamos por Cidade. Ela tem uma chave primária gerada pelo banco, então o cadastro recebe apenas o nome. Depois implementamos Linha de Ônibus, que tem sua própria chave primária e uma chave estrangeira apontando para Cidade.

Aqui no `GET /linhas`, podemos ver as linhas cadastradas e o nome da cidade relacionada. O banco guarda o `id_cidade`, e o backend usa o relacionamento para devolver uma informação compreensível, como Paiçandu ou Sarandi.

Também testamos o erro. Ao enviar uma linha com cidade inexistente, a API responde 404 e impede o cadastro. Se tentarmos repetir um registro, ela responde 409. Dados inválidos são rejeitados com 422.

As cidades foram conferidas no IBGE e as linhas em documentos do DER do Paraná. O código está no GitHub, com as credenciais fora do versionamento. Assim, cumprimos o percurso da avaliação: primeiro a tabela simples, depois a tabela com FK e a consulta com o nome relacionado.”

Durante essa versão, mostre `GET /cidades`, `GET /linhas` e o teste 404. Se o professor pedir o cadastro, siga as etapas 3 e 4 do roteiro principal.

## Perguntas que podem aparecer

| Pergunta | Resposta curta |
|---|---|
| O que é uma API? | É a interface que recebe requisições e devolve respostas para outro sistema. Aqui usamos HTTP e JSON. |
| O que é PK? | É a chave primária, que identifica cada registro da tabela. |
| O que é FK? | É a chave estrangeira, que referencia a chave de outra tabela e mantém o vínculo entre elas. |
| Por que guardar o ID e não o nome? | O ID identifica o registro e permite relacioná-lo sem repetir o nome em cada linha. |
| Qual a diferença entre `ForeignKey` e `relationship`? | `ForeignKey` define a ligação no banco. `relationship` permite navegar entre os objetos Python. |
| Por que o GET devolve o nome da cidade? | Porque `linha.cidade.nome` percorre o relacionamento; o schema de resposta permite devolver esse nome. |
| Por que existem schemas de entrada e saída? | O cadastro recebe os campos necessários; a resposta também pode incluir o ID gerado e o nome relacionado. |
| O que fazem `add`, `commit` e `refresh`? | `add` prepara o objeto; `commit` confirma a gravação; `refresh` recupera os valores atualizados do banco. |
| Por que usar `.venv`? | Para isolar as dependências deste projeto. |
| Para que serve `requirements.txt`? | Para registrar as dependências e permitir reinstalá-las em outra máquina. |
| O que acontece quando a cidade não existe? | A API devolve 404 antes da inserção. A FK também protege a ligação no PostgreSQL. |
| O 409 significa que a API quebrou? | Não. É a resposta prevista para um cadastro que viola a unicidade. |
| O que significa 422? | Os dados enviados não atendem ao schema, por exemplo um código vazio ou um texto longo demais. |
| Onde ficam as senhas? | No `.env` local, ignorado pelo Git. Não mostramos esse arquivo na apresentação. |
| Salvar, commit e push são iguais? | Não. Salvar altera o arquivo; commit registra a versão; push envia os commits ao remoto. |
| Qual seria outra entidade com FK? | Trecho: tem `id_trecho` como PK e duas FKs para Cidade, origem e destino. A API poderia devolver os dois nomes. Esse desafio é conceitual e não foi implementado neste recorte. |

## Se algo sair diferente na hora

- **409:** consulte o registro existente. Não altere um código oficial para contornar a duplicidade.
- **422:** confira o JSON, os campos obrigatórios e se `id_cidade` contém o número retornado pela API.
- **404 esperado:** no teste com `999999`, ele comprova a validação do vínculo.
- **Página não abre:** confira se o servidor iniciou e se a URL usa a mesma porta do terminal.
- **Supabase sem conexão:** confira a internet e a configuração local. Use as evidências salvas para explicar o teste anterior, deixando claro que a execução ao vivo não foi concluída naquele momento.

As fontes e as limitações dos dados estão em [FONTES.md](FONTES.md). O estado da base muda quando novos cadastros são realizados; use sempre os IDs realmente retornados.
