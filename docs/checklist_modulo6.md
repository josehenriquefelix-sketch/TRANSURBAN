# TRANSURBAN — Checklist do Módulo 6

## Objetivo
Evoluir o projeto a partir do banco já estruturado para demonstrar backend em Python, conexão PostgreSQL/Supabase, rotas GET/POST, testes de API e interface integrada.

## Banco antes do backend
- [x] DER em `docs/DER.md`
- [x] Dicionário em `docs/dicionario_dados.md`
- [x] DDL em `database/script_ddl.sql`
- [x] Seed em `database/script_seed.sql`
- [x] Consultas DQL em `database/script_dql.sql`
- [x] Seis tabelas documentadas
- [x] Massa acadêmica do Supabase documentada
- [x] Diferença entre massa do Supabase e massa de IA explicada

## Backend DS
Arquivos:
- `backend/app.py`
- `backend/database.py`
- `backend/requirements.txt`
- `backend/.env.example`

Rotas:
| Método | Rota | Finalidade |
|---|---|---|
| GET | `/api/health` | Verificar backend e conexão |
| GET | `/api/cidades` | Listar cidades |
| GET | `/api/linhas` | Listar linhas |
| GET | `/api/trechos` | Listar trechos |
| GET | `/api/atrasos` | Listar atrasos |
| GET | `/api/atrasos/resumo` | Quantidade, média, maior e menor |
| POST | `/api/atrasos` | Registrar atraso |
| POST | `/api/chat` | Consultar chatbot CSV/Ollama |

## Configuração segura
A senha do banco não deve ir para o GitHub.

1. Copiar `backend/.env.example` para `backend/.env`.
2. Informar a `DATABASE_URL` do PostgreSQL/Supabase.
3. O `.gitignore` impede o envio do arquivo `.env`.

## Execução no Windows / PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python backend\app.py
```

Abrir:
```text
http://127.0.0.1:5000
```

## Testes no Postman
Importar:
`backend/TransUrban_Modulo6.postman_collection.json`

Ordem recomendada:
1. GET `/api/health`
2. GET `/api/cidades`
3. GET `/api/linhas`
4. GET `/api/trechos`
5. GET `/api/atrasos`
6. GET `/api/atrasos/resumo`
7. POST `/api/atrasos`
8. repetir GET `/api/atrasos`

Exemplo de POST:
```json
{
  "id_linha": 1,
  "id_trecho": 1,
  "data_registro": "2026-09-21",
  "minutos_atraso": 9,
  "observacao": "DADO DE TESTE - Módulo 6"
}
```

## Interface
A interface foi alinhada ao escopo Maringá ↔ Sarandi e agora demonstra:
- dados do banco via GET;
- formulário de inserção via POST;
- chatbot com CSV/Ollama;
- aviso claro de que não há rastreamento em tempo real.

## Evidências para apresentação
- Supabase com as tabelas;
- GET no Postman retornando 200;
- POST retornando 201;
- novo registro aparecendo depois do POST;
- painel exibindo dados do Supabase;
- chatbot respondendo pergunta verificável no CSV;
- GitHub atualizado.

## Limitação correta
O TransUrban ainda não usa dados oficiais em tempo real. Prioridade semafórica e recálculo de rota são evoluções futuras e não devem ser apresentados como funcionalidades prontas.
