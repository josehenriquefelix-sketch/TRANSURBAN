-- =========================================================
-- TRANSURBAN
-- Testes CRUD - Sprint 4
-- PostgreSQL
-- =========================================================

-- CREATE
INSERT INTO faixa_exclusiva
(id_trecho, tipo, status)
VALUES
(1, 'EXCLUSIVA', 'ATIVA');

-- READ
SELECT *
FROM faixa_exclusiva
WHERE id_faixa = 1;

-- UPDATE
UPDATE faixa_exclusiva
SET status = 'INATIVA'
WHERE id_faixa = 1;

-- Verificação do UPDATE
SELECT *
FROM faixa_exclusiva
WHERE id_faixa = 1;

-- DELETE
DELETE FROM faixa_exclusiva
WHERE id_faixa = 1;

-- Verificação do DELETE
SELECT *
FROM faixa_exclusiva
WHERE id_faixa = 1;
