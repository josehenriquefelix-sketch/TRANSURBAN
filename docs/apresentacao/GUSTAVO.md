*GUSTAVO — SUA PARTE NO TRANSURBAN*

*Tempo: 3:50 a 6:20*

*Resumo:* Você demonstra 409, 404 e 422 no Swagger e executa a suíte completa. Esses erros são resultados esperados dos testes.

*Fala sugerida:*
Agora vamos conferir as regras. Primeiro, repetimos exatamente a linha já cadastrada. O retorno esperado é 409, porque o código já existe nessa cidade.

Depois, enviamos uma linha com um identificador de cidade que não aparece na consulta. Esperamos 404. Com o identificador igual a zero, esperamos 422, porque o valor é inválido.

Esses retornos mostram que a API rejeita dados incorretos. Agora executamos a suíte completa. Ela também verifica cadastro, consulta, persistência, restrições do PostgreSQL e falha de banco sem expor senha.

Na execução que estamos mostrando, precisamos conferir o resultado final antes de anunciar quantos testes passaram.

*O que você vai fazer e testar:*
1. Em POST /linhas, repetir o JSON usado por Bruno, sem mudar código nem cidade → conferir 409.
2. Trocar somente id_cidade por 2147483647, após conferir que esse ID não está na lista → conferir 404.
3. Trocar id_cidade por 0 → conferir 422.
4. Em OUTRO terminal, dentro de backend, executar:

.\.venv\Scripts\python.exe -m pytest -v

5. Esperar terminar e apontar a linha final. Na revisão: 18 passed, 1 warning. Se esse for o resultado ao vivo, dizer: “Passaram os 18 testes, sem falhas. O aviso é de depreciação de uma dependência.”
6. Não anunciar aprovação se a execução falhar. Os testes usam schemas temporários no PostgreSQL local e não cadastram no Supabase.

*Importante:* ensaio na porta 8001, banco local. As ações de tela fazem parte do seu tempo. Não leia as instruções em voz alta.
