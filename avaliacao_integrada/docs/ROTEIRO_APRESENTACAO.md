# Roteiro de apresentação — TRANSURBAN

## Antes de apresentar

1. No computador que fará a demonstração, instale as dependências conforme o README.
2. Copie `backend/.env.example` para `backend/.env` e configure a URL e a chave privada do projeto Supabase da equipe. Não mostre nem envie essa chave.
3. Confira as tabelas e os nomes das colunas no projeto Supabase correto. Use `database/01_auditar_esquema.sql` antes de aplicar qualquer DDL.
4. Dê duplo clique no atalho `ABRIR TRANSURBAN` (ou execute `iniciar_local.cmd`). Ele inicia um serviço e abre a interface. O Swagger fica em `http://127.0.0.1:8000/docs`.
5. Combine nomes fictícios para os registros de teste. Anote o ID criado para editar, consultar e excluir o mesmo registro e evitar deixar dados de teste no banco.

## Fala de abertura

“Nosso projeto TRANSURBAN organiza informações acadêmicas sobre transporte coletivo em Maringá e Sarandi. A interface foi feita em HTML, CSS e JavaScript. O backend usa Python e FastAPI, e a persistência é no Supabase com PostgreSQL. O projeto mostra um CRUD de cidades e linhas e um resumo descritivo de uma base CSV.”

## Demonstração das telas

1. Mostre o topo do site e explique que a navegação leva ao resumo dos dados, às cidades, às linhas e à documentação da API.
2. No resumo, apresente os quatro agrupamentos: por cidade, período, condição de trânsito e clima. Os indicadores e tabelas são carregados pela API.
3. Explique que cada linha do CSV representa uma observação acadêmica de atraso, não necessariamente uma viagem completa. A base é sintética e não representa a operação real.
4. Em **Cadastro de cidades**, cadastre uma cidade fictícia. Mostre a confirmação e o ID gerado. Consulte esse ID, edite o nome, atualize a lista e exclua o registro de teste. Se houver linha vinculada, o banco pode bloquear a exclusão para preservar a chave estrangeira.
5. Em **Linhas de ônibus**, selecione uma cidade existente, cadastre código e nome, consulte e edite a linha. Exclua o registro de teste ao terminar. A rota exige uma cidade válida.
6. Se a interface estiver indisponível, abra o Swagger e demonstre as rotas equivalentes. Para erros, mostre a validação de campo obrigatório (422), ID inexistente (404) e restrição de vínculo (409 quando aplicável).
7. No Supabase Table Editor, confirme os registros criados e removidos durante a demonstração. Não exponha a chave privada.

## Explicação da comunicação

1. A FastAPI entrega a página HTML, os arquivos CSS/JavaScript e as rotas da API pelo mesmo serviço local.
2. O JavaScript chama as rotas FastAPI na mesma origem `127.0.0.1:8000`.
3. Como tela e API compartilham a origem, o navegador não precisa fazer uma requisição entre origens na abertura padrão.
4. Para o CRUD, a API valida os dados com modelos Pydantic e acessa o Supabase pela Data API HTTPS usando segredo mantido só no backend.
5. As rotas de Ciência de Dados leem e validam o CSV com pandas, agrupam as observações e devolvem JSON para a página.

## Fala de encerramento

“Testamos as operações no Swagger e pela interface, conferimos as alterações no banco e validamos as quatro totalizações do CSV. O CRUD obrigatório da recuperação é o de cidade, pois é a tabela com chave primária que não possui chave estrangeira. As linhas entram na avaliação integrada e mantêm o vínculo com cidade. A base de análise é sintética, então os resultados servem para demonstrar o funcionamento, não para tirar conclusões sobre o transporte real.”

## Divisão de falas

- **HTML:** apresenta estrutura, formulários, tabelas, seções e navegação.
- **CSS:** explica cores, hierarquia visual, acessibilidade e reorganização da tela em celular e computador.
- **JavaScript:** mostra validação no navegador, chamadas `fetch`, feedback, edição e exclusão.
- **API e CORS:** explica modelos, rotas FastAPI, origens permitidas e acesso HTTPS ao Supabase.
- **Ciência de Dados:** explica o CSV, o significado da observação, os agrupamentos e os limites dos dados sintéticos.

Se a equipe tiver menos integrantes, uma pessoa pode apresentar mais de uma parte. Todos devem saber explicar o fluxo completo.

