-- =========================================================
-- TRANSURBAN
-- Testes de Integridade - PostgreSQL / Supabase
-- =========================================================
-- O bloco abaixo testa as restrições sem deixar dados inválidos no banco.
-- Cada teste captura exatamente o tipo de violação esperado.

DO $$
BEGIN
    -- TESTE 1: CHECK de distância.
    BEGIN
        INSERT INTO trecho
        (id_trecho, id_cidade_origem, id_cidade_destino, nome, distancia_km)
        VALUES
        (9001, 1, 2, 'Teste distância inválida', 0.00);

        RAISE EXCEPTION 'TESTE 1 FALHOU: distância zero foi aceita.';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'TESTE 1 OK: CHECK rejeitou distância inválida.';
    END;

    -- TESTE 2: FOREIGN KEY de cidade de origem.
    BEGIN
        INSERT INTO trecho
        (id_trecho, id_cidade_origem, id_cidade_destino, nome, distancia_km)
        VALUES
        (9002, 9999, 2, 'Teste cidade inexistente', 10.00);

        RAISE EXCEPTION 'TESTE 2 FALHOU: FK inexistente foi aceita.';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE 'TESTE 2 OK: FOREIGN KEY rejeitou cidade inexistente.';
    END;

    -- TESTE 3: NOT NULL do nome da cidade.
    BEGIN
        INSERT INTO cidade (id_cidade, nome)
        VALUES (9003, NULL);

        RAISE EXCEPTION 'TESTE 3 FALHOU: nome NULL foi aceito.';
    EXCEPTION
        WHEN not_null_violation THEN
            RAISE NOTICE 'TESTE 3 OK: NOT NULL rejeitou nome vazio.';
    END;

    -- TESTE 4: UNIQUE do nome da cidade.
    BEGIN
        INSERT INTO cidade (id_cidade, nome)
        VALUES (9004, 'Maringá');

        RAISE EXCEPTION 'TESTE 4 FALHOU: cidade duplicada foi aceita.';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'TESTE 4 OK: UNIQUE rejeitou cidade duplicada.';
    END;
END
$$;
