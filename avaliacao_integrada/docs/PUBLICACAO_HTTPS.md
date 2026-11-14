# Publicar o TRANSURBAN com um link HTTPS

O arquivo `render.yaml` na raiz do GitHub prepara um serviço Python que publica o site e a API na mesma origem. O banco existente continua no Supabase; nenhuma migração é reaplicada pelo deploy.

## Configuração

- Serviço: Web Service / Python, plano Free para avaliação.
- Repositório: https://github.com/josehenriquefelix-sketch/TRANSURBAN
- Root Directory: `avaliacao_integrada`.
- Build: `pip install -r backend/requirements.txt`.
- Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips '*'`.
- Health Check: `/health`.
- Python: `3.13.15`; cookies seguros ativados; atualização automática desativada para controlar a publicação.

Cadastre `SUPABASE_URL`, `SUPABASE_KEY` e `ADMIN_EMAILS` diretamente nas variáveis privadas do Render. Não publique `.env`, senhas ou chaves no GitHub. A chave de serviço autoriza acesso privilegiado ao banco; conceda acesso ao painel da hospedagem somente a responsáveis da equipe.

O aplicativo usa `RENDER_EXTERNAL_URL` para os retornos de autenticação quando `APP_URL` não está definido. Para domínio próprio, configure `APP_URL` com seu endereço HTTPS e atualize as configurações externas.

## Depois do primeiro deploy

1. Aguarde o serviço indicar que está ativo e copie o endereço HTTPS realmente fornecido pelo Render. O nome desejado pode não estar disponível; não invente o endereço antes da criação.
2. No Supabase, em Authentication > URL Configuration, configure esse endereço como Site URL e autorize os retornos usados pelo aplicativo, preservando os endereços locais necessários.
3. No cliente Web do Google, acrescente a origem HTTPS publicada. O redirect do Google continua sendo o callback HTTPS do projeto Supabase, não o localhost.
4. Cadastre Client ID e Client Secret diretamente no provedor Google do Supabase. Ative somente os escopos de identidade necessários: openid, e-mail e perfil.
5. Se o aplicativo Google estiver em modo de teste, permita as contas de teste da equipe. A publicação para a população exige revisar público, domínio, política de privacidade, consentimento e os requisitos de verificação do Google.
6. Verifique a página inicial, os três portais, login, logout, recuperação de senha, permissões e leitura/gravação no Supabase usando HTTPS.

## Limites do plano gratuito

O Render informa que um serviço Free pode suspender após 15 minutos sem acesso e levar cerca de um minuto para voltar. Há limites de uso e a modalidade não é indicada pelo provedor para operação de produção. Não use artifícios para manter o serviço ativo. Antes de uso público contínuo, escolha um plano e uma capacidade adequados com autorização do responsável. Não foi contratado plano pago neste preparo.

Referências: https://render.com/docs/deploy-fastapi ; https://render.com/docs/free ; https://render.com/docs/blueprint-spec ; https://supabase.com/docs/guides/auth/social-sign-in/auth-google .

## Publicação realizada — 13/11/2026

O Render publicou o serviço Free em https://transurban-mobilidade.onrender.com. O health check retornou a versão `2026.11.13-portais` com Supabase configurado. O login Google foi concluído no endereço HTTPS; o portal mostrou sessão de passageiro. Site URL e retorno público foram cadastrados no Supabase, preservando os retornos locais. O cliente Google inclui a origem HTTPS. As páginas de privacidade e uso identificam o responsável e o contato que o usuário aprovou publicar.

A versão de código `f330ad7` foi implantada, incluindo as páginas aprovadas de privacidade e uso. Depois disso, o Google confirmou o status **Em produção**. O logout HTTPS foi conferido: a sessão terminou e a rota privada de conta voltou a exigir autenticação. Atualizações posteriores somente nestes relatórios não exigem reinstalar o serviço.
