# Atividade de backend com chave estrangeira: TRANSURBAN

## Como a atividade da mercearia se aplica ao TRANSURBAN

O guia usa `clientes` e `ordem_compras` para ensinar o relacionamento. No projeto autoral TRANSURBAN, o relacionamento correspondente é entre `cidade` e `linha_onibus`, usando os nomes e campos reais do domínio:

| Conceito | Mercearia do guia | TRANSURBAN |
|---|---|---|
| Registro de origem e PK | `clientes.id_cliente` | `cidade.id_cidade` |
| Registro relacionado e PK | `ordem_compras.id_ordem_compra` | `linha_onibus.id_linha` |
| FK no registro relacionado | `ordem_compras.id_cliente` | `linha_onibus.id_cidade` |
| Campo legível consultado pela API | `clientes.nome_cliente` | `cidade.nome` |

Uma cidade pode ter várias linhas de ônibus. Cada linha pertence a uma cidade. O banco guarda `id_cidade` na tabela `linha_onibus`; a API consulta `cidade.nome` pelo relacionamento para apresentar a cidade junto da linha. A tabela não duplica o nome da cidade.

No Supabase do projeto, `cidade` e `linha_onibus` já existem. Não execute os scripts de criação em tabelas existentes e não crie tabelas da mercearia no schema TRANSURBAN. O script [03_criar_linha_banco_novo.sql](../database/03_criar_linha_banco_novo.sql) serve somente para um banco de demonstração vazio, depois de revisar a estrutura e criar `cidade`.

## Rotas e JSON

Primeiro consulte `GET /cidades` e confirme o nome e o `id_cidade` da cidade escolhida. Depois cadastre uma linha em `POST /linhas` enviando somente os campos de entrada:

```json
{
  "id_cidade": 1,
  "codigo": "001",
  "nome": "Terminal - Universidade"
}
```

Use um `id_cidade` retornado pela sua própria API. A resposta contém o ID gerado para a linha, o `id_cidade` gravado e `cidade` com o nome consultado na tabela relacionada:

```json
{
  "id_linha": 12,
  "id_cidade": 1,
  "codigo": "001",
  "nome": "Terminal - Universidade",
  "cidade": "Maringá"
}
```

O modelo rejeita campos extras; não envie `cidade` no POST ou PUT. A API verifica se a cidade existe antes de cadastrar ou alterar a linha. Código de cidade inválido retorna `400`. A chave estrangeira no banco protege o vínculo mesmo se os dados mudarem entre a validação e a gravação.

## CRUD e regra de exclusão

- `POST /linhas`: cadastra uma linha associada a uma cidade existente; retorna `201`.
- `GET /linhas`: lista as linhas com o nome de cidade consultado pelo relacionamento.
- `GET /linhas/{id_linha}`: consulta uma linha; retorna `404` se não existir.
- `PUT /linhas/{id_linha}`: altera os dados e permite escolher outra cidade existente.
- `DELETE /linhas/{id_linha}`: exclui somente a linha; retorna `204`.
- `DELETE /cidades/{id_cidade}`: se houver linhas relacionadas, o banco bloqueia e a API responde `409` com uma mensagem clara. Apague ou reassocie as linhas antes de excluir a cidade.

O DDL de demonstração declara `ON DELETE RESTRICT` explicitamente. No projeto Supabase já existente, a FK auditada impede a exclusão de cidade referenciada; não recrie nem altere a constraint durante a apresentação.

## Conferência no Swagger

Abra `http://127.0.0.1:8000/docs` e siga esta sequência com dados fictícios:

1. `GET /cidades`; anote um ID e confira o nome correspondente.
2. `GET /cidades/{id_cidade}`; valide o cadastro selecionado.
3. `POST /linhas` com o ID válido; confirme `201` e que a resposta mostra `cidade` com o nome correto.
4. Faça outro POST com o mesmo `id_cidade`; confirme que duas linhas podem pertencer à mesma cidade.
5. `GET /linhas` e `GET /linhas/{id_linha}`; confira o vínculo e os dados.
6. Tente `POST /linhas` com ID de cidade inexistente; espere `400` e confirme que nenhuma linha foi inserida.
7. Faça `PUT /linhas/{id_linha}` com os campos válidos; confirme `200` e o nome da nova cidade escolhida.
8. Tente excluir a cidade que ainda possui linha; espere `409` e confirme que a cidade e a linha permanecem.
9. Exclua a linha (`204`) e depois a cidade de teste (`204`). Confirme `404` para as consultas aos IDs excluídos.

Use somente registros temporários de apresentação, sem apagar linhas ou cidades reais. Confirme os registros na tabela `public.linha_onibus` no Supabase; devem existir `id_linha`, `id_cidade`, `codigo` e `nome`. O nome exibido na resposta vem da relação e não é uma coluna copiada para a tabela da linha.

## Preparar o GitHub para o computador do laboratório

No VS Code, pressione `Ctrl + Shift + P`, escolha `Git: Clone` e cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`. Após abrir o repositório, execute `avaliacao_integrada/iniciar_local.cmd` pelo terminal integrado (ou dê dois cliques nele no Explorador). O iniciador configura o ambiente, instala as dependências e abre o site e a API.

Na primeira execução, configure a cópia local `avaliacao_integrada/backend/.env` com a URL e a chave secreta do mesmo projeto Supabase. O `.env` não é enviado ao GitHub. Mantenha o `.env.example`, sem valores reais, no repositório. O guia [GUIA_RAPIDO_AUDITORIO.md](../GUIA_RAPIDO_AUDITORIO.md) detalha a clonagem e a inicialização.

