# TRANSURBAN — roteiro da equipe

Tempo sugerido: 4 a 5 minutos. Cada pessoa fala e mostra sua parte. Ensaiem antes e usem apenas funções que conseguem demonstrar.

## 1. José — abertura

“Olá! Nós somos a equipe do TRANSURBAN. Nosso projeto tem como tema a mobilidade entre Maringá e Sarandi. A ideia é reunir informações de transporte e facilitar a comunicação entre passageiros, motoristas e gestão. Somos estudantes do primeiro ano de Desenvolvimento de Sistemas e usamos o que aprendemos para construir este sistema.”

**Mostrar:** página inicial do passageiro e as três áreas, sem exibir senhas.

## 2. Bruno — passageiro

“Na área do passageiro, a pessoa escolhe a cidade e consulta as linhas. Ela também pode salvar suas linhas favoritas e enviar uma manifestação. Organizamos a tela para funcionar no computador e no celular. As informações têm limites: um horário publicado não é uma previsão de GPS ao vivo.”

**Mostrar:** cidades, escolha de linha e um favorito na conta de teste.

## 3. Cauã — motorista

“O motorista entra com uma conta autorizada. Ele informa o modelo e o número do ônibus, escolhe a linha e prepara a viagem. O compartilhamento da localização depende da permissão do aparelho. O mapa mostra a posição e a margem de precisão recebidas. Não temos integração com o GPS oficial da operadora.”

**Mostrar:** entrada do motorista, campos do ônibus e escolha da linha. Só inicie uma viagem de teste se o ambiente de localização estiver funcionando; encerre ao terminar.

## 4. Gustavo — gestão e banco

“A gestão tem um painel separado. Nele, a equipe autorizada acompanha manifestações e responde aos usuários. O banco PostgreSQL fica no Supabase. As tabelas usam códigos para identificar registros e chaves estrangeiras para relacioná-los. No módulo de materiais, uma ordem pode ter vários itens, e o fechamento confere o estoque antes de gravar as mudanças.”

**Mostrar:** fila da gestão, lista de tabelas e uma ordem de teste. Não mostre dados privados de pessoas.

## 5. Ana Carolina — API, dados e encerramento

“Usamos HTML para a estrutura, CSS para as cores e os tamanhos e JavaScript para as ações da tela. A API foi feita com Python e FastAPI. Ela recebe os pedidos e conversa com o Supabase. Na parte de Ciência de Dados, o pandas calcula os resultados do CSV e o site mostra os gráficos. Essa base é de estudo. O projeto fica no GitHub e pode ser baixado para executar pelo VS Code.”

“Fizemos testes para conferir acessos, consultas e operações do banco. Ainda existem integrações externas a configurar, como envio de e-mails e dados oficiais ao vivo. Nosso próximo passo é testar com usuários e continuar melhorando o sistema. Obrigada!”

**Mostrar:** `/docs`, `/dados/` e o repositório. No chat, o cálculo funciona sem Ollama; a explicação por IA é opcional e ainda depende de configuração.

## Perguntas que podem aparecer

**O que é API?** É a parte que recebe os pedidos da tela e devolve os dados.

**O que é uma chave estrangeira?** É um campo que liga um registro a outro, como o código da cidade em uma linha.

**Está integrado à prefeitura ou à TCCC?** Não. É um projeto escolar independente; dados públicos e registros do nosso sistema não são uma integração oficial.

**Já envia e-mail?** A configuração está preparada, mas a entrega real ainda depende do SMTP.

**O GPS é exato?** Ele usa a posição e a precisão que o aparelho informa. Pode variar; no celular precisa de HTTPS válido.

**Como foi feito?** Estudamos os materiais, adaptamos ao TRANSURBAN e usamos ferramentas de apoio. Cada integrante deve explicar o código que estudou e a parte em que trabalhou. Não atribuam contribuições que não fizeram.
