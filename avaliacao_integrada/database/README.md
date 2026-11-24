# Banco de dados essencial

**Se estiver usando o Supabase da equipe em outro computador, não execute as migrações.** O banco já está atualizado. Basta colocar o `.env` privado e iniciar a API.

São 12 tabelas ativas em `public`. Os arquivos anteriores e exercícios estão em `../historico/database/`; não são instruções de instalação da versão atual.

Em um Supabase novo e vazio, a ordem é:

1. `00_banco_novo_12_tabelas.sql`: tabelas, PK, FK, RLS e funções de acesso/posição.
2. `10_reduzir_para_12.sql`: históricos incorporados, contas, respostas e fila privada de notificações. Também migra a instalação anterior de 28 tabelas.
3. `12_catalogo_com_fontes.sql`: cadastros documentados. Faz cópias privadas antes de retirar cadastros fora do catálogo.

`11_testar_fila_sem_enviar.sql` é um teste com `ROLLBACK`, não uma migração. Exige pelo menos uma conta existente e SMTP parado. Não envia mensagens. A execução real no projeto da equipe passou em 24/11/2026.

O script 10 foi aplicado ao banco existente e conferido. O script 12 preservou os cadastros anteriores e atualizou o catálogo. Um projeto Supabase completamente novo, configurações OAuth e políticas de e-mail não foram recriados nesta rodada; a instalação na escola usa o banco existente.

Não execute SQL de origem desconhecida, não desative RLS e não cole credenciais nos scripts. As funções que modificam dados são restritas a `service_role`; o backend confere o usuário e o papel antes de chamá-las.

O histórico anterior foi mantido em `transurban_arquivo_20261124`, sem acesso dos papéis da API. Não o exponha nas configurações de esquemas do Supabase. Sua remoção definitiva não faz parte desta entrega.
