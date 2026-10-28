-- TRANSURBAN | consultar o esquema atual antes de qualquer alteração.
-- Script de leitura: mostra campos, PKs, FKs e geração automática em public.
SELECT
    c.table_name,
    c.column_name,
    c.data_type,
    c.is_nullable,
    c.column_default,
    c.is_identity,
    tc.constraint_type,
    kcu.constraint_name,
    ccu.table_name AS tabela_referenciada,
    ccu.column_name AS coluna_referenciada
FROM information_schema.columns AS c
LEFT JOIN information_schema.key_column_usage AS kcu
    ON kcu.table_schema = c.table_schema
   AND kcu.table_name = c.table_name
   AND kcu.column_name = c.column_name
LEFT JOIN information_schema.table_constraints AS tc
    ON tc.table_schema = kcu.table_schema
   AND tc.table_name = kcu.table_name
   AND tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.table_schema = tc.table_schema
   AND ccu.constraint_name = tc.constraint_name
WHERE c.table_schema = 'public'
ORDER BY c.table_name, c.ordinal_position;

-- Este DDL é para uma INSTÂNCIA VAZIA de demonstração.
-- Não execute sobre tabelas existentes antes de conferir o resultado acima.
-- No modelo do TRANSURBAN, cidade é a única tabela com PK e sem FK.
-- linha_onibus possui FK para cidade e não entra no CRUD desta recuperação.
