-- =========================================================
-- TRANSURBAN
-- Script DDL - Banco de Dados PostgreSQL / Supabase
-- =========================================================

CREATE TABLE cidade (
    id_cidade INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE linha_onibus (
    id_linha INTEGER PRIMARY KEY,
    id_cidade INTEGER NOT NULL,
    codigo VARCHAR(20) NOT NULL,
    nome VARCHAR(120) NOT NULL,

    CONSTRAINT uq_linha_cidade_codigo
        UNIQUE (id_cidade, codigo),

    CONSTRAINT fk_linha_cidade
        FOREIGN KEY (id_cidade)
        REFERENCES cidade(id_cidade)
);

CREATE TABLE trecho (
    id_trecho INTEGER PRIMARY KEY,
    id_cidade_origem INTEGER NOT NULL,
    id_cidade_destino INTEGER NOT NULL,
    nome VARCHAR(150) NOT NULL,
    distancia_km NUMERIC(6,2) NOT NULL,

    CONSTRAINT ck_trecho_distancia
        CHECK (distancia_km > 0),

    CONSTRAINT ck_trecho_cidades_diferentes
        CHECK (id_cidade_origem <> id_cidade_destino),

    CONSTRAINT fk_trecho_cidade_origem
        FOREIGN KEY (id_cidade_origem)
        REFERENCES cidade(id_cidade),

    CONSTRAINT fk_trecho_cidade_destino
        FOREIGN KEY (id_cidade_destino)
        REFERENCES cidade(id_cidade)
);

CREATE TABLE linha_trecho (
    id_linha INTEGER NOT NULL,
    id_trecho INTEGER NOT NULL,
    ordem INTEGER NOT NULL,

    CONSTRAINT linha_trecho_pkey
        PRIMARY KEY (id_linha, id_trecho),

    CONSTRAINT uq_linha_trecho_ordem
        UNIQUE (id_linha, ordem),

    CONSTRAINT ck_linha_trecho_ordem
        CHECK (ordem > 0),

    CONSTRAINT fk_linha_trecho_linha
        FOREIGN KEY (id_linha)
        REFERENCES linha_onibus(id_linha),

    CONSTRAINT fk_linha_trecho_trecho
        FOREIGN KEY (id_trecho)
        REFERENCES trecho(id_trecho)
);

CREATE TABLE faixa_exclusiva (
    id_faixa INTEGER PRIMARY KEY,
    id_trecho INTEGER NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,

    CONSTRAINT ck_faixa_tipo
        CHECK (tipo IN ('EXCLUSIVA', 'PREFERENCIAL')),

    CONSTRAINT ck_faixa_status
        CHECK (status IN ('ATIVA', 'INATIVA', 'PLANEJADA')),

    CONSTRAINT fk_faixa_trecho
        FOREIGN KEY (id_trecho)
        REFERENCES trecho(id_trecho)
);

CREATE TABLE registro_atraso (
    id_atraso INTEGER PRIMARY KEY,
    id_linha INTEGER NOT NULL,
    id_trecho INTEGER NOT NULL,
    data_registro DATE NOT NULL,
    minutos_atraso INTEGER NOT NULL,
    observacao VARCHAR(255),

    CONSTRAINT ck_atraso_minutos
        CHECK (minutos_atraso >= 0),

    CONSTRAINT fk_atraso_linha
        FOREIGN KEY (id_linha)
        REFERENCES linha_onibus(id_linha),

    CONSTRAINT fk_atraso_trecho
        FOREIGN KEY (id_trecho)
        REFERENCES trecho(id_trecho)
);