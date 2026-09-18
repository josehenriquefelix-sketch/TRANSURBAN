# Dicionário de Dados — TRANSURBAN

## 1. Objetivo

O banco de dados do TRANSURBAN tem como objetivo organizar informações relacionadas ao transporte coletivo entre Maringá e Sarandi, permitindo registrar cidades, linhas de ônibus, trechos, faixas exclusivas ou preferenciais e ocorrências de atrasos.

O banco serve como base para organizar e relacionar os dados necessários ao projeto, principalmente para apoiar a análise de atrasos no transporte coletivo.

---

## 2. Tabela: cidade

Representa as cidades cadastradas no sistema.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_cidade | INTEGER | Sim | PK | Identificador único da cidade |
| nome | VARCHAR(100) | Sim | UNIQUE | Nome da cidade |

### Regras

- Cada cidade possui um identificador único.
- O nome da cidade é obrigatório.
- Não podem existir duas cidades com o mesmo nome.

---

## 3. Tabela: linha_onibus

Representa as linhas de transporte coletivo cadastradas no sistema.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_linha | INTEGER | Sim | PK | Identificador único da linha |
| id_cidade | INTEGER | Sim | FK | Cidade à qual a linha está associada |
| codigo | VARCHAR(20) | Sim | UNIQUE junto com id_cidade | Código da linha |
| nome | VARCHAR(120) | Sim | - | Nome ou descrição da linha |

### Relacionamentos

- `id_cidade` referencia `cidade.id_cidade`.

### Regras

- Cada linha possui um identificador único.
- A linha deve estar associada a uma cidade existente.
- O código da linha é obrigatório.
- A combinação entre cidade e código da linha não pode se repetir.

---

## 4. Tabela: trecho

Representa um trecho utilizado pelo sistema.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_trecho | INTEGER | Sim | PK | Identificador único do trecho |
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
- As cidades de origem e destino precisam existir.

---

## 5. Tabela: linha_trecho

Relaciona as linhas de ônibus aos trechos utilizados em seus trajetos.

Essa tabela permite que uma linha utilize vários trechos e que um trecho possa ser relacionado a diferentes linhas.

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
- A combinação de linha e trecho forma a chave primária da tabela.

---

## 6. Tabela: faixa_exclusiva

Representa faixas exclusivas ou preferenciais associadas aos trechos.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_faixa | INTEGER | Sim | PK | Identificador único da faixa |
| id_trecho | INTEGER | Sim | FK | Trecho onde a faixa está localizada |
| tipo | VARCHAR(20) | Sim | CHECK | Tipo da faixa |
| status | VARCHAR(20) | Sim | CHECK | Situação da faixa |

### Relacionamentos

- `id_trecho` referencia `trecho.id_trecho`.

### Valores permitidos

**Tipo:**
- `EXCLUSIVA`
- `PREFERENCIAL`

**Status:**
- `ATIVA`
- `INATIVA`
- `PLANEJADA`

### Regras

- A faixa deve estar associada a um trecho existente.
- O tipo deve possuir um dos valores permitidos.
- O status deve possuir um dos valores permitidos.

---

## 7. Tabela: registro_atraso

Registra ocorrências de atraso no transporte coletivo.

| Campo | Tipo | Obrigatório | Chave/Regra | Descrição |
|---|---|---|---|---|
| id_atraso | INTEGER | Sim | PK | Identificador único do registro |
| id_linha | INTEGER | Sim | FK | Linha relacionada ao atraso |
| id_trecho | INTEGER | Sim | FK | Trecho relacionado ao atraso |
| data_registro | DATE | Sim | NOT NULL | Data do registro |
| minutos_atraso | INTEGER | Sim | CHECK >= 0 | Quantidade de minutos de atraso |
| observacao | VARCHAR(255) | Não | - | Informação adicional sobre o registro |

### Relacionamentos

- `id_linha` referencia `linha_onibus.id_linha`.
- `id_trecho` referencia `trecho.id_trecho`.

### Regras

- A linha deve existir.
- O trecho deve existir.
- A data do registro é obrigatória.
- A quantidade de minutos de atraso não pode ser negativa.
- A observação é opcional.

---

## 8. Resumo dos relacionamentos

| Tabela | Relacionamento | Tabela relacionada |
|---|---|---|
| linha_onibus | pertence a uma cidade | cidade |
| trecho | possui cidade de origem | cidade |
| trecho | possui cidade de destino | cidade |
| linha_trecho | relaciona uma linha | linha_onibus |
| linha_trecho | relaciona um trecho | trecho |
| faixa_exclusiva | está associada a | trecho |
| registro_atraso | está associado a | linha_onibus |
| registro_atraso | ocorreu em | trecho |

---

## 9. Regras de integridade

O banco utiliza restrições para manter os dados consistentes:

- `PRIMARY KEY` para identificar registros.
- `FOREIGN KEY` para garantir relacionamentos entre tabelas.
- `NOT NULL` para campos obrigatórios.
- `UNIQUE` para impedir duplicidades específicas.
- `CHECK` para impedir valores inválidos.

Entre as principais regras estão:

- O nome da cidade não pode se repetir.
- A combinação `id_cidade + codigo` de uma linha não pode se repetir.
- A distância de um trecho deve ser maior que zero.
- A origem e o destino de um trecho devem ser diferentes.
- A ordem de um trecho dentro de uma linha deve ser maior que zero.
- A mesma linha não pode possuir duas posições com a mesma ordem.
- Os minutos de atraso não podem ser negativos.
- Os valores de tipo e status de uma faixa são controlados.

---

## 10. Massa de teste

O banco atualmente possui uma massa pequena de dados acadêmicos utilizada para validar a estrutura e os relacionamentos.

A massa validada inclui:

- Maringá e Sarandi cadastradas como cidades.
- Uma linha de teste identificada pelo código `001`.
- Um trecho de Maringá para Sarandi com 12,00 km.
- A associação da linha ao trecho.
- Cinco registros acadêmicos de atraso.

Esses registros servem para comprovar o funcionamento do modelo e não representam monitoramento em tempo real do transporte público.

---

## 11. Observação

Este dicionário representa a estrutura validada do banco de dados do TRANSURBAN utilizada nesta etapa do projeto.

O modelo está voltado ao problema de organização e análise de informações relacionadas a atrasos no transporte coletivo entre Maringá e Sarandi. Alterações futuras no sistema deverão ser acompanhadas pela atualização do DER, do DDL e deste dicionário de dados.