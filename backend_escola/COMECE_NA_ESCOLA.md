# Continuar a API no Linux da escola

Este pacote evolui a API Python enviada pelo usuário: a versão 1.1 reúne DS, IA e dashboard em `/painel/`. O site V2 em Node.js e a apresentação são projetos separados; não são iniciados por este script.

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

A conexão remota não foi testada nesta preparação. A versão 1.1 não cria nem migra tabelas PostgreSQL ao iniciar. Use `bash iniciar-linux.sh --supabase` para informar a URI em entrada oculta e auditar o esquema por leitura antes de salvar. Não envie `.env`, senha ou URI privada ao chat ou ao GitHub. Veja `FINALIZAR_ENTREGA.md`.

## Limites

Este pacote não instala o site V2 nem o `frontend-app` do computador. Ele inclui seu próprio dashboard integrado. A atualização preparada na nuvem precisa ser obtida e iniciada no computador da escola. Não envie `.env`.
