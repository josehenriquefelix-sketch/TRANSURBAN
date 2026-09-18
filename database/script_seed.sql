-- =========================================================
-- TRANSURBAN
-- Script Seed - Massa de teste acadêmica
-- PostgreSQL / Supabase
-- =========================================================

-- CIDADES
INSERT INTO cidade (id_cidade, nome) VALUES
(1, 'Maringá'),
(2, 'Sarandi');

-- LINHA DE ÔNIBUS
INSERT INTO linha_onibus
(id_linha, id_cidade, codigo, nome)
VALUES
(1, 1, '001', 'Linha 001 - Maringá');

-- TRECHO
INSERT INTO trecho
(id_trecho, id_cidade_origem, id_cidade_destino, nome, distancia_km)
VALUES
(1, 1, 2, 'Maringá → Sarandi', 12.00);

-- RELAÇÃO ENTRE LINHA E TRECHO
INSERT INTO linha_trecho
(id_linha, id_trecho, ordem)
VALUES
(1, 1, 1);

-- REGISTROS DE ATRASO
-- Dados exclusivamente acadêmicos para validação do projeto.
INSERT INTO registro_atraso
(id_atraso, id_linha, id_trecho, data_registro, minutos_atraso, observacao)
VALUES
(2, 1, 1, '2026-09-15', 8,  'DADO DE TESTE - Atraso de 8 minutos'),
(3, 1, 1, '2026-09-16', 22, 'DADO DE TESTE - Atraso de 22 minutos'),
(4, 1, 1, '2026-09-17', 12, 'DADO DE TESTE - Atraso de 12 minutos'),
(1, 1, 1, '2026-09-18', 15, 'Atraso de teste no trecho Maringá → Sarandi'),
(5, 1, 1, '2026-09-18', 5,  'DADO DE TESTE - Atraso de 5 minutos');

-- A tabela faixa_exclusiva permanece sem registros no seed.
-- Ela é utilizada separadamente nos testes CRUD.