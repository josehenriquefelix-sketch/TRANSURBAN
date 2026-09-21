# TRANSURBAN

## Projeto Integrador - Módulo 6 DS + IA

O **TransUrban** é um projeto acadêmico voltado à organização e análise de dados relacionados a atrasos no transporte coletivo entre **Maringá e Sarandi**.

Nesta etapa, Desenvolvimento de Sistemas e Inteligência Artificial avançam de forma complementar:

- **DS:** banco PostgreSQL/Supabase -> FastAPI -> GET/POST -> Postman -> wireframes.
- **IA:** CSV -> Pandas -> estatística -> agregação -> classificação -> interpretação -> visualização.

> Os dados utilizados são sintéticos e acadêmicos. O projeto não possui rastreamento em tempo real nesta etapa.

---

## 1. Desenvolvimento de Sistemas

### Tabela escolhida para as primeiras rotas

A tabela `cidade` foi escolhida porque possui:

- chave primária simples: `id_cidade`;
- nenhuma chave estrangeira;
- nenhuma chave composta.

Isso atende ao critério do Módulo 6 para as primeiras rotas.

### Tecnologias

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Psycopg
- PostgreSQL
- Supabase
- Postman

### Backend

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

### Rotas trabalhadas

| Método | Rota | Finalidade |
|---|---|---|
| GET | `/` | Informações básicas da API |
| GET | `/health` | Verificar conexão com PostgreSQL/Supabase |
| GET | `/cidades/` | Consultar cidades |
| POST | `/cidades/` | Cadastrar cidade |

O POST recebe `id_cidade` porque o DDL atual utiliza `INTEGER PRIMARY KEY` sem `IDENTITY` ou `SERIAL`.

### Executar a API

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item backend\.env.example backend\.env
```

Edite `backend/.env` e informe a conexão real do Supabase.

Depois:

```powershell
cd backend
uvicorn main:app --reload
```

API: `http://127.0.0.1:8000`

Swagger: `http://127.0.0.1:8000/docs`

### Postman

Importe:

`backend/TransUrban_Modulo6.postman_collection.json`

Fluxo de validação:

1. GET `/cidades/`;
2. POST `/cidades/`;
3. confirmar HTTP 201;
4. repetir GET;
5. conferir persistência no Supabase.

A senha do Supabase não é versionada. O arquivo real `.env` está no `.gitignore`.

---

## 2. Inteligência Artificial

Fonte principal:

`database/dados.csv`

O arquivo é uma cópia sincronizada de `data/atrasos_analise.csv` e possui **180 registros acadêmicos**.

### Código

A camada analítica reutilizável está em:

`backend/analise.py`

Ela possui funções para:

- carregar o CSV;
- calcular estatísticas;
- realizar agregações com `groupby`;
- classificar atrasos por regras;
- gerar visualização.

### Executar a análise

Na raiz:

```powershell
python backend/main.py
```

A execução demonstra:

- primeiras linhas;
- colunas;
- quantidade de registros;
- estatísticas de `minutos_atraso`;
- atraso médio por condição de trânsito;
- classificação;
- geração de gráfico.

### Resultados principais

Para `minutos_atraso`:

| Medida | Resultado |
|---|---:|
| Média | 7,57 min |
| Mediana | 8 min |
| Moda | 8 min |
| Mínimo | 2 min |
| Máximo | 12 min |
| Amplitude | 10 min |
| Desvio padrão | 2,60 min |

Atraso médio por condição de trânsito:

- Leve: **4,22 min**
- Moderado: **7,11 min**
- Muito intenso: **9,09 min**
- Intenso: **9,84 min**

Classificação acadêmica:

- Baixo (até 5): **43**
- Moderado (6 a 10): **111**
- Alto (11 a 15): **26**
- Muito alto (>15): **0**

A interpretação completa está em:

`documentacao/analise_dados.md`

---

## 3. Banco de dados

Banco: **PostgreSQL / Supabase**

Tabelas do modelo:

- `cidade`
- `linha_onibus`
- `trecho`
- `linha_trecho`
- `faixa_exclusiva`
- `registro_atraso`

Arquivos:

- `database/script_ddl.sql`
- `database/script_seed.sql`
- `database/script_dql.sql`
- `database/testes_crud.sql`
- `database/testes_integridade.sql`
- `docs/DER.md`
- `docs/dicionario_dados.md`

---

## 4. Interfaces / Wireframes

A documentação dos wireframes da tabela `cidade` está em:

`documentacao/wireframes_cidade.md`

Há também um mockup HTML em:

`frontend/modulo6_cidade_wireframe.html`

O cadastro representa o POST e a consulta representa o GET.

---

## 5. Estrutura principal

```text
TRANSURBAN/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── analise.py
│   ├── routes/
│   └── legacy_flask/
├── database/
│   ├── dados.csv
│   ├── script_ddl.sql
│   ├── script_seed.sql
│   └── script_dql.sql
├── data/
├── documentacao/
│   ├── modulo6_ds.md
│   ├── analise_dados.md
│   └── wireframes_cidade.md
├── docs/
├── frontend/
├── ia/
├── requirements.txt
└── README.md
```

---

## 6. Observação sobre o protótipo anterior

O protótipo Flask/Ollama desenvolvido anteriormente foi preservado em:

`backend/legacy_flask/`

Ele não é a implementação principal do Módulo 6 de DS. A implementação atual segue o padrão **FastAPI + Uvicorn + SQLAlchemy + Psycopg** solicitado para esta etapa.

---

## 7. Evidências reais

O código e a documentação estão preparados. Para a comprovação final em sala, ainda é necessário usar a credencial privada do Supabase no arquivo local `backend/.env` e registrar evidências reais:

- GET no Postman;
- POST com HTTP 201;
- GET após o POST;
- registro persistido no Supabase.

Essas evidências não devem ser inventadas ou simuladas.

---

## 8. Repositório

`https://github.com/josehenriquefelix-sketch/TRANSURBAN`
