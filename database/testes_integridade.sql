-- =========================================================
-- TRANSURBAN
-- Testes de Integridade - Sprint 4
-- PostgreSQL
-- =========================================================

-- TESTE 1: CHECK
-- Distância inválida.
-- Esperado: ERRO - ck_trecho_distancia

INSERT INTO trecho
(id_cidade_origem, id_cidade_destino, nome, distancia_km)
VALUES
(1, 2, 'Teste distância inválida', 0.00);


-- TESTE 2: FOREIGN KEY
-- Cidade de origem inexistente.
-- Esperado: ERRO - fk_trecho_cidade_origem

INSERT INTO trecho
(id_cidade_origem, id_cidade_destino, nome, distancia_km)
VALUES
(9999, 2, 'Teste cidade inexistente', 10.00);


-- TESTE 3: NOT NULL
-- Cidade sem nome.
-- Esperado: ERRO - campo nome não pode ser NULL

INSERT INTO cidade (nome)
VALUES (NULL);


-- TESTE 4: UNIQUE
-- Cidade duplicada.
-- Esperado: ERRO - cidade_nome_key

INSERT INTO cidade (nome)
VALUES ('Maringá');
