# TRANSURBAN — falas resumidas

Ordem: **José → Bruno → Cauã → Ana Carolina → Gustavo**.

Os textos são curtos. Depois de cada fala, mostrem a tela indicada. A demonstração pode ocupar mais tempo que a leitura. Não projetem senhas ou o `.env`.

## 1. José — abertura e objetivo do site

“Olá! Somos a equipe do TRANSURBAN. Nosso site tem como objetivo facilitar o acesso às informações de ônibus entre Maringá e Sarandi. Reunimos consulta de linhas, horários, avaliações e relatos em uma plataforma. Ela tem três áreas: passageiro, motorista e gestão, com acesso e funções diferentes.”

**Mostrar:** página inicial e os três acessos. Chamar o Bruno.

## 2. Bruno — passageiro

“Na área do passageiro, a pessoa escolhe a cidade, a linha e o sentido: Terminal / Bairro ou Bairro / Terminal. Ela consulta os horários disponíveis, salva suas linhas favoritas e envia avaliações ou relatos. Quando marca um local no mapa, essa informação chega à gestão para análise.”

**Mostrar:** cidade, linha, sentido e suporte. Não envie uma ocorrência inventada como se fosse real. Chamar o Cauã.

## 3. Cauã — motorista

“O motorista entra com sua conta autorizada. O sistema já identifica quem ele é. Ele informa o ônibus, escolhe a linha ou bairro e o sentido e inicia a viagem com o veículo parado. Com permissão do aparelho, sua posição é compartilhada com gestão e passageiros. Ao encerrar, o compartilhamento termina.”

**Mostrar:** identificação da conta, modelo, número do ônibus e escolha da linha. Iniciar somente se houver permissão e GPS disponível; encerrar ao terminar. Chamar a Ana Carolina.

## 4. Ana Carolina — gestão

“A gestão acompanha os ônibus em viagem e os relatos de passageiros e motoristas. O dashboard mostra os registros da sua área. No mapa, os pontos cinza aguardam análise. Depois de confirmar a situação, a gestão publica avisos em vermelho, amarelo ou verde e responde aos usuários.”

**Mostrar:** Visão geral, Ônibus em viagem e Ocorrências recebidas. Uma área sem marcação não significa trânsito livre. Chamar o Gustavo.

## 5. Gustavo — API, banco e encerramento

“As telas usam HTML, CSS e JavaScript. A API, feita com Python e FastAPI, recebe os pedidos do site, verifica o acesso e consulta o banco PostgreSQL no Supabase. Assim, os três painéis usam os mesmos registros. Para os gráficos de estudo, usamos pandas e CSV. O código fica no GitHub e executa pelo VS Code. Nosso projeto é independente e ainda pode evoluir com integrações oficiais. Obrigado!”

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
- **O que vocês testaram?** Acesso, permissões, consultas, início e fim da viagem, relatos, respostas e operações do banco. Há relatórios no repositório.

## Preparação

- Seguir o arquivo `PASSO_A_PASSO_ESCOLA.md`.
- Entrar nas contas antes de projetar a tela. Não mostrar credenciais.
- Abrir os slides, os três painéis e a API. Manter o servidor ativo.
- Testar internet e celular na rede do local.
- Cada integrante deve estudar a parte que apresenta e explicar somente o que acompanhou. O roteiro divide os assuntos; não comprova autoria individual de código.
