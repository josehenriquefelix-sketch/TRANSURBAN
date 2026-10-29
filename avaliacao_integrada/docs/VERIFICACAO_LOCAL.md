# Verificação local da entrega

Data da revisão: 28/10/2026.

- Sintaxe Python: `py_compile` aprovado para `backend/main.py`, `backend/database.py` e `backend/abrir_app.py`.
- Sintaxe JavaScript: `node --check frontend/app.js` aprovado.
- Integridade da interface: 31 referências estáticas do JavaScript apontam para IDs existentes; não há IDs duplicados.
- Inicialização: a aplicação serve interface, API e Swagger pela mesma origem local. No Windows, enquanto a API está ativa, ela solicita temporariamente que o sistema não suspenda; ao fechar a API, libera a solicitação.
- Pacote de transferência: inclui código, scripts, CSV e `.env.example`; não inclui o `.env` privado, `.venv`, logs nem cache.
- Testes automatizados: a execução nesta sessão do Windows não completou. O `TestClient` ficou bloqueado ao criar seu socket interno antes de obter resposta da aplicação. Por isso, esta revisão não declara uma execução visual validada no navegador.
- Nenhuma escrita de CRUD de demonstração foi enviada ao Supabase durante esta revisão. Use registros fictícios e confira os resultados no Table Editor durante o ensaio.
- A base do projeto é sintética e não representa a operação real do transporte.

A chave privada deve ficar somente em `backend/.env` no computador que executa a apresentação. Nunca a coloque no HTML/JavaScript, no arquivo `.env.example`, no ZIP compartilhado ou no GitHub.

