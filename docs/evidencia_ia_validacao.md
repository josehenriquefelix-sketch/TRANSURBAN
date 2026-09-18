# Evidência de Validação da IA — TransUrban

## 1. Ambiente

- Modelo utilizado: `llama3.2`
- Ollama: `0.34.2`
- Framework do backend: Flask
- Fonte de dados: `data/atrasos_analise.csv`
- Natureza dos dados: massa de teste sintética para validação acadêmica
- Quantidade de registros: 180
- Período da massa: 01/08/2026 a 31/08/2026
- Rastreamento em tempo real: não disponível

Os dados utilizados pelo chatbot nesta etapa são acadêmicos e não representam informações em tempo real do transporte público.

---

## 2. Teste — Maior atraso registrado

**Pergunta:**

Qual foi o maior atraso registrado?

**Resposta validada:**

O maior atraso registrado foi de 12 minutos. Houve empate entre as linhas:

- 007 — Interbairros Zona Norte
- 024 — Parque Itaipu
- 034 — Jardim São Silvestre
- 051 — Parque das Grevíleas

**Resultado:** APROVADO

O valor foi conferido diretamente na massa de análise utilizada pelo projeto.

---

## 3. Teste — Linha com maior atraso

**Pergunta:**

Qual linha teve o maior atraso?

**Resposta validada:**

O chatbot informou que o maior atraso foi de 12 minutos e identificou corretamente o empate entre as linhas 007, 024, 034 e 051.

**Resultado:** APROVADO

Esse teste é importante porque evita apresentar apenas uma linha quando existem várias com o mesmo valor máximo.

---

## 4. Teste — Atraso médio

**Pergunta:**

Qual é o atraso médio da massa de teste?

**Resposta obtida:**

O atraso médio da massa de teste é de 7.57 minutos.

**Valor validado na análise:** 7.57 minutos

**Resultado:** APROVADO

---

## 5. Teste — Quantidade de registros

**Pergunta:**

Quantos registros existem na massa de teste?

**Resposta obtida:**

Existem 180 registros na massa de teste.

**Resultado:** APROVADO

---

## 6. Teste — Controle de informação inexistente

**Pergunta:**

Qual é o nome do motorista da linha 007?

**Resposta obtida:**

O chatbot informou que não existem informações disponíveis sobre o nome do motorista da linha 007 no contexto fornecido.

**Resultado:** APROVADO

Esse teste demonstra que o sistema consegue reconhecer quando uma informação não está presente no contexto, evitando inventar um dado inexistente.

---

## 7. Qualidade da massa de análise

A validação da fonte `data/atrasos_analise.csv` apresentou:

- 180 registros;
- 13 colunas;
- 0 valores nulos;
- 0 registros duplicados;
- 0 atrasos negativos;
- atraso médio de 7.57 minutos;
- maior atraso de 12 minutos.

Essas verificações ajudam a garantir que a massa utilizada na demonstração possui estrutura adequada para os testes acadêmicos realizados.

---

## 8. Fluxo do chatbot

O fluxo utilizado na aplicação é:

Usuário → Frontend → Flask → Contexto do TransUrban → Ollama → Resposta

O frontend envia a pergunta para o backend Flask. O backend utiliza os dados e o contexto permitido pelo projeto para processar a pergunta e gerar a resposta apresentada ao usuário.

---

## 9. Diferença entre a massa da IA e o Supabase

O projeto utiliza duas massas acadêmicas com finalidades diferentes.

A massa `data/atrasos_analise.csv` é utilizada na análise de IA e possui 180 registros. Nela, o maior atraso é de 12 minutos.

O banco Supabase possui uma massa relacional menor, utilizada para validar tabelas, relacionamentos e regras do banco. Nessa massa, o maior atraso registrado é de 22 minutos.

Portanto, a diferença entre 12 e 22 minutos não representa erro: os valores pertencem a massas de teste diferentes.

---

## 10. Conclusão

Os testes realizados demonstram que o chatbot TransUrban consegue responder perguntas relacionadas à massa de dados utilizada na validação.

Também foi verificado que o sistema consegue tratar uma pergunta cuja informação não está disponível no contexto, sem apresentar um nome de motorista inexistente.

A validação comprova a integração entre a interface web, o backend Flask, o contexto de dados do TransUrban e o Ollama.

Os resultados apresentados são referentes a dados sintéticos de teste acadêmico e não devem ser interpretados como informações em tempo real.