-- TRANSURBAN Sprint 7: aplicar apenas em banco isolado, após revisão.
BEGIN;

CREATE TABLE cidade (
	id_cidade SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id_cidade), 
	UNIQUE (nome)
)

;

CREATE TABLE linha_onibus (
	id_linha SERIAL NOT NULL, 
	id_cidade INTEGER NOT NULL, 
	codigo VARCHAR(20) NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id_linha), 
	UNIQUE (id_cidade, codigo), 
	FOREIGN KEY(id_cidade) REFERENCES cidade (id_cidade)
)

;

CREATE TABLE trecho (
	id_trecho SERIAL NOT NULL, 
	id_cidade_origem INTEGER NOT NULL, 
	id_cidade_destino INTEGER NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	distancia_km FLOAT NOT NULL, 
	PRIMARY KEY (id_trecho), 
	CHECK (distancia_km > 0), 
	FOREIGN KEY(id_cidade_origem) REFERENCES cidade (id_cidade), 
	FOREIGN KEY(id_cidade_destino) REFERENCES cidade (id_cidade)
)

;

CREATE TABLE faixa_exclusiva (
	id_faixa SERIAL NOT NULL, 
	id_trecho INTEGER NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	km FLOAT NOT NULL, 
	PRIMARY KEY (id_faixa), 
	CHECK (km > 0), 
	FOREIGN KEY(id_trecho) REFERENCES trecho (id_trecho)
)

;

CREATE TABLE linha_trecho (
	id_linha INTEGER NOT NULL, 
	id_trecho INTEGER NOT NULL, 
	ordem INTEGER NOT NULL, 
	PRIMARY KEY (id_linha, id_trecho), 
	UNIQUE (id_linha, ordem), 
	CHECK (ordem > 0), 
	FOREIGN KEY(id_linha) REFERENCES linha_onibus (id_linha), 
	FOREIGN KEY(id_trecho) REFERENCES trecho (id_trecho)
)

;

CREATE TABLE registro_atraso (
	id_atraso SERIAL NOT NULL, 
	id_linha INTEGER NOT NULL, 
	id_trecho INTEGER NOT NULL, 
	data_registro DATE NOT NULL, 
	minutos_atraso FLOAT NOT NULL, 
	observacao VARCHAR(600) NOT NULL, 
	PRIMARY KEY (id_atraso), 
	CHECK (minutos_atraso >= 0), 
	FOREIGN KEY(id_linha) REFERENCES linha_onibus (id_linha), 
	FOREIGN KEY(id_trecho) REFERENCES trecho (id_trecho)
)

;
COMMIT;
