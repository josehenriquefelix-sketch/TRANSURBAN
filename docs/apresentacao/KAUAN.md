*KAUAN — SUA PARTE NO TRANSURBAN*

*Tempo: 1:20 a 2:20*

*Resumo:* Você faz POST /cidades e GET /cidades. Explique que o ID é gerado pelo banco e anote o ID real de Sarandi.

*Fala sugerida:*
Vamos começar pela cidade. Em POST /cidades, clicamos em Try it out, informamos o nome e executamos.

O resultado esperado para um cadastro novo é 201. A resposta mostra o identificador gerado pelo banco. Fazemos isso com Maringá e Sarandi.

Agora executamos GET /cidades. O retorno 200 e os registros na lista confirmam a consulta. Vamos anotar o identificador de Sarandi para vincular a linha no próximo teste.

No código, Cidade tem uma chave primária. A linha vai usar esse identificador como chave estrangeira.

*O que você vai fazer e testar:*
1. Abrir POST /cidades → Try it out.
2. Enviar {"nome":"Maringá"} → Execute → conferir 201.
3. Enviar {"nome":"Sarandi"} → Execute → conferir 201.
4. Abrir GET /cidades → Try it out → Execute → conferir 200.
5. Anotar o id_cidade real de Sarandi. Não presumir um ID.

Se houver 409, esse cadastro já existe. Consulte o registro; não chame isso de falha da API. O ensaio deve ser preparado em um schema local novo.

*Importante:* ensaio na porta 8001, banco local. As ações de tela fazem parte do seu tempo. Não leia as instruções em voz alta.
