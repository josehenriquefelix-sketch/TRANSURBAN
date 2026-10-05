-- SOMENTE LEITURA. Execute no SQL Editor do projeto Supabase correto.
-- Identifica todas as PK/FK existentes no schema public, inclusive compostas.
SELECT n.nspname AS esquema, t.relname AS tabela,
       c.conname AS restricao,
       CASE c.contype WHEN 'p' THEN 'PK' WHEN 'f' THEN 'FK' END AS tipo,
       k.pos AS ordem_na_chave, a.attname AS coluna,
       nr.nspname AS esquema_referenciado, tr.relname AS tabela_referenciada,
       ar.attname AS coluna_referenciada,
       c.convalidated AS validada, pg_get_constraintdef(c.oid) AS definicao
FROM pg_constraint c
JOIN pg_class t ON t.oid = c.conrelid
JOIN pg_namespace n ON n.oid = t.relnamespace
CROSS JOIN LATERAL unnest(c.conkey) WITH ORDINALITY AS k(attnum, pos)
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum
LEFT JOIN pg_class tr ON tr.oid = c.confrelid AND c.contype = 'f'
LEFT JOIN pg_namespace nr ON nr.oid = tr.relnamespace
LEFT JOIN pg_attribute ar ON ar.attrelid = tr.oid AND ar.attnum = c.confkey[k.pos::integer]
WHERE n.nspname = 'public' AND c.contype IN ('p', 'f')
ORDER BY t.relname, tipo, c.conname, k.pos;

-- PK não significa necessariamente ID automático: confira DEFAULT/IDENTITY.
SELECT table_name, column_name, data_type, is_nullable, column_default,
       is_identity, identity_generation
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

-- Tabelas sem PK (não inclui views).
SELECT t.relname AS tabela_sem_pk
FROM pg_class t
JOIN pg_namespace n ON n.oid = t.relnamespace
WHERE n.nspname = 'public' AND t.relkind IN ('r', 'p')
AND NOT EXISTS (SELECT 1 FROM pg_constraint c WHERE c.conrelid = t.oid AND c.contype = 'p')
ORDER BY t.relname;

-- RLS é separado de PK/FK e não deve ser desativado para corrigir cadastro.
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
