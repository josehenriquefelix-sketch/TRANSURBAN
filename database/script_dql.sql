-- =========================================================
-- TRANSURBAN
-- Script DQL - Consultas de validação do banco
-- PostgreSQL / Supabase
-- =========================================================

-- Pergunta 1:
-- Quais atrasos foram registrados, do maior para o menor?
SELECT
    r.data_registro,
    l.codigo AS codigo_linha,
    l.nome AS linha,
    t.nome AS trecho,
    r.minutos_atraso,
    r.observacao
FROM registro_atraso r
JOIN linha_onibus l
    ON r.id_linha = l.id_linha
JOIN trecho t
    ON r.id_trecho = t.id_trecho
ORDER BY r.minutos_atraso DESC;


-- Pergunta 2:
-- Qual foi o maior atraso registrado na massa de teste do banco?
SELECT
    MAX(minutos_atraso) AS maior_atraso_minutos
FROM registro_atraso;


-- Pergunta 3:
-- Qual é o atraso médio registrado por linha?
SELECT
    l.codigo AS codigo_linha,
    l.nome AS linha,
    ROUND(AVG(r.minutos_atraso), 2) AS atraso_medio_minutos
FROM registro_atraso r
JOIN linha_onibus l
    ON r.id_linha = l.id_linha
GROUP BY l.id_linha, l.codigo, l.nome
ORDER BY atraso_medio_minutos DESC;


-- Pergunta 4:
-- Quantos registros de atraso existem para cada linha?
SELECT
    l.codigo AS codigo_linha,
    l.nome AS linha,
    COUNT(r.id_atraso) AS quantidade_registros
FROM linha_onibus l
LEFT JOIN registro_atraso r
    ON l.id_linha = r.id_linha
GROUP BY l.id_linha, l.codigo, l.nome
ORDER BY quantidade_registros DESC;


-- Pergunta 5:
-- Quais cidades, linhas e trechos estão relacionados no sistema?
SELECT
    c.nome AS cidade,
    l.codigo AS codigo_linha,
    l.nome AS linha,
    t.nome AS trecho,
    lt.ordem
FROM linha_trecho lt
JOIN linha_onibus l
    ON lt.id_linha = l.id_linha
JOIN cidade c
    ON l.id_cidade = c.id_cidade
JOIN trecho t
    ON lt.id_trecho = t.id_trecho
ORDER BY l.codigo, lt.ordem;


-- Pergunta 6:
-- Quais registros possuem atraso igual ou superior a 10 minutos?
SELECT
    r.data_registro,
    l.codigo AS codigo_linha,
    l.nome AS linha,
    r.minutos_atraso
FROM registro_atraso r
JOIN linha_onibus l
    ON r.id_linha = l.id_linha
WHERE r.minutos_atraso >= 10
ORDER BY r.minutos_atraso DESC;