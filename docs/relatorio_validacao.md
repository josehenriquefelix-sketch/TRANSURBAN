# TRANSURBAN — Relatório de Validação

## 1. Objetivo

Validar a estrutura, os relacionamentos e as regras de integridade
do banco de dados do sistema TransUrban.

## 2. Banco de dados

**SGBD:** PostgreSQL  
**Ambiente remoto:** Supabase

### Tabelas

- cidade
- linha_onibus
- trecho
- linha_trecho
- faixa_exclusiva
- registro_atraso

## 3. Validação estrutural

Foram verificadas:

- chaves primárias;
- chave primária composta;
- chaves estrangeiras;
- campos NOT NULL;
- restrições UNIQUE;
- restrições CHECK;
- tipos de dados.

O schema.sql foi comparado com a estrutura existente no banco remoto.

## 4. Testes CRUD

Foi realizado um CRUD na tabela `faixa_exclusiva`.

### CREATE

Registro criado com sucesso.

### READ

Registro consultado com sucesso.

### UPDATE

O status foi alterado de `ATIVA` para `INATIVA`.

### DELETE

O registro foi removido com sucesso e a consulta posterior retornou zero linhas.

## 5. Testes negativos

Foram realizados quatro testes de integridade.

### Teste 1 — CHECK

Foi tentada a inserção de um trecho com distância `0.00`.

**Resultado:** registro rejeitado pela restrição `ck_trecho_distancia`.

### Teste 2 — FOREIGN KEY

Foi tentada a inserção de um trecho utilizando a cidade `9999`, que não existe.

**Resultado:** registro rejeitado pela restrição `fk_trecho_cidade_origem`.

### Teste 3 — NOT NULL

Foi tentada a inserção de uma cidade sem informar o nome.

**Resultado:** registro rejeitado pela restrição de campo obrigatório.

### Teste 4 — UNIQUE

Foi tentada a inserção de uma segunda cidade chamada `Maringá`.

**Resultado:** registro rejeitado pela restrição `cidade_nome_key`.

## 6. Homologação

O banco remoto foi homologado por meio de consultas,
testes CRUD e testes negativos.

A consulta de relacionamento confirmou que a linha **101 —
Maringá - Sarandi** está associada ao trecho **Maringá - Sarandi**,
com distância de **13,50 km** e ordem **1**.

## 7. Conclusão

Os testes realizados demonstraram que o banco possui estrutura,
relacionamentos e restrições de integridade funcionando conforme
as regras definidas no projeto.

O banco remoto está disponível para demonstração e os artefatos
da Sprint estão organizados no repositório.
