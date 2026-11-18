# Abrir na informática



1. No VS Code: **Ctrl+Shift+P → Git: Clone**.
2. Cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`, escolha uma pasta e abra a cópia.
3. Abra `avaliacao_integrada/TRANSURBAN.code-workspace` como workspace.
4. Pressione **Ctrl+Shift+B**. Na primeira vez, o iniciador prepara o ambiente e solicita a configuração privada em `avaliacao_integrada/backend/.env`.
5. Use os comandos da pasta `avaliacao_integrada/ACESSOS`: `ABRIR_PASSAGEIRO.cmd`, `ABRIR_MOTORISTA.cmd` e `ABRIR_GESTAO.cmd`.

Os atalhos iniciam ou reutilizam o servidor local. Mantenha a janela da API aberta. O `.env`, as senhas, as chaves e a `.venv` não vão para o GitHub.

| Portal | Link no computador que está rodando o projeto |
|---|---|
| Passageiro | http://127.0.0.1:8000/ |
| Motorista | http://127.0.0.1:8000/motorista/ |
| Gestão | http://127.0.0.1:8000/gestao/ |

Se o projeto já está clonado, use **Git Pull** e reinicie o servidor para carregar o backend novo. Preserve as configurações privadas e as alterações locais da equipe.

