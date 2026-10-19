# Validação da API escolar 1.1 — 19/10/2026

- **22 testes automatizados aprovados**, incluindo o teste DS original, indicadores, reconciliação independente com csv/statistics, fonte inválida, arquivos do painel e proteção da configuração privada. Uma advertência de depreciação do TestClient foi emitida; ela não representa falha do teste.
- **16 requisições HTTP verificadas** em Uvicorn e SQLite temporário pelo script `gerar_evidencias.py`. `http.json` contém entradas, status e respostas. Resumo, qualidade, linhas e datas foram obtidos por HTTP, não apresentados como execução no computador da escola.
- Dashboard conferido em Chromium: indicadores, cadastro de cidade/linha, FK inexistente, busca, exportação JSON, troca de dimensão, erro de fonte e viewport móvel. Nenhum erro JavaScript observado. A página não excedeu a largura de 390 px; tabelas possuem rolagem própria.
- Os testes do configurador não usaram credenciais reais. Conferiram rejeição de TLS desativado, preservação de TLS mais forte, backup e permissões do `.env`, rejeição de symlink e ausência de salvamento/exposição de URI em falha de auditoria.
- Foi testado que inicialização em modo remoto não chama criação de tabelas. Não houve conexão real ao projeto Supabase nesta sessão.

Esses resultados são da preparação na nuvem. As evidências enviadas pelo usuário a partir do computador da escola continuam em `../testes-escola-2026-10-19.json`, da API anterior. A atualização precisa ser obtida e iniciada na escola para demonstrar as rotas novas.

O workflow CI foi acrescentado, mas seu resultado remoto não foi confirmado aqui. Arquivos e testes de `site_v2` não são usados como evidência do `frontend-app` local, cujo código não foi fornecido nesta versão.
