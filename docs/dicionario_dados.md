# Dicionário de Dados — TRANSURBAN

## 1. Objetivo

O banco de dados do TRANSURBAN tem como objetivo organizar informações relacionadas ao transporte coletivo entre Maringá e Sarandi, permitindo registrar linhas de ônibus, trechos viários, faixas exclusivas ou preferenciais e ocorrências de atrasos.

O banco será utilizado como base para apoiar a identificação de trechos que podem apresentar problemas de circulação e atrasos no transporte coletivo.

---

# 2. Tabela: cidade

Representa as cidades atendidas pelo sistema.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_cidade | INTEGER | Sim | PK / Identity | Identificador único da cidade |
| nome | VARCHAR(100) | Sim | UNIQUE | Nome da cidade |

### Regras

- Cada cidade possui um identificador único.
- O nome da cidade é obrigatório.
- Não podem existir duas cidades com o mesmo nome.

---

# 3. Tabela: linha_onibus

Representa as linhas de transporte coletivo cadastradas no sistema.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_linha | INTEGER | Sim | PK / Identity | Identificador único da linha |
| codigo | VARCHAR(20) | Sim | UNIQUE | Código da linha |
| nome | VARCHAR(120) | Sim | - | Nome ou descrição da linha |

### Regras

- Cada linha possui um identificador único.
- O código da linha é obrigatório.
- O código não pode se repetir.

---

# 4. Tabela: trecho

Representa um trecho viário utilizado pelo sistema.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_trecho | INTEGER | Sim | PK / Identity | Identificador único do trecho |
| id_cidade_origem | INTEGER | Sim | FK | Cidade de origem do trecho |
| id_cidade_destino | INTEGER | Sim | FK | Cidade de destino do trecho |
| nome | VARCHAR(150) | Sim | - | Nome ou descrição do trecho |
| distancia_km | NUMERIC(6,2) | Sim | CHECK > 0 | Distância do trecho em quilômetros |

### Relacionamentos

- `id_cidade_origem` referencia `cidade.id_cidade`.
- `id_cidade_destino` referencia `cidade.id_cidade`.

### Regras

- A distância deve ser maior que zero.
- A cidade de origem deve ser diferente da cidade de destino.

---

# 5. Tabela: linha_trecho

Relaciona linhas de ônibus aos trechos utilizados em seus trajetos.

Essa tabela resolve o relacionamento muitos-para-muitos entre linhas e trechos.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_linha | INTEGER | Sim | PK composta / FK | Linha de ônibus |
| id_trecho | INTEGER | Sim | PK composta / FK | Trecho utilizado pela linha |
| ordem | INTEGER | Sim | CHECK > 0 / UNIQUE por linha | Ordem do trecho no trajeto |

### Relacionamentos

- `id_linha` referencia `linha_onibus.id_linha`.
- `id_trecho` referencia `trecho.id_trecho`.

### Regras

- Uma linha pode possuir vários trechos.
- Um trecho pode ser utilizado por várias linhas.
- A ordem deve ser maior que zero.
- Uma linha não pode possuir duas posições com a mesma ordem.

---

# 6. Tabela: faixa_exclusiva

Representa faixas destinadas ao transporte coletivo.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_faixa | INTEGER | Sim | PK / Identity | Identificador único da faixa |
| id_trecho | INTEGER | Sim | FK | Trecho onde a faixa está localizada |
| tipo | VARCHAR(20) | Sim | CHECK | Tipo da faixa |
| status | VARCHAR(20) | Sim | CHECK | Situação atual da faixa |

### Relacionamentos

- `id_trecho` referencia `trecho.id_trecho`.

### Valores permitidos

**Tipo:**

- EXCLUSIVA
- PREFERENCIAL

**Status:**

- ATIVA
- INATIVA
- PLANEJADA

---

# 7. Tabela: registro_atraso

Registra ocorrências de atrasos no transporte coletivo.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_atraso | INTEGER | Sim | PK / Identity | Identificador do registro |
| id_linha | INTEGER | Sim | FK | Linha que apresentou o atraso |
| id_trecho | INTEGER | Sim | FK | Trecho onde o atraso foi registrado |
| data_registro | DATE | Sim | - | Data da ocorrência |
| minutos_atraso | INTEGER | Sim | CHECK >= 0 | Quantidade de minutos de atraso |
| observacao | VARCHAR(255) | Não | - | Observação adicional |

### Relacionamentos

- `id_linha` referencia `linha_onibus.id_linha`.
- `id_trecho` referencia `trecho.id_trecho`.

### Regras

- A linha deve existir.
- O trecho deve existir.
- A data do registro é obrigatória.
- A quantidade de minutos não pode ser negativa.

---

# 8. Resumo dos relacionamentos

| Tabela | Relacionamento | Tabela relacionada |
|---|---|---|
| trecho | cidade de origem | cidade |
| trecho | cidade de destino | cidade |
| linha_trecho | pertence a | linha_onibus |
| linha_trecho | utiliza | trecho |
| faixa_exclusiva | localizada em | trecho |
| registro_atraso | pertence a | linha_onibus |
| registro_atraso | ocorreu em | trecho |

---

# 9. Regras de integridade

O banco utiliza as seguintes restrições:

- PRIMARY KEY para identificação única dos registros.
- FOREIGN KEY para manter os relacionamentos.
- NOT NULL para informações obrigatórias.
- UNIQUE para impedir duplicidade em campos específicos.
- CHECK para impedir valores inválidos.

---

# 10. Observação

Este dicionário representa a versão inicial do modelo de dados do TRANSURBAN e deverá ser atualizado caso alterações estruturais sejam realizadas durante as etapas de validação, testes e implantação.
