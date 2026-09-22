-- =========================================================
-- TRANSURBAN
-- Testes CRUD - PostgreSQL / Supabase
-- =========================================================
-- Este script usa um ID reservado para teste e remove o registro ao final.
-- Pré-requisito: o trecho 1 deve existir (massa de teste padrão).

-- CREATE
INSERT INTO faixa_exclusiva
(id_faixa, id_trecho, tipo, status)
VALUES
(99, 1, 'EXCLUSIVA', 'ATIVA');

-- READ
SELECT *
FROM faixa_exclusiva
WHERE id_faixa = 99;

-- UPDATE
UPDATE faixa_exclusiva
SET status = 'INATIVA'
WHERE id_faixa = 99;

-- Verificação do UPDATE
SELECT *
FROM faixa_exclusiva
WHERE id_faixa = 99;

-- DELETE
DELETE FROM faixa_exclusiva
WHERE id_faixa = 99;

-- Verificação do DELETE
SELECT *
FROM faixa_exclusiva
WHERE id_faixa = 99;
