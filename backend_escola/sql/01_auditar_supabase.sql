-- SOMENTE LEITURA. Execute primeiro no SQL Editor do projeto correto.
-- Não contém credenciais e não cria nem altera tabelas ou registros.

SELECT c.table_name, c.column_name, c.data_type,
       c.character_maximum_length, c.is_nullable, c.column_default,
       c.is_identity, c.identity_generation
FROM information_schema.columns AS c
WHERE c.table_schema = 'public'
  AND c.table_name IN ('cidade', 'linha_onibus')
ORDER BY c.table_name, c.ordinal_position;

SELECT n.nspname AS schema_name, t.relname AS table_name,
       c.conname AS constraint_name, c.contype AS constraint_type,
       pg_get_constraintdef(c.oid) AS definition
FROM pg_constraint AS c
JOIN pg_class AS t ON t.oid = c.conrelid
JOIN pg_namespace AS n ON n.oid = t.relnamespace
WHERE n.nspname = 'public'
  AND t.relname IN ('cidade', 'linha_onibus')
ORDER BY t.relname, c.contype, c.conname;

SELECT n.nspname AS schema_name, c.relname AS table_name,
       c.relrowsecurity AS rls_enabled, c.relforcerowsecurity AS rls_forced
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p')
  AND c.relname IN ('cidade', 'linha_onibus');

SELECT schemaname, tablename, policyname, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public' AND tablename IN ('cidade', 'linha_onibus')
ORDER BY tablename, policyname;

SELECT table_name, grantee, privilege_type
FROM information_schema.table_privileges
WHERE table_schema = 'public' AND table_name IN ('cidade', 'linha_onibus')
ORDER BY table_name, grantee, privilege_type;
