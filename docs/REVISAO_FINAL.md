# Revisão final — 20/10/2026

## Ajustes encontrados e corrigidos

| Encontrado | Correção |
|---|---|
| Swagger mostrava 404 e 409 como “Undocumented” | Respostas e modelo de erro declarados nos POSTs |
| Nome ou código contendo apenas espaços passava pelo tamanho mínimo | Entrada remove espaços nas pontas antes da validação |
| README dizia que Paiçandu ainda não havia sido cadastrada | Estado do ensaio atualizado; Marialva reservada como opção real para demonstração |
| Fontes descreviam somente as três primeiras linhas | Acrescentadas a linha de Paiçandu e as fontes do próximo exemplo |

## Verificações executadas nesta revisão

- 10 chamadas HTTP na etapa de cidades, em schema isolado de PostgreSQL local.
- 11 chamadas HTTP na etapa de linhas, incluindo cadastro, consulta, duplicidade, campos inválidos, FK e nome relacionado.
- 6 chamadas HTTP usando o Supabase, com comparação dos IDs e nomes por SQL.
- 9 chamadas HTTP contra a execução final, incluindo OpenAPI, dados atuais, 404, 409 e 422.
- Confirmação direta no banco: três cidades, quatro linhas e FK para Cidade; registros inválidos não acrescentaram linhas.
- `pip check` sem dependências incompatíveis; revisão de diferenças do Git sem erros de espaços.
- `.env`, `.venv` e `__pycache__` ignorados pelo Git.

Total: 36 chamadas HTTP aprovadas, além da conferência SQL e da verificação visual no Swagger. As respostas 404, 409 e 422 são resultados esperados dos testes de rejeição.

## Estado para apresentação

A execução revisada usa http://127.0.0.1:8091/docs. A execução anterior em 8090 não tem as últimas correções de documentação.

O schema `transurban_caderno` contém Maringá, Sarandi e Paiçandu e quatro linhas reais. Marialva e a linha 001.0224-400 ainda não estavam cadastradas quando esta revisão foi executada. A proposta de demonstração usa esse exemplo com fontes oficiais, sem apagar os dados do ensaio.

As evidências de cada etapa estão em `evidencias/resultado_cidade.json`, `resultado_linha.json`, `resultado_supabase.json` e `revisao_final.json`. As contagens são um retrato da revisão e podem aumentar na apresentação.

O servidor depende da conexão com o Supabase. O roteiro inclui a sequência de início e encerramento e distingue uma demonstração ao vivo de evidências previamente salvas. Os testes aprovados cobrem os fluxos descritos; não representam garantia de ausência de qualquer falha em todas as condições possíveis.
