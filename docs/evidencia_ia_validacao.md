# Evidência de Validação da IA — TransUrban

## Ambiente

- Modelo: llama3.2
- Ollama: 0.34.2
- Framework do backend: Flask
- Fonte dos dados: data/atrasos_analise.csv
- Natureza dos dados: massa de teste sintética para validação acadêmica
- Rastreamento em tempo real: não disponível

## Teste 1 — Maior atraso

Pergunta:
Qual foi o maior atraso registrado?

Resposta obtida:
O maior atraso registrado foi de 12 minutos.

Resultado:
APROVADO

## Teste 2 — Atraso médio

Pergunta:
Qual é o atraso médio da massa de teste?

Resposta obtida:
O atraso médio da massa de teste é de 7.57 minutos.

Resultado:
APROVADO

Valor validado na análise:
7.57 minutos.

## Teste 3 — Quantidade de registros

Pergunta:
Quantos registros existem na massa de teste?

Resposta obtida:
Existem 180 registros na massa de teste.

Resultado:
APROVADO

## Teste 4 — Controle de informação inexistente

Pergunta:
Qual é o nome do motorista da linha 007?

Resposta obtida:
A informação sobre o nome do motorista da linha 007 não está fornecida no contexto.

Resultado:
APROVADO

## Conclusão

Os testes demonstraram que o chatbot TransUrban consegue utilizar o contexto fornecido pela massa de dados e responder perguntas relacionadas aos dados disponíveis.

Também foi realizado um teste com uma informação que não existe na base. Nesse caso, o assistente não inventou uma resposta e informou que o dado não estava disponível.

Essa validação demonstra o fluxo:

Usuário → Frontend → Flask → Ollama → Contexto do TransUrban → Resposta

