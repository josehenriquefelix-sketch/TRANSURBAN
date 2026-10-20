# Banco da avaliação de backend

## Banco novo

Use PostgreSQL local ou um projeto de desenvolvimento Supabase autorizado. A entrega não inclui credenciais. A conexão fica somente em backend/.env:

```dotenv
DATABASE_URL=postgresql+psycopg2://USUARIO:SENHA@HOST:5432/BANCO
```

No Supabase, copie os parâmetros corretos do painel de conexão, inclusive host, porta, usuário e SSL quando exigido. Não compartilhe a senha. A API utiliza o driver psycopg2-binary solicitado no caderno.

Execute python init_db.py na pasta backend. O script cria apenas cidade e linha_onibus, com IDs gerados pelo PostgreSQL, nome da cidade único e combinação cidade/código única. Não carrega CSV, massa antiga ou dados fixos. O Supabase do usuário foi posteriormente auditado e recebeu somente a correção de limite descrita no relatório EVIDENCIAS.md; init_db.py não foi executado nele.

## Banco existente

O DDL histórico database/script_ddl.sql usa INTEGER PRIMARY KEY sem geração automática. O caderno pede que o cliente não envie o ID. create_all não migra tabelas existentes; por isso o servidor não executa DDL automaticamente e init_db.py recusa tabelas já presentes.

A solução reproduzível para esta avaliação é usar um banco novo. O DDL histórico foi mantido porque abrange outras entidades e dados. Não execute database/schema.sql: ele descreve outra estrutura, transporte, incompatível com este recorte. Não execute scripts antigos como preparação desta entrega.

Para reutilizar um banco existente, primeiro faça backup, confira DDL e dependências e planeje a migração das duas PKs para identity/sequências com valores acima dos IDs existentes. Essa alteração depende do estado real do banco. A auditoria do Supabase real confirmou que suas duas PKs já são identity, portanto não foi necessário migrá-las. Não renumere IDs: outras tabelas podem referenciá-los.

## Verificação por SQL

Em uma ferramenta conectada ao mesmo banco novo, sem divulgar a conexão:

```sql
SELECT id_cidade, nome FROM cidade ORDER BY id_cidade;

SELECT l.id_linha, l.codigo, l.nome, l.id_cidade, c.nome AS cidade
FROM linha_onibus AS l
JOIN cidade AS c ON c.id_cidade = l.id_cidade
ORDER BY l.id_linha;

SELECT table_name, column_name, column_default, is_identity
FROM information_schema.columns
WHERE table_schema = current_schema()
AND (table_name, column_name) IN (
  ('cidade', 'id_cidade'), ('linha_onibus', 'id_linha')
);
```

No banco novo gerado pelo SQLAlchemy, column_default usa nextval de sequência. Isso gera a PK automaticamente mesmo com is_identity = NO. A FK e as restrições UNIQUE permanecem ativas.

## Problemas corrigidos

| Problema observado | Correção nesta entrega |
|---|---|
| POST de cidade exigia ID informado pelo cliente | Schema recebe somente nome; PK gerada em banco novo |
| API principal tinha apenas cidade | Adicionadas linha_onibus, FK, relationship e rotas |
| Nome da linha em cópia paralela limitado a 100 | Backend principal usa 120, conforme dicionário |
| README instalava requirements inexistente na raiz | Roteiro instala arquivo dentro de backend |
| Documentos e APIs de escopos diferentes competiam como entrada | README atual aponta um backend e um conjunto de roteiros |
| Risco de aparentar validação por evidência antiga | Evidências desta entrega são registradas separadamente |

## Solução de erros de execução

- DATABASE_URL ausente: copie backend/.env.example para backend/.env e configure.
- 503 nas rotas de dados: verifique se PostgreSQL está ativo, rede/SSL, credenciais locais e tabelas no schema configurado. A resposta não expõe a mensagem interna do driver.
- Erro de importação: execute Uvicorn dentro de backend, como orientado.
- init_db.py recusa tabelas existentes: escolha banco novo; não apague nem migre dados por tentativa.
- 409: consulte os registros e escolha dados demonstrativos diferentes.
- Porta 8000 ocupada: use python -m uvicorn main:app --reload --port 8001 e ajuste o endereço de teste.

## Resultado do Supabase inspecionado

O projeto lsnpvokfnvyjkvqzkvof possui as PKs automáticas, a FK e as unicidades esperadas. O limite de linha_onibus.nome foi ajustado de 150 para 120, compatível com o dicionário. As 6 cidades e 4 linhas foram preservadas. Consulte EVIDENCIAS.md para os registros anteriores e posteriores. A API não recebe a senha PostgreSQL através do login no painel web; configure essa conexão localmente para verificar a integração direta.

## Estado final desta máquina

DATABASE_URL foi configurada privadamente pelo usuário e a conexão da API ao Supabase foi confirmada. As consultas HTTP devolveram exatamente os dados obtidos por SELECT no banco. TEST_DATABASE_URL continuou no PostgreSQL local. Não execute init_db.py no Supabase existente.
