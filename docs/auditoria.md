# Auditoria — Dicionário × DER × DDL × Supabase

## Projeto

TRANSURBAN — Sistema de apoio ao transporte coletivo de Maringá e Sarandi.

## Objetivo da auditoria

Verificar se o Dicionário de Dados, o DER e o arquivo `database/script_ddl.sql` representam de forma coerente a estrutura relacional validada no banco PostgreSQL hospedado no Supabase.

---

## Elementos comparados

A auditoria considerou as seguintes tabelas:

| Tabela | Dicionário | DER | script_ddl.sql | Supabase | Resultado |
|---|---|---|---|---|---|
| cidade | OK | OK | OK | OK | Coerente |
| linha_onibus | OK | OK | OK | OK | Coerente |
| trecho | OK | OK | OK | OK | Coerente |
| linha_trecho | OK | OK | OK | OK | Coerente |
| faixa_exclusiva | OK | OK | OK | OK | Coerente |
| registro_atraso | OK | OK | OK | OK | Coerente |

---

## Verificações realizadas

Foram comparados:

- nomes das tabelas;
- nomes dos campos;
- tipos de dados;
- campos obrigatórios;
- chaves primárias;
- chave primária composta;
- chaves estrangeiras;
- restrições `UNIQUE`;
- restrições `CHECK`;
- relacionamentos entre as entidades.

---

## Relacionamentos verificados

O modelo validado possui os seguintes relacionamentos:

- `linha_onibus.id_cidade` → `cidade.id_cidade`
- `trecho.id_cidade_origem` → `cidade.id_cidade`
- `trecho.id_cidade_destino` → `cidade.id_cidade`
- `linha_trecho.id_linha` → `linha_onibus.id_linha`
- `linha_trecho.id_trecho` → `trecho.id_trecho`
- `faixa_exclusiva.id_trecho` → `trecho.id_trecho`
- `registro_atraso.id_linha` → `linha_onibus.id_linha`
- `registro_atraso.id_trecho` → `trecho.id_trecho`

---

## Principais regras verificadas

Entre as regras de integridade representadas na documentação e no DDL estão:

- o nome da cidade deve ser único;
- uma linha deve estar associada a uma cidade existente;
- a combinação entre cidade e código da linha deve ser única;
- a distância de um trecho deve ser maior que zero;
- origem e destino de um trecho devem ser diferentes;
- a ordem do trecho dentro de uma linha deve ser maior que zero;
- uma mesma linha não pode possuir duas posições com a mesma ordem;
- os minutos de atraso não podem ser negativos;
- o tipo da faixa deve ser `EXCLUSIVA` ou `PREFERENCIAL`;
- o status da faixa deve ser `ATIVA`, `INATIVA` ou `PLANEJADA`.

---

## Resultado da auditoria

Após a revisão, o DER, o Dicionário de Dados e o `database/script_ddl.sql` ficaram alinhados à estrutura relacional validada no Supabase.

A auditoria também permitiu identificar que o arquivo antigo `database/schema.sql` representa uma versão anterior do projeto e não deve ser utilizado como referência principal para a estrutura atual do banco.

O arquivo mantido como referência da estrutura atual é:

`database/script_ddl.sql`

---

## Massa de teste

O arquivo `database/script_seed.sql` representa a massa pequena de dados acadêmicos utilizada na validação do banco.

A estrutura validada contém dados relacionados a:

- Maringá;
- Sarandi;
- linha acadêmica `001`;
- trecho `Maringá → Sarandi`;
- registros acadêmicos de atraso.

Esses dados são utilizados para testes e demonstração e não representam informações em tempo real do transporte público.

---

## Conclusão

A auditoria atualizada demonstra a coerência entre o modelo documentado e a estrutura validada no Supabase.

O DER apresenta as entidades e seus relacionamentos, o Dicionário de Dados explica os campos e regras, e o `script_ddl.sql` representa a implementação relacional correspondente.

O arquivo `schema.sql` foi preservado como parte do histórico do projeto, mas não representa a versão atual validada do banco.