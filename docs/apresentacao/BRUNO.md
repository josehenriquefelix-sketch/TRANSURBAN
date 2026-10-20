*BRUNO — SUA PARTE NO TRANSURBAN*

*Tempo: 2:20 a 3:50*

*Resumo:* Você faz POST /linhas com a cidade existente e GET /linhas. Troque o ID do exemplo pelo ID real anotado por Kauan.

*Fala sugerida:*
Agora vamos cadastrar uma linha associada à cidade. Em POST /linhas, informamos o código, o nome e o identificador de Sarandi que acabamos de consultar.

Este exemplo usa a identificação de uma ligação publicada pelo DER do Paraná. Estamos demonstrando o cadastro, sem afirmar que a API representa todo o trajeto ou informa horários.

Para um cadastro novo, esperamos 201. Em seguida, executamos GET /linhas. A resposta deve trazer o código, o nome da linha e Sarandi no campo cidade.

O banco guarda o vínculo pelo ID, mas a API mostra o nome da cidade para facilitar a leitura.

*O que você vai fazer e testar:*
1. Abrir POST /linhas → Try it out.
2. Colar o JSON abaixo e TROCAR o número 2 pelo ID real de Sarandi:

{"codigo":"001.0254-410","nome":"Maringá - Sarandi (Jardim Independência L03)","id_cidade":2}

3. Execute → conferir 201 e cidade: Sarandi.
4. Abrir GET /linhas → Try it out → Execute → conferir 200 e o registro salvo.
5. Deixar o mesmo corpo de cadastro disponível para Gustavo testar a duplicidade.

Fonte da identificação: https://www.der.pr.gov.br/Pagina/Horarios-Vigentes . Associação a Sarandi para o cadastro da avaliação; não é modelagem completa de origem e destino.

*Importante:* ensaio na porta 8001, banco local. As ações de tela fazem parte do seu tempo. Não leia as instruções em voz alta.
