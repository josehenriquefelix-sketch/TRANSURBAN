# TRANSURBAN — Mobilidade que conecta

Portal de transporte e participação cidadã entre Maringá e Sarandi, com áreas de **passageiro**, **motorista autorizado** e **gestão autorizada**.

O projeto atual está na pasta [avaliacao_integrada](avaliacao_integrada). Site e API iniciam juntos em **http://127.0.0.1:8000/**.

## Abrir pelo VS Code em outro computador

1. Instale Git e Python 3.10+; no Windows, marque **Add Python to PATH**.
2. No VS Code, pressione **Ctrl+Shift+P → Git: Clone** e cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`.
3. Abra o repositório. Copie `avaliacao_integrada/backend/.env.example` para `avaliacao_integrada/backend/.env` e preencha os dados privados do mesmo projeto Supabase. Esse arquivo não vem pelo GitHub.
4. Na raiz, execute **INICIAR_TRANSURBAN.cmd**. Na primeira abertura ele prepara o ambiente e instala as dependências. Mantenha o servidor aberto.
5. Acesse **http://127.0.0.1:8000/**. O menu **API do sistema** abre **http://127.0.0.1:8000/docs**.
6. Execute **VERIFICAR_TRANSURBAN.cmd** para conferir dependências, tabelas, site e API.

Se já estiver clonado, atualize com `git pull` antes de iniciar, preservando suas alterações locais. O banco da equipe já recebeu as migrações 05 e 06; usar o mesmo Supabase em outro computador não exige reinstalar as tabelas.

O endereço `127.0.0.1` é local a cada computador. Para acesso público ou por vários dispositivos, é necessário hospedar o sistema em HTTPS e configurar as URLs do Supabase.

## O que está implementado

- Login por e-mail/CPF, sessão em cookies HttpOnly, cadastro, logout e fluxo de recuperação de senha.
- Início, dashboard com documentos oficiais, cidades/linhas, horários e mapa, favoritas, avaliações e conta, com layout responsivo.
- Perfil/veículo do motorista, notas vinculadas, início/encerramento de viagem e envio consentido da posição do dispositivo.
- Central de manifestações com protocolo, filtros por escopo, atendimento e resposta ao cidadão.
- CRUD acadêmico de cidade e linha com FK na API protegida. Ciência de Dados permanece separada em `/dados/docs`.

## Cobertura e dependências externas

O catálogo separa as 66 linhas municipais de Maringá publicadas no Na Hora das ligações que atendem Sarandi. Em Sarandi, são 22 atendimentos, incluindo variantes de bairro, documentados em 12 tabelas do DER/PR. Foram conferidas 1.064 partidas documentais, sem duplicar as variantes. Ao escolher a linha, o site abre os horários; em Maringá, oferece também a consulta pública oficial incorporada com pontos e itinerários. O serviço municipal interbairros de Sarandi está identificado separadamente, com confirmação de vigência pendente. Horários de saída não são previsões de passagem em todos os pontos. Não há API autorizada de telemetria nem integração de bilhetagem.

O código de Google OAuth está implementado, mas o provedor ainda precisa de credenciais/configuração no Supabase. Confirmação e recuperação por e-mail precisam de SMTP e teste de entrega real. O GPS do navegador requer permissão, contexto seguro e página aberta; as verificações automatizadas não comprovam um sensor GPS real.

O TRANSURBAN é independente. Não há adesão institucional confirmada de Prefeitura, DER/PR ou operadora. As manifestações ficam na central TRANSURBAN; seu encaminhamento institucional depende dessa adesão.

## Instruções e testes

- [Instalação completa, tecnologias e atividade escolar](avaliacao_integrada/README.md)
- [Operação, papéis, Google, GPS e fontes](avaliacao_integrada/docs/MOBILIDADE_OPERACAO.md)
- [Validação com Supabase real — 12/11/2026](avaliacao_integrada/docs/VALIDACAO_MOBILIDADE_20261112.json)
- [Atividade de chave estrangeira](avaliacao_integrada/docs/RELACIONAMENTO_FK_CIDADE_LINHA.md)

Os arquivos de outras etapas permanecem no repositório como histórico. Para executar o portal atual, use **avaliacao_integrada** e a porta **8000**. Nunca publique `.env`, senhas, chaves secretas ou o ambiente virtual.
