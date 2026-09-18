# TRANSURBAN — Relatório de Validação

## 1. Objetivo

Validar a estrutura, os relacionamentos, as regras de integridade e a massa de teste do banco de dados do sistema TransUrban.

O banco foi desenvolvido para organizar informações relacionadas ao transporte coletivo, com foco no registro e análise de atrasos entre Maringá e Sarandi.

---

## 2. Banco de Dados

**SGBD:** PostgreSQL  
**Ambiente remoto:** Supabase

### Tabelas validadas

- `cidade`
- `linha_onibus`
- `trecho`
- `linha_trecho`
- `faixa_exclusiva`
- `registro_atraso`

A estrutura existente no Supabase foi consultada e utilizada como referência para a atualização do DER, do dicionário de dados e do arquivo `script_ddl.sql`.

---

## 3. Validação Estrutural

Foram verificadas no banco remoto:

- chaves primárias;
- chave primária composta;
- chaves estrangeiras;
- campos obrigatórios (`NOT NULL`);
- restrições `UNIQUE`;
- restrições `CHECK`;
- tipos e tamanhos dos campos.

### Principais regras identificadas

- O nome da cidade não pode se repetir.
- Uma linha deve estar associada a uma cidade existente.
- A combinação entre cidade e código da linha não pode se repetir.
- A distância de um trecho deve ser maior que zero.
- A cidade de origem deve ser diferente da cidade de destino.
- A ordem de um trecho dentro de uma linha deve ser maior que zero.
- Uma mesma linha não pode possuir duas posições com a mesma ordem.
- Os minutos de atraso não podem ser negativos.
- Os tipos permitidos para faixa são `EXCLUSIVA` e `PREFERENCIAL`.
- Os status permitidos são `ATIVA`, `INATIVA` e `PLANEJADA`.

---

## 4. Relacionamentos Validados

As consultas realizadas no Supabase confirmaram os relacionamentos entre as tabelas.

Foram identificadas as seguintes chaves estrangeiras:

- `linha_onibus.id_cidade` → `cidade.id_cidade`
- `trecho.id_cidade_origem` → `cidade.id_cidade`
- `trecho.id_cidade_destino` → `cidade.id_cidade`
- `linha_trecho.id_linha` → `linha_onibus.id_linha`
- `linha_trecho.id_trecho` → `trecho.id_trecho`
- `faixa_exclusiva.id_trecho` → `trecho.id_trecho`
- `registro_atraso.id_linha` → `linha_onibus.id_linha`
- `registro_atraso.id_trecho` → `trecho.id_trecho`

---

## 5. Massa de Teste do Supabase

Durante a validação, o banco possuía:

| Tabela | Quantidade de registros |
|---|---:|
| cidade | 2 |
| linha_onibus | 1 |
| trecho | 1 |
| linha_trecho | 1 |
| registro_atraso | 5 |
| faixa_exclusiva | 0 |

As cidades cadastradas são **Maringá** e **Sarandi**.

A linha acadêmica utilizada na validação possui:

- Código: `001`
- Nome: `Linha 001 - Maringá`
- Cidade associada: `Maringá`

O trecho validado possui:

- Origem: `Maringá`
- Destino: `Sarandi`
- Nome: `Maringá → Sarandi`
- Distância: `12,00 km`
- Ordem na linha: `1`

---

## 6. Registros de Atraso

Foram consultados cinco registros acadêmicos de atraso associados à linha `001` e ao trecho `Maringá → Sarandi`.

| Data | Minutos de atraso |
|---|---:|
| 15/09/2026 | 8 |
| 16/09/2026 | 22 |
| 17/09/2026 | 12 |
| 18/09/2026 | 15 |
| 18/09/2026 | 5 |

Esses registros são utilizados exclusivamente como massa de teste acadêmica.

O maior atraso dessa massa do **Supabase** é de **22 minutos**.

---

## 7. Testes CRUD

O projeto possui o arquivo `database/testes_crud.sql`, preparado para demonstrar as quatro operações básicas na tabela `faixa_exclusiva`:

- `CREATE` — inserção de uma faixa.
- `READ` — consulta do registro.
- `UPDATE` — alteração do status.
- `DELETE` — remoção do registro.

Ao final do fluxo de teste, o registro criado é removido. Por isso, a tabela `faixa_exclusiva` pode permanecer vazia após o teste.

---

## 8. Testes de Integridade

O arquivo `database/testes_integridade.sql` contém testes negativos preparados para verificar regras do banco.

Os testes contemplam:

1. tentativa de inserir trecho com distância igual a zero;
2. tentativa de utilizar uma cidade inexistente;
3. tentativa de cadastrar cidade com nome nulo;
4. tentativa de cadastrar uma cidade duplicada.

Esses testes foram projetados para provocar rejeições quando as restrições do banco estiverem funcionando.

As restrições correspondentes foram confirmadas na estrutura do Supabase durante a validação.

---

## 9. Scripts do Banco

Foram organizados os seguintes artefatos:

- `database/script_ddl.sql` — representa a estrutura relacional validada no Supabase;
- `database/script_seed.sql` — contém a massa acadêmica utilizada para reproduzir os dados básicos validados;
- `database/testes_crud.sql` — contém os testes CRUD;
- `database/testes_integridade.sql` — contém testes das regras de integridade.

Os arquivos antigos foram preservados para não destruir o histórico do projeto.

---

## 10. Banco e Massa de Dados da IA

É importante diferenciar as massas utilizadas no projeto.

O Supabase possui uma massa pequena voltada à validação do banco relacional.

A análise de IA utiliza o arquivo `data/atrasos_analise.csv`, que contém uma massa acadêmica maior utilizada para análise e para o contexto do chatbot.

Por esse motivo, os valores máximos podem ser diferentes:

- Massa de validação do Supabase: maior atraso de `22 minutos`.
- Massa de análise da IA: maior atraso de `12 minutos`.

Isso não representa erro de cálculo. São duas massas acadêmicas diferentes, utilizadas para finalidades diferentes nesta etapa do projeto.

---

## 11. Conclusão

A validação confirmou que o banco remoto possui as seis tabelas previstas no modelo e que os principais relacionamentos e restrições estão configurados.

Também foram confirmados registros acadêmicos relacionados entre cidade, linha, trecho e atraso.

O DER, o dicionário de dados, o `script_ddl.sql` e o `script_seed.sql` foram alinhados à estrutura validada no Supabase.

Os dados utilizados nesta etapa são acadêmicos e não devem ser apresentados como informações em tempo real do transporte público.

## Validação de execução do DDL e Seed

Foi realizada uma validação adicional dos scripts do banco de dados em um schema separado chamado `transurban_teste`, criado no Supabase exclusivamente para o teste.

O objetivo foi verificar se a estrutura atual do banco poderia ser criada e receber a massa de teste sem interferir nas tabelas existentes no schema oficial.

### Resultado do DDL

A estrutura foi criada do zero no ambiente de teste e as seis tabelas previstas pelo modelo foram criadas sem erro:

- `cidade`
- `linha_onibus`
- `trecho`
- `linha_trecho`
- `faixa_exclusiva`
- `registro_atraso`

### Resultado do Seed

Após a criação das tabelas, foi executada a massa correspondente ao `script_seed.sql`.

A conferência apresentou:

| Tabela | Quantidade |
|---|---:|
| cidade | 2 |
| linha_onibus | 1 |
| trecho | 1 |
| linha_trecho | 1 |
| registro_atraso | 5 |
| faixa_exclusiva | 0 |

O resultado confirma que a massa de teste pôde ser inserida respeitando a estrutura do banco.

### Validação dos relacionamentos

Também foi realizada uma consulta relacionando `linha_onibus`, `cidade`, `linha_trecho` e `trecho`.

O resultado obtido foi:

| Código | Linha | Cidade | Trecho | Ordem |
|---|---|---|---|---:|
| 001 | Linha 001 - Maringá | Maringá | Maringá → Sarandi | 1 |

Isso confirmou que o relacionamento entre cidade, linha e trecho está funcionando corretamente.

### Limpeza do ambiente de teste

Depois da validação, o schema `transurban_teste` foi removido com `DROP SCHEMA transurban_teste CASCADE`.

Dessa forma, somente o ambiente criado para o teste foi removido, sem necessidade de alterar as tabelas do schema oficial.

### Conclusão

A validação demonstrou que a estrutura representada pelo DDL e a massa correspondente ao Seed são compatíveis entre si e conseguem reproduzir o banco acadêmico utilizado nesta etapa do TransUrban.
