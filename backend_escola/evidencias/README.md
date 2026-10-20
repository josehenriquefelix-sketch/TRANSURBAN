# Evidências da API no computador da escola

Em 19/10/2026, o usuário iniciou a API no computador da escola e compartilhou as respostas do Swagger na conversa de preparação. O JSON `testes-escola-2026-10-19.json` registra essas respostas e sua procedência.

| Operação | Resultado informado |
|---|---|
| Cadastrar Maringá | 201, id_cidade 1 |
| Cadastrar linha 001 com id_cidade 1 | 201, nome relacionado Maringá |
| Consultar linhas | 200, linha cadastrada presente |
| Cadastrar linha com cidade 999999 | 404, Cidade não encontrada |
| Consultar depois da tentativa inválida | 200, somente a linha válida |
| Cadastrar cidade com nome de espaços | 422, string_too_short |
| Consultas finais de cidades e linhas | 200, registros preservados |

Esses resultados demonstram cadastro, consulta, relacionamento e rejeição das entradas testadas. A conexão Supabase e o reinício do processo não foram comprovados por essas respostas. O JSON é uma transcrição das evidências enviadas, não uma execução remota feita pelo agente.

O teste automatizado fornecido e executado na preparação é separado dessas verificações manuais. Veja `../../docs/validacao_escola_2026_10_19.md` a partir desta pasta, ou o relatório na pasta `docs` da raiz do repositório. Capturas reais de rota, status e resposta podem ser acrescentadas pela equipe; não incluam `.env` nem credenciais.
