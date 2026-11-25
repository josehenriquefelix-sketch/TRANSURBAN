# Google, e-mail e CPF nos três acessos

Revisão: 25/11/2026.

Passageiro, motorista e gestão oferecem entrada por e-mail/CPF e senha, cadastro próprio e Google. No motorista e na gestão há **Continuar com Google** tanto no login quanto na criação da conta. O mesmo Supabase Auth atende as três entradas.

## Como usar

1. Abra `/motorista/` ou `/gestao/` no servidor local.
2. Clique em **Continuar com Google** e escolha sua conta na página do Google. Não digite a senha do Google em um formulário do TRANSURBAN.
3. Se a conta já possuir o vínculo profissional ativo, o servidor retorna ao painel correspondente.
4. Sem vínculo ativo, retorna à área de solicitação, com a identidade conectada. Informe seu vínculo e envie o pedido, ou clique em **Consultar minha autorização**. Não é necessário criar uma senha local para pedir autorização usando Google.
5. O responsável analisa e decide na central restrita. O login Google não cria vínculos administrativos ou de motorista automaticamente. O solicitante não aprova o próprio pedido.
6. Para trocar a conta conectada, use **Sair desta conta** e depois entre novamente.

O cadastro próprio continua solicitando nome, CPF, e-mail, senha e confirmação. Google usa a identidade do provedor; não fornece o CPF nem cria uma senha local. O vínculo é ligado ao identificador da conta no Supabase, e não ao botão em que a pessoa clicou.

## Validação e limites

- Provedor Google confirmado ativo por `/auth/configuracao`.
- Teste real no navegador: seleção de uma Conta Google já existente e retorno correto para as duas áreas sem vínculo, mantendo o painel protegido. Consulta de autorização usando a sessão Google funcionou sem senha local. Nenhum pedido real ou nova permissão foi criado durante o teste.
- Testes automatizados verificam retorno de motorista e gestor autorizados, retorno sem vínculo, rejeição de estado inválido e papel adulterado. O caminho aprovado usa respostas simuladas nos testes; não foi concedido novo papel a uma Conta Google real.
- Os links públicos da política de privacidade e dos termos na tela de consentimento Google ainda apontam para o endereço histórico de hospedagem. Isso é uma pendência de configuração da marca no Google Cloud; a autenticação testada retornou ao servidor local. Não foi contratado ou reativado serviço de hospedagem.
- Confirmação e recuperação por e-mail/senha continuam dependendo do envio configurado e testado. Google não substitui a aprovação profissional.

Referências técnicas consultadas em 25/11/2026: [Google com Supabase](https://supabase.com/docs/guides/auth/social-sign-in/auth-google), [URLs de retorno](https://supabase.com/docs/guides/auth/redirect-urls). O fluxo do projeto usa PKCE, valida estado, troca código no backend e mantém os tokens da sessão em cookies HttpOnly.
