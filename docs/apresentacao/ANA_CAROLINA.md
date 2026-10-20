*ANA CAROLINA — SUA PARTE NO TRANSURBAN*

*Tempo: 6:20 a 8:25*

*Resumo:* Você confirma o registro após reiniciar a API, mostra busca e filtro no site e encerra. O reinício usa o MESMO schema do início.

*Fala sugerida:*
Para finalizar, vamos confirmar a persistência. Paramos somente a API e iniciamos novamente usando o mesmo banco e o mesmo schema. Ao consultar as linhas, o registro deve continuar aparecendo.

Agora mostramos o site. Podemos buscar uma linha por código, nome ou cidade, filtrar pelo município e limpar os filtros. A interface também se adapta ao celular.

Com isso, demonstramos o fluxo completo: cadastro, consulta, relacionamento, rejeição de dados inválidos e persistência.

Os registros do Supabase ainda precisam ser conciliados com o catálogo oficial. Hoje entregamos a base funcional e os testes que acabamos de mostrar. Obrigada.

*O que você vai fazer e testar:*
1. No terminal da API, Ctrl+C. Não parar o PostgreSQL.
2. Executar novamente o MESMO comando usado na preparação, com o MESMO --schema.
3. Em GET /linhas, Execute → conferir o registro que Bruno cadastrou.
4. Abrir http://127.0.0.1:8001/site/.
5. Buscar 001.0254-410, mostrar o resultado, filtrar Sarandi e clicar em Limpar filtros.
6. Encerrar até 8min25s. Há 35s de margem até 9 minutos.

*Importante:* ensaio na porta 8001, banco local. As ações de tela fazem parte do seu tempo. Não leia as instruções em voz alta.
