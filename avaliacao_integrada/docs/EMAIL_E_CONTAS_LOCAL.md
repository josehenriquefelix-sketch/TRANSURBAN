# Cadastro, login e aprovação em execução local

## O que está preparado

- `APP_URL=http://127.0.0.1:8000` e cookies locais sem exigir HTTPS.
- Cadastro, reenvio de confirmação e recuperação apontam explicitamente para o endereço local. A variável da hospedagem anterior é ignorada.
- E-mail ou CPF de uma conta já confirmada pode ser usado no login.
- Cadastro público cria somente passageiro. Motorista e gestor precisam solicitar o vínculo.
- A decisão administrativa é gravada no banco. Não é permitido aprovar o próprio pedido.
- Um trigger grava as notificações de recebimento e decisão no campo privado `notificacoes` de `tu_pedido_acesso`. A antiga tabela separada foi arquivada na redução para 12 tabelas.
- `EMAIL_APROVACOES` define os e-mails dos revisores que também receberão aviso de um pedido novo.
- Com SMTP configurado, o backend tenta entregar a fila enquanto o servidor estiver ativo. Falhas têm tentativas com intervalo; não são marcadas como enviadas.

## Configuração futura do Gmail

O responsável informou que ainda não possui SMTP e pediu para deixar a configuração preparada. Portanto, **o recebimento real no Gmail não foi validado**.

Preencher, somente em `backend/.env`, host, porta 587 ou 465, usuário, senha do aplicativo/provedor e remetente autorizado. Não usar a senha comum da conta Google e não enviar credenciais por chat ou GitHub. Preencher também `EMAIL_APROVACOES` com os destinatários administrativos autorizados.

Para os e-mails de confirmação e recuperação, cadastrar o SMTP no painel Supabase em Authentication → Email/SMTP e manter a confirmação de e-mail ativada. O SMTP padrão do Supabase tem restrições de destinatário e limite; não é uma solução de envio para toda a população.

No Supabase, os redirecionamentos locais `http://127.0.0.1:8000/**` e `http://localhost:8000/**` precisam estar autorizados. O endereço padrão do projeto também deve ser ajustado para local se a equipe abandonar a hospedagem anterior. Esta rodada não confirmou a alteração desse valor no painel; o código usa redirecionamentos locais explícitos.

A rota administrativa `GET /atendimento/gestao/notificacoes` informa a configuração e a fila de notificações; não há uma área de materiais e ordens no produto atual. "Enviado" significa aceito pelo servidor SMTP; ainda é necessário conferir a caixa de entrada e o spam. Uma interrupção após o envio pode causar nova tentativa, portanto o recebimento não é prometido como exatamente uma vez.

O link `127.0.0.1` funciona no computador que está executando o projeto. Abrir o mesmo e-mail em outro aparelho aponta para aquele aparelho, não para o computador da escola.

Referências: [SMTP no Supabase](https://supabase.com/docs/guides/auth/auth-smtp), [redirecionamentos](https://supabase.com/docs/guides/auth/redirect-urls).

## Passo a passo para pessoas novas — conferido em 25/11/2026

Cada pessoa deve ter sua própria conta e usar seu próprio e-mail. Os papéis ficam no banco; não dependem de criar três contas Gmail compartilhadas. A conta de demonstração é apenas para a equipe testar os painéis. Seus dados privados ficam em `backend/.env`, nos campos `DEMO_EMAIL` e `DEMO_PASSWORD`. Esse endereço de demonstração não possui caixa Gmail para receber recuperação.

### 1. Cadastrar passageiro

1. Com o servidor aberto, acessar `http://127.0.0.1:8000/#cadastro`.
2. Informar nome, e-mail próprio, CPF válido, senha e confirmação da senha. A senha deve ter no mínimo 8 caracteres, maiúscula, minúscula, número e símbolo.
3. Enviar o cadastro uma vez e ler a mensagem. Se pedir confirmação, abrir o e-mail recebido e confirmar antes de entrar.
4. Acessar `http://127.0.0.1:8000/#login` e entrar com e-mail ou CPF e a senha da conta.
5. Se o e-mail não chegar, conferir spam e a configuração SMTP. Não considerar o recebimento garantido enquanto o remetente não estiver configurado e testado.

### 2. Solicitar motorista ou gestão

1. Primeiro criar e confirmar a conta de passageiro, conforme solicitado pelo sistema.
2. Abrir `/motorista/` para motorista ou `/gestao/` para gestão.
3. Abaixo do formulário principal, expandir **Primeiro acesso? Solicitar autorização**.
4. Informar e-mail ou CPF, senha da própria conta e uma justificativa profissional com pelo menos 10 caracteres. Não enviar documentos ou senhas na justificativa.
5. Clicar em **Enviar pedido de autorização** e aguardar a análise. O pedido sozinho não libera o painel.

### 3. Aprovar como responsável

1. Entrar em `/gestao/` com a conta administrativa já autorizada.
2. Abrir **Autorizar profissionais**, disponível somente ao administrador.
3. Conferir nome, e-mail, papel solicitado e justificativa.
4. Selecionar o escopo adequado: Maringá, Sarandi, Metropolitano ou Todos os escopos. Conceder somente o necessário.
5. Escrever a justificativa da decisão, com pelo menos 10 caracteres, e clicar em **Aprovar vínculo** ou **Recusar pedido**.
6. O administrador não pode aprovar o próprio pedido. O sistema registra a decisão e o acesso no banco.
7. A pessoa aprovada volta ao formulário principal do painel correspondente e entra com sua própria conta. Não deve enviar o mesmo pedido toda vez que entrar.

### 4. Conferir e-mails

- Confirmação de conta e recuperação de senha: configuração de remetente no Supabase Auth.
- Avisos de pedidos e decisões: configuração SMTP privada do backend e `EMAIL_APROVACOES` para revisores autorizados.
- Usar a mesma caixa autorizada como remetente é uma opção; isso não cria nem autoriza usuários.
- O SMTP padrão do Supabase possui restrições e não serve como comprovação de envio público irrestrito. Não publicar senhas ou configurar a senha comum do Gmail no repositório.
- Caso o provedor escolhido exija senha de app, o titular deve gerá-la e inseri-la diretamente na configuração privada. Não enviar a credencial pelo chat. A disponibilidade depende das regras da conta.

Fontes técnicas reconsultadas em 25/11/2026: [SMTP do Supabase](https://supabase.com/docs/guides/auth/auth-smtp) e [senhas de app do Google](https://support.google.com/accounts/answer/185833?hl=pt-BR).
