# Verificação da entrega — 06/11/2026

- Os seis testes automatizados com banco em memória passaram: CRUD de cidade e linha, FK com exclusão bloqueada, entradas inválidas, análise e CORS.
- Foram aprovadas 37 verificações de integração usando a aplicação FastAPI e o Supabase real por HTTPS. O relatório [EVIDENCIAS_FK_20261106.json](EVIDENCIAS_FK_20261106.json) registra método, rota e status esperado/recebido.
- Foram testados dois registros filhos ligados à mesma cidade, consulta do nome atual da cidade após renomeá-la, reassociação por PUT, FK inexistente (400), campos inválidos/extra (422), registro inexistente (404), exclusão de cidade referenciada (409) e exclusões válidas (204).
- Todos os registros temporários criados nesta conferência foram removidos, e os IDs removidos retornaram 404.
- Interface, CSS, JavaScript, Swagger e OpenAPI responderam HTTP 200; os IDs HTML são únicos e as referências estáticas do JavaScript correspondem a elementos existentes. A sintaxe JavaScript passou em `node --check frontend/app.js`.
- Esta evidência de interface é estrutural e HTTP; não equivale a uma inspeção visual ou a cliques automatizados no navegador. As capturas do Swagger/Table Editor e o ensaio no computador da escola devem compor a apresentação da equipe.
- O iniciador mantém o servidor ativo no mesmo console; mantenha a janela aberta durante a apresentação.
- A cópia local `backend/.env` é privada e precisa ser configurada em cada computador. Ela, o ambiente virtual, caches e logs ficam fora do GitHub e dos pacotes compartilhados.
- A base CSV é sintética. Os nomes dos integrantes e a validação coletiva do esboço devem ser preenchidos/realizados pela equipe.

