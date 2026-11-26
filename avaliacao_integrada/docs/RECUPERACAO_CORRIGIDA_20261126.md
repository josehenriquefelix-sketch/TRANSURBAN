# Recuperação de senha — revisão de 26/11/2026

## O que foi corrigido

- As três entradas oferecem **Esqueci minha senha**. Motorista e gestão informam a área de origem no link.
- A API solicita retorno para `/recuperar-senha?area=...`, sem fragmento no endereço enviado ao provedor. O Supabase acrescenta seu fragmento de autenticação ao retornar.
- A interface dá prioridade à tela de nova senha e trata o formato padrão e o legado `#nova-senha#access_token=...`, em vez de enviá-los para o início.
- O token é removido do endereço e mantido apenas na memória da página, sem localStorage/sessionStorage.
- Depois de salvar, aparece o acesso da área correspondente. Links expirados orientam solicitar outro.
- No Supabase, o Site URL foi corrigido de `http://127.0.0.1:8091` para `http://127.0.0.1:8000`, porta ativa confirmada. A origem local `http://127.0.0.1:8000/**` foi adicionada aos retornos permitidos. A entrada anterior da porta 8091 foi preservada.

## Como usar agora

1. Mantenha o servidor do projeto aberto.
2. Na entrada de passageiro, motorista ou gestão, clique em **Esqueci minha senha**.
3. Informe um e-mail real cadastrado e solicite um **novo** link. Não reutilize o e-mail anterior à correção.
4. Abra o e-mail mais recente. A tela deve mostrar **Crie uma nova senha** e a área de origem.
5. Escolha pessoalmente uma senha diferente da anterior, com 8 a 72 caracteres, maiúscula, minúscula, número e símbolo. Confirme e salve.
6. Use o link para voltar à entrada da sua área.

O endereço da conta de apresentação em `example.com` não é uma caixa de e-mail. Recuperação precisa de um endereço que a pessoa consiga abrir. A senha da Conta Google é gerenciada no próprio Google; a opção do TRANSURBAN trata a senha local da conta no Supabase.

## O que foi verificado

- 62 testes da API aprovados.
- 47 testes de JavaScript aprovados.
- Abertura da tela de nova senha nas três áreas e no formato legado, com token **fictício**, sem submissão de nova senha.
- Modelo de envio padrão do Supabase confirmado no painel. O usuário relatou recebimento; não foi feito acesso ao e-mail pessoal nesta conferência.
- As 12 tabelas ativas responderam HTTP 200 a consultas com limite zero, sem expor registros. Não foi necessária migração nem exclusão de tabelas.
- PDF original do banner conferido: uma página com 90,00 × 120,00 cm.

## Limites

A troca com um link real recebido por e-mail e uma nova senha pessoal deve ser concluída pelo usuário. Não foi alterada senha de nenhuma conta. O envio usa o serviço padrão do Supabase; SMTP próprio continua sendo uma configuração separada para atender usuários fora das limitações desse serviço. Alterar a porta em outro computador exige manter APP_URL e os retornos permitidos compatíveis.

Fontes técnicas consultadas em 26/11/2026: [Supabase — redefinição de senha](https://supabase.com/docs/reference/javascript/auth-resetpasswordforemail), [retornos permitidos](https://supabase.com/docs/guides/auth/redirect-urls), [por que a recuperação pode abrir apenas uma sessão](https://supabase.com/kb/troubleshooting/password-reset-link-logs-user-in-without-prompting-for-a-new-password-e51b22). A configuração efetiva foi conferida no painel do projeto.
