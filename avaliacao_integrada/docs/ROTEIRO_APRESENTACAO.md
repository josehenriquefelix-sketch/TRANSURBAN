# TRANSURBAN — apresentação da equipe

Tempo sugerido: 4 a 5 minutos, incluindo a demonstração. José começa. Cada pessoa mostra uma tela depois da fala. Não mostrem senhas, chaves ou o `.env` ao público.

## 1. José — o projeto

“Olá! Nós somos José, Bruno, Cauã, Gustavo e Ana Carolina. Nosso projeto é o TRANSURBAN, voltado à mobilidade entre Maringá e Sarandi. A proposta é reunir informações do transporte e melhorar a comunicação entre passageiros, motoristas e gestão. Criamos três áreas, cada uma com suas funções. Somos estudantes do primeiro ano de Desenvolvimento de Sistemas e estamos aplicando o que aprendemos.”

**Mostrar:** página inicial e explicar os três acessos. Passar a fala ao Bruno.

## 2. Bruno — passageiro

“O passageiro escolhe a cidade, a linha e o sentido: Terminal / Bairro ou Bairro / Terminal. Ele consulta as informações disponíveis, salva favoritos e envia avaliações ou relatos. Se informar um local no mapa, a gestão recebe esse ponto para analisar. A tela se adapta ao computador e ao celular.”

**Mostrar:** cidade, linha, sentido e suporte. Não envie uma reclamação inventada durante a apresentação. Passar ao Cauã.

## 3. Cauã — motorista

“O motorista entra com uma conta já autorizada. O sistema reconhece quem ele é. Ele informa o ônibus, escolhe a linha ou bairro e o sentido, e inicia a viagem com o veículo parado. Com sua permissão, o aparelho envia a localização. Essa mesma viagem aparece para a gestão e para os passageiros. Ao encerrar, o compartilhamento termina.”

**Mostrar:** conta autorizada, ônibus e linha. Só inicie uma viagem se o GPS estiver disponível e autorizado; encerre ao terminar. Passar ao Gustavo.

## 4. Gustavo — gestão

“A gestão acompanha os ônibus em viagem, os motoristas e os relatos recebidos. No mapa, os pontos cinza são relatos aguardando análise. Depois da confirmação, a gestão pode publicar orientações em vermelho, amarelo ou verde. Ela também responde aos usuários. O painel é voltado à operação dos ônibus; as ferramentas técnicas do banco ficam separadas.”

**Mostrar:** Visão geral, Ônibus em viagem e Ocorrências recebidas. Uma área sem marcação não significa trânsito livre. Passar à Ana Carolina.

## 5. Ana Carolina — API, banco e encerramento

“Usamos HTML para a estrutura, CSS para o visual e JavaScript para as ações das telas. A API foi feita com Python e FastAPI: ela recebe os pedidos, confere o acesso e conversa com o banco PostgreSQL do Supabase. O pandas calcula os resultados do nosso CSV de estudo. O código fica no GitHub e o sistema executa pelo VS Code.”

“Fizemos testes dos acessos, das consultas e das operações do banco. Ainda precisamos de integrações externas para dados oficiais ao vivo e envio de e-mails. Nosso próximo passo é testar com usuários e continuar melhorando o projeto. Obrigada!”

**Mostrar:** `/docs`, uma consulta GET e o repositório. Se houver tempo, mostrar `/dados/`. O CSV é de estudo; não representa passageiros reais.

## Respostas curtas para perguntas

- **O que é API?** É a parte que recebe os pedidos da tela e devolve os dados.
- **O que é banco de dados?** É onde os registros ficam organizados em tabelas.
- **O banco está no computador?** O código, os scripts SQL e a visualização técnica estão no computador. Os dados continuam no PostgreSQL do Supabase.
- **O que é uma chave estrangeira?** É um campo que liga registros de tabelas diferentes, como uma linha ligada à sua cidade.
- **Por que três áreas?** Cada pessoa vê e faz o que corresponde ao seu papel. Escolher outro endereço não dá permissão de gestão.
- **A gestão precisa autorizar cada viagem?** O motorista precisa ter uma conta autorizada. Depois de iniciar, a viagem fica disponível automaticamente. Relatos são analisados antes de virar avisos públicos.
- **Já é um serviço da prefeitura ou da TCCC?** Não. É um projeto escolar independente, sem adesão oficial confirmada.
- **O GPS é exato?** Ele usa a posição e a margem de precisão do aparelho. No celular, precisa de HTTPS válido e permissão.
- **Já envia e-mail ao Gmail?** O fluxo está preparado, mas o envio real ainda depende do SMTP.
- **Por que não há banco e compras na Gestão?** A Gestão acompanha o transporte. O banco é consultado nas ferramentas do desenvolvedor; o exercício de materiais fica isolado.

## Antes de apresentar

1. Baixar a versão atual do GitHub e configurar o `.env` em particular.
2. Iniciar pelo VS Code e manter a API aberta.
3. Entrar nas contas autorizadas antes de começar; não projetar a senha.
4. Testar a rede e o celular no local. HTTP da rede permite telas e login por senha, mas não libera GPS no celular.
5. Abrir os slides, os três painéis e a API. Não usar o endereço antigo do Render.
6. Ensaiar e estudar o código. Cada integrante deve explicar a parte que acompanhou, sem atribuir contribuições que não fez.
