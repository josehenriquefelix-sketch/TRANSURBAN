# Cadastro e acesso às três áreas

Revisão: 25/11/2026.

1. Inicie o servidor local seguindo o PASSO_A_PASSO_ESCOLA.md.
2. Passageiro: http://127.0.0.1:8000/#cadastro.
3. Motorista: http://127.0.0.1:8000/motorista/ → Criar conta de motorista.
4. Gestão: http://127.0.0.1:8000/gestao/ → Criar conta de gestão.

Os formulários pedem nome, CPF, e-mail, senha e confirmação. Use seus próprios dados. A senha precisa ter de 8 a 72 caracteres, com maiúscula, minúscula, número e símbolo. O CPF passa por conferência dos dígitos verificadores no navegador e na API. Essa conferência não verifica a identidade da pessoa na Receita Federal.

Também há **Continuar com Google** no login e no cadastro das áreas profissionais. A conta Google usa a identidade do provedor, sem fornecer CPF ou criar senha local. Após conectar, a pessoa pode pedir ou consultar o vínculo sem digitar a senha do Google no site. Consulte o [guia do Google nos três acessos](GOOGLE_NOS_TRES_ACESSOS.md).

Criar conta não concede acesso profissional. No motorista e na gestão, informe também o vínculo para análise. Se o Supabase retornar uma sessão confirmada, o site envia um pedido de vínculo pendente. Se exigir confirmação por e-mail, confirme primeiro, volte e clique em Continuar para solicitar autorização. Entre com a conta e envie o pedido. O responsável analisa no painel restrito; o solicitante não aprova o próprio pedido.

## Consultar e autorizar

Na entrada do motorista ou da gestão, abra **Primeiro acesso? Solicitar ou consultar autorização**. Informe e-mail ou CPF e senha. O botão **Consultar minha autorização** consulta a situação sem exigir uma nova justificativa e sem criar outro pedido. Se já estiver autorizado, volte ao formulário principal e entre com a mesma conta.

O responsável configurado como administrador entra em `/gestao/#autorizacoesGestao`, abre **Autorizar profissionais**, confere o vínculo, escolhe o escopo e registra uma justificativa para aprovar ou recusar. Contas comuns de gestão não podem conceder permissões. Não compartilhe a conta do responsável.

O vínculo aprovado é conferido diretamente pela API. A pessoa não precisa receber um e-mail de aprovação para entrar depois da decisão. A confirmação inicial da conta pelo provedor, quando exigida, é uma etapa diferente e continua necessária. Os testes reais de 25/11/2026 confirmaram entrada da conta de teste já autorizada nos três perfis e consulta à fila administrativa; não houve aprovação de uma nova pessoa durante essa conferência.

Não compartilhe contas, senhas, CPF ou documentos pelo chat de suporte. Senhas são tratadas pelo Supabase Auth; o projeto não cria uma tabela de senhas.

## Limitação ainda pendente

O SMTP autorizado ainda precisa ser configurado e a entrega real de confirmação e recuperação precisa ser testada. A presença dos formulários não comprova entrega de e-mail nem a criação de uma nova conta no provedor. Nesta revisão, os testes automatizados do fluxo usam respostas simuladas; nenhuma nova conta com CPF real foi criada para filmar.

## Vídeo atualizado

Arquivo mais recente: `docs/video/TRANSURBAN_VIDEO_EQUIPE.mp4`. Narração sintética em português do Brasil, acompanhando capturas reais das telas e indicando o tema de cada integrante. O arquivo `VIDEO_EQUIPE_LEGENDAS.srt` contém as legendas com tempos retornados pelo serviço de voz. As versões anteriores foram preservadas.
