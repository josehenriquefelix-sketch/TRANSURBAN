# Operação do TRANSURBAN

Versão de 12/11/2026. A plataforma é independente e não representa a Prefeitura, o DER/PR, a TCCC ou a Cidade Verde. Não existe adesão institucional confirmada.

## Áreas e permissões

O cadastro público cria uma conta de passageiro no Supabase Auth. A aba Motorista/Gestão no login apenas seleciona o tipo de acesso: ela não concede um papel. A API verifica os vínculos ativos em `tu_acesso` e o escopo de gestão em cada solicitação. `ADMIN_EMAILS`, definido somente no backend, identifica a administração da equipe e permite o CRUD acadêmico de cidades/linhas e a central completa.

Para autorizar um profissional, o responsável pelo banco deve confirmar sua identidade e vínculo fora do sistema. Depois deve localizar seu UUID em Authentication → Users e executar no SQL Editor, substituindo o UUID fictício:

```sql
-- Motorista verificado: não use o UUID fictício abaixo.
insert into public.tu_acesso(usuario_id,papel,escopo,ativo)
values ('00000000-0000-0000-0000-000000000000','motorista','metropolitano',true)
on conflict(usuario_id,papel) do update set ativo=true;

-- Gestor verificado: escolha apenas a competência autorizada.
-- Escopos: maringa, sarandi, metropolitano; todos exige autorização ampla.
insert into public.tu_acesso(usuario_id,papel,escopo,ativo)
values ('00000000-0000-0000-0000-000000000000','gestor','metropolitano',true)
on conflict(usuario_id,papel) do update set ativo=true,escopo=excluded.escopo;
```

Para revogar um vínculo, atualize `ativo=false` no registro correto. Não coloque UUIDs, senhas ou chaves de contas reais no repositório. A conta da equipe em `ADMIN_EMAILS` é administração do TRANSURBAN, não conta institucional de um órgão público.

## Manifestação e resposta

O passageiro seleciona cidade e linha, informa tipo/categoria e descreve a experiência. A associação opcional a uma viagem identifica o motorista no servidor; o cliente não pode escolher livremente seu UUID. Uma nota de motorista exige viagem vinculada. O protocolo `TU-000001` é da plataforma. O sistema não envia automaticamente uma denúncia a órgãos externos.

A competência deriva da linha documentada. A central retorna até 500 manifestações recentes do escopo autorizado. Um gestor municipal não acessa a fila metropolitana sem esse vínculo. Cada resposta e alteração de estado gera evento no banco; registros encerrados não podem receber nova alteração. O passageiro consulta apenas suas manifestações. O motorista consulta apenas as vinculadas às próprias viagens.

## Localização e mapa

O motorista configura modelo/prefixo e perfil antes de iniciar. Há no máximo uma viagem ativa por motorista e prefixo. A posição só é enviada após consentimento e permissão de localização no navegador, com intervalo mínimo de dez segundos e precisão informada de até 1.000 metros. O servidor grava a hora do recebimento. Posições com mais de 90 segundos são identificadas como desatualizadas. Ao encerrar, a viagem sai da consulta pública e a função SQL recusa novas posições.

O mapa utiliza Leaflet 1.9.4 e OpenStreetMap, com atribuição visível, sem download em massa ou modo offline. O navegador mantém cache normal dos mapas. A política de referência envia somente a origem nas solicitações externas, permitindo identificar o site ao provedor. A disponibilidade do mapa depende de internet e do serviço externo. Não existe geometria oficial integrada: nenhuma rota inventada é desenhada como itinerário autorizado.

Use HTTPS em hospedagem e mantenha o navegador aberto. Uma aba fechada, telefone bloqueado ou aplicativo em segundo plano pode interromper o GPS; esse site não garante rastreamento contínuo em segundo plano. O Waze é aberto externamente como apoio de navegação e não substitui o itinerário autorizado do ônibus.

## Google e recuperação de senha

O backend implementa Google OAuth com PKCE, cookies temporários HttpOnly e conferência de estado. Para habilitar, o responsável deve configurar um cliente OAuth no Google Cloud, fornecer o Client ID/Secret em Supabase Authentication → Sign In / Providers → Google e autorizar o callback exibido pelo Supabase. O segredo não entra no JavaScript nem no GitHub.

Em Supabase Authentication → URL Configuration, configure o Site URL e permita os retornos do próprio site, incluindo `/auth/google/callback` e `/#nova-senha`. No computador local, use a mesma origem `http://127.0.0.1:8000` do `APP_URL`; em hospedagem, use HTTPS e `COOKIE_SECURE=true`. Não habilite URLs de retorno arbitrárias.

Configure SMTP para enviar confirmação/recuperação ao público. A resposta de solicitação de recuperação não revela se o e-mail existe. A senha nova exige mínimo de oito caracteres com maiúscula, minúscula, número e símbolo. O Supabase recusa a senha igual à anterior; a API mostra uma mensagem específica. A validação de entrega do e-mail e do retorno real do Google depende de configuração externa e precisa ser feita com uma conta do responsável.

## Dados e cobertura

O catálogo em `data/catalogo_publico_verificado.json` separa 66 linhas municipais de Maringá, conferidas na lista oficial Na Hora, e 22 atendimentos de Sarandi, incluindo variantes de bairro de 12 documentos DER/PR. As contagens das 1.064 partidas documentais foram comparadas às frequências diárias dos cabeçalhos. As variantes I/IT/O/SP, U/L/SJ/A, N/C/IP e J preservam as legendas dos documentos. Bairros intermediários não são inferidos pelo nome da linha.

A seleção da linha abre os horários automaticamente. O quadro oficial Na Hora/Bus2 é incorporado para as linhas municipais, com link alternativo para abrir diretamente. Ele carrega o conteúdo público do provedor; não utiliza credenciais de API nem transforma esse acesso em parceria institucional. Sua aba Pontos e trajeto apresenta paradas por viagem. A busca por endereço/ponto usa o quadro público indicado pelo próprio site Na Hora. A disponibilidade de ETA continua sendo do provedor.

Os dados metropolitanos são partidas publicadas no DER, com vigência explícita, e não uma previsão de passagem por ponto. A página municipal de Sarandi sobre Alvamar ↔ Conjunto Floresta não informa vigência recente; por isso é vinculada com esse limite, sem prometer operação atual. O cadastro completo e atualizado dos pontos municipais de Sarandi não foi confirmado.

Fontes:

- [Na Hora — Consulta oficial por linha](https://www.nahoramaringa.com.br/pesquisa-por-linhas/)
- [Na Hora — Consulta oficial por endereço e ponto](https://www.nahoramaringa.com.br/pesquisa-geral/)
- [Prefeitura de Sarandi — Transporte urbano, vigência não informada](https://sarandi.pr.gov.br/web/index.php/servicos/horarios-transporte-publico)

- [DER/PR — Horários Vigentes](https://www.der.pr.gov.br/Pagina/Horarios-Vigentes)
- [DER/PR — Aeroporto/Sarandi, vigência 01/02/2026](https://www.der.pr.gov.br/sites/der/arquivos_restritos/files/documento/2026-02/Maringa_Sarandi_Aeroporto_REG0511_Linha0030254430_010226.pdf)
- [TCE/PR — Gestão da concessão municipal de Maringá](https://www.tce.pr.gov.br/noticias/tce-pr-orienta-maringa-para-melhorar-gestao-do-transporte-coletivo-municipal/12127/N.htm)
- [SEMOB — Ofício 18/2023 sobre integração metropolitana](https://sapl.cmm.pr.gov.br/media/sapl/public/documentoacessorio/2023/24786/req_173.pdf)
- [Na Hora — Maringá, canal oficial da operadora](https://play.google.com/store/apps/details?id=com.maringa.voudeonibus&hl=pt_BR)
- [OpenStreetMap — Política de uso dos mapas](https://operations.osmfoundation.org/policies/tiles/)
- [Supabase — Login Google](https://supabase.com/docs/guides/auth/social-sign-in/auth-google)
- [Waze — Deep links](https://developers.google.com/waze/deeplinks)

## Verificação

Execute `backend/.venv/Scripts/python.exe -m unittest discover -s tests -v` no Windows ou o equivalente no ambiente ativado. Execute também `verificar_ambiente.py` com a aplicação aberta. Os testes com Supabase real de 12/11/2026 usaram contas descartáveis e estão resumidos em `VALIDACAO_MOBILIDADE_20261112.json`. Testes com coordenadas sintéticas não comprovam o GPS de um aparelho real.


## Atualização de 13/11/2026 — três ambientes

O portal público não exibe a central de gestão nem a área operacional. Passageiro usa `/`, motorista usa `/motorista/`, gestão usa `/gestao/`. Compartilham a origem e a sessão; trocar de conta ou sair vale para todos os painéis desse navegador. O backend verifica papéis e competências em cada consulta, independentemente da página aberta.

A migração `07_suporte_e_aprovacoes.sql` cria chamados privados, eventos de resposta, alertas operacionais com validade e solicitações de vínculo. A administração definida em `ADMIN_EMAILS` revisa os pedidos, confirma identidade e vínculo e justifica a decisão. A função transacional bloqueia autoaprovação e decisões repetidas; a criação de uma solicitação nunca concede papel.

Relatos de acessibilidade, obras e trânsito chegam à gestão do escopo correspondente. O mapa público só apresenta informações que a gestão publicou manualmente; sem marcação significa sem informação. A orientação não modifica automaticamente itinerários oficiais. A localização do visitante só é solicitada após clique, mostra a precisão do dispositivo e não preenche nem envia silenciosamente sua posição. Marcar uma ocorrência no mapa é uma ação separada.

O login distingue e-mail não confirmado de credencial inválida; há reenvio solicitado pelo usuário. Google foi conferido e permanece desativado, com Client ID e Client Secret vazios. Para ativar, o responsável configura uma aplicação OAuth no Google Cloud e preenche diretamente o Supabase; não publicar segredos no repositório. O callback do projeto é `https://lsnpvokfnvyjkvqzkvof.supabase.co/auth/v1/callback`.

Validação: 31 testes automatizados; login de conta confirmada por e-mail e CPF; suporte, resposta, isolamento de escopo, retirada de alerta e aprovação com Supabase real em `VALIDACAO_SUPORTE_20261113.json`. As contas e os dados sintéticos foram descartados. Esses testes não confirmam entrega de e-mail, integração com GPS da operadora, pagamentos nem cobertura municipal completa de Sarandi.
