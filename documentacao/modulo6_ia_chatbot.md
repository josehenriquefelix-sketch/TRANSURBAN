# Módulo 6 IA — Chatbot web com contexto controlado

## Objetivo

Disponibilizar o agente de IA do TransUrban por uma interface web, mantendo a resposta vinculada à massa acadêmica utilizada no projeto.

## Arquitetura

```text
Navegador
   ↓
frontend/index.html + frontend/script.js
   ↓
Flask — backend/legacy_flask/app.py
   ↓
CSV acadêmico + regras factuais
   ↓
Ollama / llama3.2 quando necessário
```

## Fonte de dados

Arquivo: `data/atrasos_analise.csv`

A massa contém 180 registros sintéticos e acadêmicos. Ela não representa telemetria em tempo real.

## Rota do chatbot

```http
POST /api/chat
Content-Type: application/json
```

Exemplo de corpo:

```json
{
  "message": "Qual é o atraso médio da massa de análise?"
}
```

## Controle de comportamento

O backend:

1. carrega o CSV do projeto;
2. responde diretamente perguntas factuais conhecidas, como quantidade de registros, maior atraso e atraso médio;
3. para perguntas analíticas adicionais, cria um contexto resumido;
4. envia ao Ollama somente esse contexto e a pergunta;
5. usa temperatura 0 e orienta o modelo a não inventar dados;
6. informa no prompt que a fonte é acadêmica.

## Interface web

A interface está em `frontend/` e possui:

- área de conversa;
- sugestões de perguntas;
- campo para digitação;
- aviso de que os dados são acadêmicos;
- painel integrado às rotas do banco quando a conexão Supabase está configurada.

## Como executar

No Windows PowerShell, na raiz do repositório:

```powershell
python -m pip install -r backend/legacy_flask/requirements.txt
ollama run llama3.2
python backend/legacy_flask/app.py
```

Abrir:

`http://127.0.0.1:5000`

## Perguntas de validação

- Qual é o atraso médio da massa de análise?
- Quantos registros existem na massa de análise?
- Qual foi o maior atraso?
- Qual linha teve o maior atraso?

As respostas devem ser conferidas com os resultados do CSV e com os arquivos gerados pela análise Python.

## Separação entre DS e IA

O backend FastAPI em `backend/main.py` é a implementação principal das primeiras rotas de DS.

O Flask/Ollama é utilizado para a interface web do agente de IA e para integrar o chatbot aos dados acadêmicos. As duas partes são complementares.
