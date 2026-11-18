# TRANSURBAN — projeto local para a escola

**Site e API executados no VS Code, sem dependência do Render.** O banco da equipe continua no Supabase.

## Abrir no computador da informática

1. No VS Code: **Ctrl+Shift+P → Git: Clone**.
2. Cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`, escolha uma pasta e abra a cópia.
3. Abra `TRANSURBAN.code-workspace` da raiz como workspace.
4. Pressione **Ctrl+Shift+B**. Na primeira vez, o iniciador prepara o ambiente e solicita a configuração privada em `avaliacao_integrada/backend/.env`.
5. Use os comandos da pasta `avaliacao_integrada/ACESSOS`: `ABRIR_PASSAGEIRO.cmd`, `ABRIR_MOTORISTA.cmd` e `ABRIR_GESTAO.cmd`.

Os atalhos iniciam ou reutilizam o servidor local. Mantenha a janela da API aberta. O `.env`, as senhas, as chaves e a `.venv` não vão para o GitHub.

| Portal | Link no computador que está rodando o projeto |
|---|---|
| Passageiro | http://127.0.0.1:8000/ |
| Motorista | http://127.0.0.1:8000/motorista/ |
| Gestão | http://127.0.0.1:8000/gestao/ |

Se o projeto já está clonado, use **Git Pull** e reinicie o servidor para carregar o backend novo. Preserve as configurações privadas e as alterações locais da equipe.

## O que foi acrescentado nesta etapa

- Materiais da manutenção com unidade/oficina, itens de chave composta, total, estoque e limite transacionais.
- Dashboard do CSV com gráficos Chart.js, tabela e consultas por dia.
- Chat que calcula pelo CSV e mantém o resultado quando o Ollama não está configurado.
- Fila privada de avisos de solicitação e decisão de acesso de motorista e gestão.
- Visualização administrativa da estrutura real do banco.
- Tarefas e ambiente Python configurados para o VS Code.

SMTP e chave/modelo Ollama ainda não foram fornecidos. Esses campos estão preparados, sem segredos fictícios funcionando. A equipe pode testar os cálculos sem IA; o Gmail só será validado após configurar o envio.

Veja o [README completo](avaliacao_integrada/README.md), a [explicação das etapas](avaliacao_integrada/docs/ETAPAS_ESCOLA_E_EXPLICACAO.md), a [estrutura do banco](avaliacao_integrada/docs/ESQUEMA_BANCO_ATUAL.json) e a [validação real de materiais](avaliacao_integrada/docs/VALIDACAO_MATERIAIS_ESCOLA.json).

A área de gestão exige conta autorizada e não aparece na navegação do passageiro. A documentação de DS fica em `/docs`; a de Ciência de Dados e chat em `/dados/docs`.
