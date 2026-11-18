# Cadastro, login e aprovação em execução local

## O que está preparado

- `APP_URL=http://127.0.0.1:8000` e cookies locais sem exigir HTTPS.
- Cadastro, reenvio de confirmação e recuperação apontam explicitamente para o endereço local. A variável da hospedagem anterior é ignorada.
- E-mail ou CPF de uma conta já confirmada pode ser usado no login.
- Cadastro público cria somente passageiro. Motorista e gestor precisam solicitar o vínculo.
- A decisão administrativa é gravada no banco. Não é permitido aprovar o próprio pedido.
- Um trigger grava a notificação de recebimento e de decisão na fila privada `tu_email_acesso`.
- `EMAIL_APROVACOES` define os e-mails dos revisores que também receberão aviso de um pedido novo.
- Com SMTP configurado, o backend tenta entregar a fila enquanto o servidor estiver ativo. Falhas têm tentativas com intervalo; não são marcadas como enviadas.

## Configuração futura do Gmail

O responsável informou que ainda não possui SMTP e pediu para deixar a configuração preparada. Portanto, **o recebimento real no Gmail não foi validado**.

Preencher, somente em `backend/.env`, host, porta 587 ou 465, usuário, senha do aplicativo/provedor e remetente autorizado. Não usar a senha comum da conta Google e não enviar credenciais por chat ou GitHub. Preencher também `EMAIL_APROVACOES` com os destinatários administrativos autorizados.

Para os e-mails de confirmação e recuperação, cadastrar o SMTP no painel Supabase em Authentication → Email/SMTP e manter a confirmação de e-mail ativada. O SMTP padrão do Supabase tem restrições de destinatário e limite; não é uma solução de envio para toda a população.

No Supabase, os redirecionamentos locais `http://127.0.0.1:8000/**` e `http://localhost:8000/**` precisam estar autorizados. O endereço padrão do projeto também deve ser ajustado para local se a equipe abandonar a hospedagem anterior. Esta rodada não confirmou a alteração desse valor no painel; o código usa redirecionamentos locais explícitos.

Em Materiais e ordens → Consultar fila de e-mails, a administração vê se há SMTP configurado e os estados pendente, processando, enviado ou falha. "Enviado" significa aceito pelo servidor SMTP; ainda é necessário conferir a caixa de entrada e o spam. Uma interrupção após o envio pode causar nova tentativa, portanto o recebimento não é prometido como exatamente uma vez.

O link `127.0.0.1` funciona no computador que está executando o projeto. Abrir o mesmo e-mail em outro aparelho aponta para aquele aparelho, não para o computador da escola.

Referências: [SMTP no Supabase](https://supabase.com/docs/guides/auth/auth-smtp), [redirecionamentos](https://supabase.com/docs/guides/auth/redirect-urls).
