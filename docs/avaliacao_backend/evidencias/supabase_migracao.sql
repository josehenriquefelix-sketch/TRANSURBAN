-- Aplicado em 20/10/2026 pelo SQL Editor após auditoria. Não é preparação de banco novo.
BEGIN;
SET LOCAL lock_timeout = '3s';
ALTER TABLE public.linha_onibus ALTER COLUMN nome TYPE varchar(120);
COMMIT;
