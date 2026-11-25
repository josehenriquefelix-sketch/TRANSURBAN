# TRANSURBAN — falas resumidas e demonstração

Revisão de fatos: **25/11/2026**. Preparação para o ensaio de sexta-feira, **27/11/2026**.

Ordem: **José → Bruno → Cauã → Ana Carolina → Gustavo**.

Os textos são curtos. Depois de cada fala, mostrem a tela indicada. A demonstração pode ocupar mais tempo que a leitura. Não projetem senhas ou o `.env`.

## 1. José — abertura e objetivo do site

“Olá! Somos a equipe do TRANSURBAN. Nosso projeto tem como objetivo facilitar o acesso às informações de ônibus em Maringá e Sarandi. Começamos organizando os cadastros e o banco de dados. Depois conectamos a API e as telas. Hoje temos três áreas: passageiro, motorista e gestão. Cada uma tem funções e permissões diferentes. A proposta é aproximar quem usa o ônibus de quem acompanha a operação.”

**Mostrar:** página inicial e os três acessos. Chamar o Bruno.

## 2. Bruno — passageiro

“No passageiro, a pessoa consulta as linhas e pode buscar pelo bairro ou código. Separamos as linhas municipais de Maringá das ligações entre Maringá e Sarandi. Os horários usam as fontes disponíveis, incluindo a consulta oficial. Com uma conta, a pessoa salva favoritos e envia avaliações ou relatos para a gestão. O site se adapta ao computador e ao celular.”

**Mostrar:** cidade, linha, sentido e suporte. Não envie uma ocorrência inventada como se fosse real. Chamar o Cauã.

## 3. Cauã — motorista

“O motorista entra com uma conta autorizada. Ele informa o modelo e o número do ônibus, escolhe a linha e o sentido e prepara a viagem. Para compartilhar a posição, precisa permitir o GPS do aparelho. A gestão e os passageiros podem acompanhar as posições recebidas. Ao encerrar a viagem, o compartilhamento termina. Essa posição vem do dispositivo autorizado; não é o GPS oficial da operadora.”

**Mostrar:** identificação da conta, modelo, número do ônibus e escolha da linha. Iniciar somente se houver permissão e GPS disponível; encerrar ao terminar. Chamar a Ana Carolina.

## 4. Ana Carolina — gestão

“A gestão tem um painel separado. Ela acompanha viagens, avaliações e relatos de passageiros e motoristas. Os indicadores vêm dos registros disponíveis. Um relato precisa ser analisado antes de virar um aviso público no mapa. As cores mostram a condição informada e confirmada pela gestão. A administração também aprova os acessos profissionais. Criar uma conta comum não dá permissão de motorista ou gestor.”

**Mostrar:** Visão geral, Ônibus em viagem e Ocorrências recebidas. Uma área sem marcação não significa trânsito livre. Chamar o Gustavo.

## 5. Gustavo — API, banco e encerramento

“As telas usam HTML, CSS e JavaScript. A API usa Python e FastAPI para receber os pedidos, conferir o acesso e consultar o PostgreSQL no Supabase. O banco da aplicação tem 12 tabelas ativas. O código e as instruções ficam no GitHub, e executamos o sistema pelo terminal do VS Code. Também temos uma parte de estudo de dados com pandas e CSV sintético. O TRANSURBAN é um projeto escolar independente, com espaço para futuras integrações oficiais. Obrigado!”

**Mostrar:** `/docs`, uma consulta GET, o VS Code e o repositório. Se houver tempo, mostrar `/dados/`. A base de análise é sintética, sem passageiros reais.

## Respostas simples para as perguntas

- **O que é API?** É a parte que recebe os pedidos das telas e devolve os dados.
- **O que é banco de dados?** É onde os registros ficam organizados em tabelas.
- **Onde está o banco?** No PostgreSQL do Supabase. Os scripts SQL e a visualização técnica estão nos arquivos do computador.
- **O que é FK?** É uma chave que liga registros de tabelas diferentes, como uma linha ligada à sua cidade.
- **Por que três áreas?** Para cada pessoa usar as funções correspondentes ao seu papel. Escolher outro endereço não concede permissão.
- **É oficial da prefeitura ou da TCCC?** Não. É um projeto escolar independente, sem adesão oficial confirmada.
- **Tem GPS da operadora?** Não. O acompanhamento usa posições compartilhadas por motoristas autorizados do TRANSURBAN.
- **O GPS é exato?** O sistema mostra a posição e a margem de precisão do aparelho. No celular, precisa de HTTPS válido e permissão.
- **O Gmail já recebe mensagens?** O fluxo está preparado; a entrega real ainda depende da configuração do SMTP.
- **O que vocês testaram?** Em 25/11, passaram 54 testes Python, 27 testes JavaScript e 34 verificações reais da API e do banco. As verificações reais incluíram login e logout nos três papéis e um chamado privado descartável com resposta e histórico. GPS físico e recebimento real de e-mail não foram comprovados nesta rodada.
- **Todas as linhas de Sarandi estão cadastradas?** Não. As 22 opções metropolitanas documentadas estão na ligação Maringá–Sarandi. A lista municipal atual completa de Sarandi continua pendente de confirmação. As 66 municipais de Maringá são do catálogo consultado em 12/11/2026.
- **Os três painéis estão no Chrome?** Os links podem ser abertos pelo usuário no Chrome. A automação do Chrome externo não ficou disponível nesta rodada; os testes HTTP não devem ser descritos como testes visuais no Chrome.
- **O projeto já vale um preço específico?** Não houve avaliação comercial comprovada. O grupo pode apresentar a proposta e o produto atual sem afirmar um valor certificado.

## Preparação

- Seguir o arquivo `PASSO_A_PASSO_ESCOLA.md`.
- Entrar nas contas antes de projetar a tela. Não mostrar credenciais.
- Abrir os três painéis e a API. Não é necessário usar slides. Manter o servidor ativo.
- Testar internet e celular na rede do local.
- Cada integrante deve estudar a parte que apresenta e explicar somente o que acompanhou. O roteiro divide os assuntos; não comprova autoria individual de código.

## Sequência rápida para ensaiar

1. José abre `/` e apresenta objetivo e as três áreas.
2. Bruno pesquisa `olimpico`, mostra a linha selecionada e o sentido. Mostra a aba Maringá ↔ Sarandi e explica a separação. Não transforma uma partida de terminal em previsão de chegada a qualquer ponto.
3. Cauã abre `/motorista/` com conta autorizada e mostra os campos do ônibus e da viagem. Não inicia uma viagem como se fosse um ônibus real da operadora. Um teste com aparelho só deve ser feito se identificado como teste, com GPS e permissão disponíveis; encerrar ao terminar.
4. Ana Carolina abre `/gestao/`, mostra visão geral e ocorrências recebidas. Se a fila estiver vazia, explicar que não há registros naquele momento. Não inventar reclamações para preencher os indicadores.
5. Gustavo abre `/docs`, usa **GET /cidades → Try it out → Execute** e mostra o JSON. No Supabase, mostra o esquema e os nomes das tabelas, sem projetar e-mails, perfis, chaves ou outros dados pessoais. Finaliza com o GitHub.

Na demonstração de API, usar GET para consultas. Evitar executar exclusões, aprovações ou publicações reais só para apresentar.
