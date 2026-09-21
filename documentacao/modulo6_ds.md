# Módulo 6 DS — Do banco de dados às primeiras rotas

## Tabela elegível escolhida

A tabela escolhida para esta etapa é `cidade`.

Estrutura no DER/DDL:

| Campo | Tipo | Regra |
|---|---|---|
| id_cidade | INTEGER | PK |
| nome | VARCHAR(100) | NOT NULL, UNIQUE |

### Por que ela atende ao critério?

- possui **chave primária simples**: `id_cidade`;
- não possui chave estrangeira;
- não possui chave primária composta.

As demais tabelas do modelo atual possuem FKs ou chave composta, por isso não são a melhor escolha para as primeiras rotas desta etapa.

## Tecnologias

Fluxo utilizado:

```text
Postman
   ↓
FastAPI
   ↓
SQLAlchemy
   ↓
Psycopg
   ↓
PostgreSQL / Supabase
```

- FastAPI declara as rotas.
- Uvicorn executa a API localmente.
- SQLAlchemy representa e consulta a tabela.
- Psycopg realiza a comunicação com PostgreSQL.
- Supabase hospeda o PostgreSQL da equipe.

## Estrutura do backend

```text
backend/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── analise.py
├── requirements.txt
├── .env.example
└── routes/
    ├── __init__.py
    └── cidades.py
```

## GET

Rota:

```http
GET /cidades/
```

Finalidade: consultar as cidades existentes no Supabase.

Resposta esperada com a massa já validada:

```json
[
  {"id_cidade": 1, "nome": "Maringá"},
  {"id_cidade": 2, "nome": "Sarandi"}
]
```

## POST

Rota:

```http
POST /cidades/
Content-Type: application/json
```

Exemplo acadêmico:

```json
{
  "id_cidade": 99,
  "nome": "Cidade Teste Módulo 6"
}
```

O DDL atual usa `INTEGER PRIMARY KEY` e não usa `IDENTITY` ou `SERIAL`. Por isso, nesta versão do TransUrban o `id_cidade` precisa ser enviado no cadastro.

Resposta de sucesso esperada: **HTTP 201 Created**.

## Como provar a persistência

1. execute um GET e registre o resultado inicial;
2. execute o POST;
3. confirme o status 201;
4. execute novamente o GET;
5. confirme que a cidade cadastrada aparece na lista;
6. confira o mesmo registro no Supabase.

## Como executar no Windows PowerShell

Na raiz do projeto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item backend\.env.example backend\.env
```

Edite `backend/.env` e coloque a string real de conexão do Supabase.

Depois:

```powershell
cd backend
uvicorn main:app --reload
```

API: `http://127.0.0.1:8000`

Documentação automática: `http://127.0.0.1:8000/docs`

## Testes do Postman

Importar:

`backend/TransUrban_Modulo6.postman_collection.json`

A coleção possui:

1. API raiz;
2. health;
3. GET antes do cadastro;
4. POST da cidade de teste;
5. GET depois do cadastro.

## Segurança

A senha do Supabase não está no GitHub. O arquivo real `.env` permanece ignorado pelo Git. Apenas `.env.example` é versionado.

## Resultado da etapa

O código necessário para GET e POST está implementado no repositório. A comprovação de execução exige a credencial local do Supabase e deve ser registrada com prints reais do Postman e/ou Supabase; não é correto fabricar essas evidências.
