# Validação na nuvem — 07/10/2026

Os cadernos DS e IA foram comparados com o pacote `avaliacao_backend`.
A implementação existente atende ao recorte Cidade → Linha de ônibus e à análise descritiva do CSV autoral.

## Execuções desta sessão

- Python 3.12.14 e ambiente virtual isolado; `pip check` aprovado.
- 18 testes `unittest` aprovados: 9 de análise e 9 de API/integridade.
- 20 requisições HTTP aprovadas pelo script existente em SQLite descartável.
- 28 verificações HTTP/SQL aprovadas em PostgreSQL 17.11 local, incluindo as APIs de avaliação e Módulo 6.
- Cadastros com HTTP 201, consultas com 200, FK inexistente com 404, duplicidade com 409 na avaliação e com 400 no Módulo 6, entrada inválida com 422.
- Persistência conferida com SQL direto; somente os registros criados nesta validação foram removidos ao final.
- 180 observações de atraso, soma de 1.362 minutos, média de 7,5667 minutos e mediana de 8 minutos.

`http_postgresql.json` contém as respostas novas. `resumo.json`, `linhas.json`, `datas.json` e `qualidade.json` foram obtidos por HTTP nesta sessão.

## Uso no VS Code

Abra `TRANSURBAN.code-workspace` na raiz do repositório. No terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m backend.analise
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

No Windows, selecione `.venv\\Scripts\\python.exe` em Python: Select Interpreter e use os comandos do README. Na nuvem, selecione `/workspace/.venvs/transurban/bin/python`. Pare Uvicorn com Ctrl+C; depois execute `deactivate` se ativou o ambiente.

## Supabase e modelo

PostgreSQL local foi comprovado; Supabase remoto ainda depende da conexão privada da equipe. Configure `.env` conforme `.env.example`, com `PGSSLMODE=require`. Execute primeiro a auditoria de leitura `sql/01_auditar_supabase.sql`. O SQL de criação destina-se apenas a banco de teste novo; não execute migrações no banco existente sem conferir seu esquema.

No recorte de avaliação, Cidade possui PK `id_cidade`; Linha possui PK `id_linha` e FK obrigatória `id_cidade`. A cardinalidade é Cidade (1) → Linha (0..N), e cada linha pertence a uma cidade. O banco guarda a FK e a resposta da API também apresenta o nome da cidade. O DER completo está em `../../docs/DER.md` a partir da pasta de avaliação; não foi produzido nem validado um arquivo nativo brModelo nesta sessão.

## Pendências da entrega externa

- Configurar e testar a conexão real do Supabase, sem publicar `.env`.
- Registrar capturas reais de Swagger/Postman no computador da apresentação.
- Confirmar se a atividade exige o arquivo nativo do brModelo.
- Enviar o pacote e o link do GitHub na atividade correta do Classroom; não houve envio ao Classroom nesta validação.

Os dados são sintéticos. Cada linha do CSV representa uma observação por trecho, não uma viagem completa. A documentação dos indicadores e sua conferência manual estão em `docs/GUIA_APRESENTACAO.md` e `docs/IA_E_DASHBOARD.md` no pacote de avaliação.
