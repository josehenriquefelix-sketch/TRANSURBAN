# Verificação local da entrega

Data da verificação: 28/10/2026.

- Testes automatizados: `python -m unittest discover -s tests -v` — 5 testes aprovados (CRUD de cidade, CRUD de linha com FK, validações Pydantic, CORS local e quatro totalizações).
- JavaScript: `node --check frontend/app.js` — sintaxe aprovada.
- Dependências: `pip check` — nenhuma dependência quebrada.
- Ciência de Dados: os valores conferidos com o CSV estão em `BASE_E_PERGUNTAS.md`; os testes usam a base entregue.
- Limite da verificação: não foram executadas chamadas contra o Supabase da equipe nem foram capturadas evidências do Swagger/Table Editor. O pacote não contém `SUPABASE_URL` ou chave real. Os testes CRUD usam armazenamento em memória e não alteram banco remoto. Antes da apresentação, preencher `backend/.env` localmente e executar o roteiro do README no projeto correto.
- Origem: CSV sintético para exercício, não dados operacionais reais.

