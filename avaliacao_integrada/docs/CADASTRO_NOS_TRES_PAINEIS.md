# Cadastro e acesso às três áreas

Revisão: 25/11/2026.

1. Inicie o servidor local seguindo o PASSO_A_PASSO_ESCOLA.md.
2. Passageiro: http://127.0.0.1:8000/#cadastro.
3. Motorista: http://127.0.0.1:8000/motorista/ → Criar conta de motorista.
4. Gestão: http://127.0.0.1:8000/gestao/ → Criar conta de gestão.

Os formulários pedem nome, CPF, e-mail, senha e confirmação. Use seus próprios dados. A senha precisa ter de 8 a 72 caracteres, com maiúscula, minúscula, número e símbolo. O CPF passa por conferência dos dígitos verificadores no navegador e na API. Essa conferência não verifica a identidade da pessoa na Receita Federal.

Criar conta não concede acesso profissional. No motorista e na gestão, informe também o vínculo para análise. Se o Supabase retornar uma sessão confirmada, o site envia um pedido de vínculo pendente. Se exigir confirmação por e-mail, confirme primeiro, volte e clique em Continuar para solicitar autorização. Entre com a conta e envie o pedido. O responsável analisa no painel restrito; o solicitante não aprova o próprio pedido.

Não compartilhe contas, senhas, CPF ou documentos pelo chat de suporte. Senhas são tratadas pelo Supabase Auth; o projeto não cria uma tabela de senhas.

## Limitação ainda pendente

O SMTP autorizado ainda precisa ser configurado e a entrega real de confirmação e recuperação precisa ser testada. A presença dos formulários não comprova entrega de e-mail nem a criação de uma nova conta no provedor. Nesta revisão, os testes automatizados do fluxo usam respostas simuladas; nenhuma nova conta com CPF real foi criada para filmar.

## Vídeo atualizado

Arquivo: `docs/video/TRANSURBAN_GUIA_NARRADO.mp4`. Narração sintética em português do Brasil, acompanhando capturas reais das telas. O arquivo SRT contém as legendas com tempos retornados pelo serviço de voz. A versão anterior, sem áudio, foi preservada.
