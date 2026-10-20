# TRANSURBAN — como vamos testar a API na apresentação

Integrantes: José, Kauan, Bruno, Gustavo e Ana Carolina, de DS.

Tempo planejado: 8min25s, incluindo cliques e execução dos testes. Margem: 35s até 9 minutos. Ensaiar com cronômetro.

Este roteiro é para explicar e executar os testes da API. A instalação fica fora do tempo da apresentação.

## Preparação antes de começar

Na pasta backend, com o PostgreSQL local ativo, iniciar um ensaio local SEM cadastros automáticos:

```powershell
.\.venv\Scripts\python.exe executar_auditorio.py --schema transurban_auditorio_palco --vazio
```

Esse comando não apaga dados. Use um schema ainda não utilizado para mostrar os cadastros com 201. Se já ensaiou com palco, troque apenas o final para palco2. Anote o comando escolhido: Ana Carolina deve repetir exatamente o mesmo para demonstrar persistência.

Abrir http://127.0.0.1:8001/docs e http://127.0.0.1:8001/site/. Deixar um segundo terminal na pasta backend para os testes. Não abrir o .env na tela. O Supabase permanece separado, na porta 8000. Todos os POSTs desta apresentação são feitos no modo local.

Antes de começar, GET /cidades e GET /linhas devem estar vazios nesse schema novo. Se houver registros, preserve-os e prepare outro schema de ensaio, sem apagar tabelas.

## José — 0:00 a 1:20 — Problema, objetivo e solução

**Resumo:** Você abre a apresentação. Mostre a seção O projeto no site. Ainda não execute cadastros.

**Fala:**

“Boa tarde. Somos José, Kauan, Bruno, Gustavo e Ana Carolina, de DS. O TRANSURBAN busca organizar informações do transporte coletivo de Maringá e Sarandi.

A ideia é reunir cidades, linhas e seus vínculos em uma base que seja fácil de consultar e manter. A solução usa um banco de dados, uma API e um site integrado.

Nesta etapa, já temos cadastro e consulta de cidades e linhas. Outras análises, como estudos de atrasos, dependem de dados oficiais e de desenvolvimento futuro.

Agora vamos mostrar os testes na prática: cadastrar, consultar, provocar erros de validação e conferir se os dados permanecem salvos.”

**O que fazer na tela:**

Abrir o site local e depois a documentação em http://127.0.0.1:8001/docs. A API e o banco já devem estar ativos.

## Kauan — 1:20 a 2:20 — Cadastrar e consultar cidades

**Resumo:** Você faz POST /cidades e GET /cidades. Explique que o ID é gerado pelo banco e anote o ID real de Sarandi.

**Fala:**

“Vamos começar pela cidade. Em POST /cidades, clicamos em Try it out, informamos o nome e executamos.

O resultado esperado para um cadastro novo é 201. A resposta mostra o identificador gerado pelo banco. Fazemos isso com Maringá e Sarandi.

Agora executamos GET /cidades. O retorno 200 e os registros na lista confirmam a consulta. Vamos anotar o identificador de Sarandi para vincular a linha no próximo teste.

No código, Cidade tem uma chave primária. A linha vai usar esse identificador como chave estrangeira.”

**O que fazer na tela:**

1. Abrir POST /cidades → Try it out.
2. Enviar {"nome":"Maringá"} → Execute → conferir 201.
3. Enviar {"nome":"Sarandi"} → Execute → conferir 201.
4. Abrir GET /cidades → Try it out → Execute → conferir 200.
5. Anotar o id_cidade real de Sarandi. Não presumir um ID.

Se houver 409, esse cadastro já existe. Consulte o registro; não chame isso de falha da API. O ensaio deve ser preparado em um schema local novo.

## Bruno — 2:20 a 3:50 — Cadastrar linha e consultar o relacionamento

**Resumo:** Você faz POST /linhas com a cidade existente e GET /linhas. Troque o ID do exemplo pelo ID real anotado por Kauan.

**Fala:**

“Agora vamos cadastrar uma linha associada à cidade. Em POST /linhas, informamos o código, o nome e o identificador de Sarandi que acabamos de consultar.

Este exemplo usa a identificação de uma ligação publicada pelo DER do Paraná. Estamos demonstrando o cadastro, sem afirmar que a API representa todo o trajeto ou informa horários.

Para um cadastro novo, esperamos 201. Em seguida, executamos GET /linhas. A resposta deve trazer o código, o nome da linha e Sarandi no campo cidade.

O banco guarda o vínculo pelo ID, mas a API mostra o nome da cidade para facilitar a leitura.”

**O que fazer na tela:**

1. Abrir POST /linhas → Try it out.
2. Colar o JSON abaixo e TROCAR o número 2 pelo ID real de Sarandi:

{"codigo":"001.0254-410","nome":"Maringá - Sarandi (Jardim Independência L03)","id_cidade":2}

3. Execute → conferir 201 e cidade: Sarandi.
4. Abrir GET /linhas → Try it out → Execute → conferir 200 e o registro salvo.
5. Deixar o mesmo corpo de cadastro disponível para Gustavo testar a duplicidade.

Fonte da identificação: https://www.der.pr.gov.br/Pagina/Horarios-Vigentes . Associação a Sarandi para o cadastro da avaliação; não é modelagem completa de origem e destino.

## Gustavo — 3:50 a 6:20 — Erros esperados e testes automatizados

**Resumo:** Você demonstra 409, 404 e 422 no Swagger e executa a suíte completa. Esses erros são resultados esperados dos testes.

**Fala:**

“Agora vamos conferir as regras. Primeiro, repetimos exatamente a linha já cadastrada. O retorno esperado é 409, porque o código já existe nessa cidade.

Depois, enviamos uma linha com um identificador de cidade que não aparece na consulta. Esperamos 404. Com o identificador igual a zero, esperamos 422, porque o valor é inválido.

Esses retornos mostram que a API rejeita dados incorretos. Agora executamos a suíte completa. Ela também verifica cadastro, consulta, persistência, restrições do PostgreSQL e falha de banco sem expor senha.

Na execução que estamos mostrando, precisamos conferir o resultado final antes de anunciar quantos testes passaram.”

**O que fazer na tela:**

1. Em POST /linhas, repetir o JSON usado por Bruno, sem mudar código nem cidade → conferir 409.
2. Trocar somente id_cidade por 2147483647, após conferir que esse ID não está na lista → conferir 404.
3. Trocar id_cidade por 0 → conferir 422.
4. Em OUTRO terminal, dentro de backend, executar:

.\.venv\Scripts\python.exe -m pytest -v

5. Esperar terminar e apontar a linha final. Na revisão: 18 passed, 1 warning. Se esse for o resultado ao vivo, dizer: “Passaram os 18 testes, sem falhas. O aviso é de depreciação de uma dependência.”
6. Não anunciar aprovação se a execução falhar. Os testes usam schemas temporários no PostgreSQL local e não cadastram no Supabase.

## Ana Carolina — 6:20 a 8:25 — Persistência, site e encerramento

**Resumo:** Você confirma o registro após reiniciar a API, mostra busca e filtro no site e encerra. O reinício usa o MESMO schema do início.

**Fala:**

“Para finalizar, vamos confirmar a persistência. Paramos somente a API e iniciamos novamente usando o mesmo banco e o mesmo schema. Ao consultar as linhas, o registro deve continuar aparecendo.

Agora mostramos o site. Podemos buscar uma linha por código, nome ou cidade, filtrar pelo município e limpar os filtros. A interface também se adapta ao celular.

Com isso, demonstramos o fluxo completo: cadastro, consulta, relacionamento, rejeição de dados inválidos e persistência.

Os registros do Supabase ainda precisam ser conciliados com o catálogo oficial. Hoje entregamos a base funcional e os testes que acabamos de mostrar. Obrigada.”

**O que fazer na tela:**

1. No terminal da API, Ctrl+C. Não parar o PostgreSQL.
2. Executar novamente o MESMO comando usado na preparação, com o MESMO --schema.
3. Em GET /linhas, Execute → conferir o registro que Bruno cadastrou.
4. Abrir http://127.0.0.1:8001/site/.
5. Buscar 001.0254-410, mostrar o resultado, filtrar Sarandi e clicar em Limpar filtros.
6. Encerrar até 8min25s. Há 35s de margem até 9 minutos.

## Ordem dos resultados esperados

| Teste | Resultado esperado |
|---|---|
| POST de cidade nova | 201 e ID gerado |
| GET de cidades | 200 e cidades cadastradas |
| POST de linha com cidade existente | 201 e nome da cidade na resposta |
| GET de linhas | 200 e linha cadastrada |
| Repetir linha na mesma cidade | 409 |
| Cidade inexistente | 404 |
| id_cidade igual a zero | 422 |
| Reiniciar a API e consultar | Registro permanece |
| Suíte automatizada | Conferir o resultado real; referência: 18 aprovados |

O tempo depende do ensaio e das ferramentas. Se ocorrer uma falha real, informe a situação. Não apresente um resultado gravado como execução ao vivo.

Fonte da identificação de linha: https://www.der.pr.gov.br/Pagina/Horarios-Vigentes . As demais evidências vêm das requisições e dos testes executados no próprio projeto. A divisão das falas não atribui autoria individual do código.
