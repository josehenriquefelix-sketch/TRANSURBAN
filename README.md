# TRANSURBAN

## Sistema de apoio ao transporte coletivo de Maringá e Sarandi

O **TRANSURBAN** é um projeto acadêmico desenvolvido pelas equipes de Desenvolvimento de Sistemas e Inteligência Artificial.

O projeto busca organizar e analisar informações relacionadas ao transporte coletivo entre **Maringá e Sarandi**, com foco principalmente nos registros de atrasos e nos trechos utilizados pelas linhas de ônibus.

---

## 1. Problema

O trânsito entre Maringá e Sarandi pode contribuir para atrasos no transporte coletivo, prejudicando o deslocamento dos passageiros.

Para estudar esse problema, é necessário organizar informações como:

- cidades;
- linhas de ônibus;
- trechos;
- registros de atraso;
- faixas exclusivas ou preferenciais;
- dados utilizados para análise.

---

## 2. Proposta

O TRANSURBAN propõe uma aplicação capaz de organizar dados relacionados ao transporte coletivo e permitir consultas sobre atrasos.

Nesta etapa do projeto, foram desenvolvidos:

- banco de dados relacional no Supabase;
- modelo DER;
- dicionário de dados;
- scripts SQL;
- massa de teste;
- análise de dados com Python;
- backend utilizando Flask;
- chatbot utilizando Ollama;
- interface web para interação com o chatbot;
- documentação e evidências de validação.

---

## 3. Banco de Dados

O banco utiliza **PostgreSQL** e está hospedado no **Supabase**.

O modelo validado possui seis tabelas:

- `cidade`
- `linha_onibus`
- `trecho`
- `linha_trecho`
- `faixa_exclusiva`
- `registro_atraso`

Os relacionamentos utilizam chaves primárias e estrangeiras para manter os dados conectados.

Também são utilizadas regras como:

- `PRIMARY KEY`
- `FOREIGN KEY`
- `NOT NULL`
- `UNIQUE`
- `CHECK`

O arquivo principal que representa a estrutura atual validada é:

`database/script_ddl.sql`

A massa pequena utilizada para reproduzir os dados acadêmicos do banco está em:

`database/script_seed.sql`

---

## 4. Inteligência Artificial

A parte de Inteligência Artificial utiliza uma massa sintética de teste localizada em:

`data/atrasos_analise.csv`

Essa massa possui **180 registros** e é utilizada para análises e validação do chatbot.

Durante a análise foram verificados:

- quantidade de registros;
- valores nulos;
- registros duplicados;
- atrasos negativos;
- atraso médio;
- maior atraso;
- comportamento dos dados em diferentes categorias.

Na massa de análise da IA, o atraso médio validado é de **7,57 minutos** e o maior atraso é de **12 minutos**.

As linhas que atingiram o maior atraso de 12 minutos foram:

- 007 — Interbairros Zona Norte
- 024 — Parque Itaipu
- 034 — Jardim São Silvestre
- 051 — Parque das Grevíleas

---

## 5. Chatbot

O TRANSURBAN possui uma interface web conectada a um backend desenvolvido com **Flask**.

O backend utiliza o **Ollama** com o modelo `llama3.2` para permitir a interação com o chatbot.

Fluxo simplificado:

```text
Usuário
   ↓
Frontend
   ↓
Flask
   ↓
Contexto do TransUrban
   ↓
Ollama
   ↓
Resposta
```

O chatbot foi testado com perguntas relacionadas à massa de dados.

Também foi realizado um teste solicitando uma informação que não existia no contexto, como o nome do motorista de uma linha. Nesse caso, o sistema informou que a informação não estava disponível, em vez de apresentar um nome inexistente.

---

## 6. Dados Acadêmicos

Os dados utilizados atualmente são **dados sintéticos de teste acadêmico**.

O projeto não possui rastreamento em tempo real dos ônibus nesta etapa.

Existem duas massas de teste diferentes:

**Supabase:** massa pequena utilizada para validar tabelas, relacionamentos e regras do banco.

**IA:** massa localizada em `data/atrasos_analise.csv`, utilizada para análise de dados e validação do chatbot.

Por isso, alguns resultados são diferentes entre as duas massas.

Na massa do Supabase, o maior atraso registrado é de **22 minutos**.

Na massa utilizada pela IA, o maior atraso é de **12 minutos**.

Essa diferença não representa erro, pois são conjuntos de dados acadêmicos diferentes e utilizados para finalidades diferentes.

---

## 7. Tecnologias Utilizadas

- Python
- Flask
- PostgreSQL
- Supabase
- SQL
- Ollama
- modelo `llama3.2`
- HTML
- CSS
- JavaScript
- Git
- GitHub
- Visual Studio Code
- Pandas
- Matplotlib

---

## 8. Estrutura Principal

```text
TRANSURBAN/
│
├── backend/
│   └── app.py
│
├── database/
│   ├── script_ddl.sql
│   ├── script_seed.sql
│   ├── testes_crud.sql
│   ├── testes_integridade.sql
│   └── ...
│
├── data/
│   └── atrasos_analise.csv
│
├── docs/
│   ├── DER.md
│   ├── dicionario_dados.md
│   ├── auditoria.md
│   ├── relatorio_validacao.md
│   └── evidencia_ia_validacao.md
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── ia/
│   ├── analise_transurban.py
│   ├── requirements.txt
│   └── resultados/
│
└── README.md
```

---

## 9. Como Executar o Chatbot

### Requisitos

É necessário possuir:

- Python;
- dependências Python do projeto;
- Ollama;
- modelo `llama3.2`.

Com o Ollama instalado, o modelo utilizado pelo projeto pode ser verificado com:

```powershell
ollama list
```

Na pasta principal do projeto, o backend pode ser iniciado com:

```powershell
python backend\app.py
```

Com o servidor em execução, a aplicação pode ser acessada localmente em:

```text
http://127.0.0.1:5000
```

---

## 10. Validação

A validação do projeto foi documentada na pasta `docs`.

### Banco de dados

Consultar:

`docs/relatorio_validacao.md`

### DER

Consultar:

`docs/DER.md`

### Dicionário de Dados

Consultar:

`docs/dicionario_dados.md`

### Auditoria

Consultar:

`docs/auditoria.md`

### Evidência da IA

Consultar:

`docs/evidencia_ia_validacao.md`

---

## 11. Limitações Atuais

Nesta etapa, o TRANSURBAN é um projeto acadêmico em desenvolvimento.

O sistema ainda não utiliza dados oficiais em tempo real de ônibus ou trânsito.

As análises e respostas apresentadas na demonstração são baseadas nas massas sintéticas utilizadas para validação acadêmica.

Funcionalidades futuras devem ser implementadas e comprovadas antes de serem apresentadas como funcionalidades disponíveis.

---

## 12. Conclusão

O TRANSURBAN integra conhecimentos de **Desenvolvimento de Sistemas** e **Inteligência Artificial** em uma solução acadêmica relacionada ao problema de atrasos no transporte coletivo entre Maringá e Sarandi.

O projeto possui banco de dados relacional, documentação do modelo, scripts SQL, massa de análise, processamento de dados, backend Flask, interface web e integração com Ollama.

A estrutura atual permite demonstrar o funcionamento do banco, seus relacionamentos, a análise da massa acadêmica e a interação do usuário com o chatbot.