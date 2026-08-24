# Auditoria — Dicionário × DER × SQL

## Projeto

TRANSURBAN — Sistema de apoio ao transporte coletivo de Maringá e Sarandi.

## Objetivo da auditoria

Verificar se o Dicionário de Dados, o DER e o arquivo `schema.sql` representam as mesmas decisões de estrutura do banco de dados.

## Resultado

| Item | Dicionário | DER | SQL | Conclusão |
|---|---|---|---|---|
| cidade | OK | OK | OK | Coerente |
| linha_onibus | OK | OK | OK | Coerente |
| trecho | OK | OK | OK | Coerente |
| linha_trecho | OK | OK | OK | Coerente |
| faixa_exclusiva | OK | OK | OK | Coerente |
| registro_atraso | OK | OK | OK | Coerente |

## Verificações realizadas

Foram comparados:

- nomes das tabelas;
- nomes dos campos;
- tipos de dados;
- chaves primárias;
- chaves estrangeiras;
- campos obrigatórios;
- restrições de integridade;
- relacionamentos entre as entidades.

## Resultado da auditoria

Não foram identificadas inconsistências entre o Dicionário de Dados, o DER e o `schema.sql` nesta versão inicial.

## Observação

O modelo ainda será submetido à execução no PostgreSQL. Caso sejam encontrados problemas durante a execução ou os testes, as alterações deverão ser refletidas no SQL, no Dicionário e no DER.
