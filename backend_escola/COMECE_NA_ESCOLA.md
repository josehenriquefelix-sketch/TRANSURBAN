# Continuar a API no Linux da escola

Este pacote mantém a API Python enviada pelo usuário. O site V2 em Node.js e a apresentação são projetos separados; não são iniciados por este script.

1. Extraia este ZIP em uma pasta nova, sem substituir `TRANSURBAN/BACKEND` nem apagar seu banco antigo.
2. No VS Code, abra a pasta `TRANSURBAN_BACKEND` extraída, onde estão `main.py` e `iniciar-linux.sh`.
3. Clique em Terminal → Novo Terminal e execute:

```bash
bash iniciar-linux.sh
```

O iniciador cria `.venv-escola`, instala as dependências e prepara SQLite local somente se não houver configuração de banco. Ele não sobrescreve `.env`, não altera os arquivos Python e não importa nem remove dados do backend antigo.

Se o servidor antigo estiver rodando na porta 8000, encerre-o com Ctrl+C no terminal dele. Após aparecer `Application startup complete`, mantenha o novo terminal aberto e abra `http://127.0.0.1:8000/docs` no navegador do mesmo computador.

Para conferir a API sem tocar no banco configurado:

```bash
bash iniciar-linux.sh --testar
```

O teste fornecido no pacote usa SQLite temporário e confere POST/GET de cidades e linhas, nome relacionado, persistência, FK, 404 e 422.

## Supabase

A conexão remota não foi testada nesta preparação. Se houver configuração privada existente, ela será preservada. O código original executa `create_all` na inicialização: pode criar tabelas ausentes em PostgreSQL; não migra tabelas existentes. Antes de usar uma conexão remota, confira o esquema e use banco autorizado para testes. Não envie `.env`, senha ou URI privada ao chat ou ao GitHub.

## Limites

Este pacote não instala o site V2, não inclui o dashboard de IA do pacote anterior e não comprova que o computador da escola já foi configurado. Para continuar no código que está nesse computador, envie o conteúdo atual de `main.py`, `models.py` e `schemas.py` quando necessário; não envie `.env`.
