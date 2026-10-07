# Site TRANSURBAN

O painel fica em `/painel/` e é servido pelo mesmo processo FastAPI da API. Não precisa de Node, Live Server, CDN, API key no navegador ou configuração de CORS. Os arquivos do site estão em `frontend/`, dentro deste pacote de avaliação. O frontend Flask antigo na raiz do repositório permanece separado.

## Iniciar no Linux

Abra a pasta `avaliacao_backend` do pacote atualizado no VS Code. Não substitua o `.env`, a venv ou o banco da pasta BACKEND antiga sem backup. O comando é diferente daquele da pasta antiga:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Deixe o terminal aberto. No mesmo computador, abra `http://127.0.0.1:8000/painel/`. A documentação da API continua em `/docs`. Se o servidor antigo estiver usando a porta 8000, pare apenas esse servidor com Ctrl+C antes de iniciar o novo.

Sem configuração de banco, o pacote usa SQLite local. Para PostgreSQL/Supabase, use `.env` privado conforme a documentação existente. Cadastros exibem os dados reais do banco configurado; os gráficos analisam o CSV sintético e não são atualizados por esses cadastros.

## Funcionalidades

- Navegação entre visão geral, cidades, linhas e qualidade da fonte.
- Indicadores de contagem, média, mediana e máximo carregados da API.
- Série diária e comparação por trânsito, cidade, período ou clima.
- Tabela analítica por cidade/linha, ordenada por atraso médio.
- POST de cidades e linhas; seleção da cidade a partir dos cadastros existentes.
- Busca por código, linha ou cidade.
- Auditoria do CSV e download do resumo JSON.
- Estados vazios, erros de requisição, confirmação de cadastro e bloqueio de duplo envio.
- Layout responsivo, labels nos formulários, navegação por teclado e foco visível.

## Validação executada

Os 18 testes de backend passaram após integrar o frontend. Em Chromium/Playwright foram executados os carregamentos de indicadores, os cadastros, a duplicidade de cidade, a busca sem resultados, a troca da dimensão do gráfico, o download JSON e a falha simulada da fonte. A falha remove indicadores antigos e desabilita o download do resumo obsoleto. Nenhum erro JavaScript foi observado.

Layout conferido em 1440 × 1080 e 390 × 844. A página móvel não excedeu a largura da viewport; as tabelas têm rolagem própria para preservar as colunas.

Esta validação usa banco local descartável. Não representa publicação em domínio público nem validação do Supabase remoto.
