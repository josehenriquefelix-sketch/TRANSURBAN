# Ferramentas do desenvolvedor

Esta pasta é para consulta no computador de quem desenvolve o TRANSURBAN. Ela não é servida pelo site e não aparece na Gestão.

- Abra `estrutura_banco.html` para ver os metadados conferidos do banco.
- Os scripts SQL estão em `database/` e a explicação das tabelas em `docs/BANCO_CONFERIDO.md`.
- Para conferir os registros e a estrutura atual, entre no projeto da equipe pelo painel do Supabase.
- A API administrativa de metadados continua protegida por conta administrativa. Ela não retorna os registros de usuários.

O banco real continua sendo PostgreSQL no Supabase. Estes arquivos locais não transferem nem substituem o banco.

O exercício escolar de materiais e ordens permanece isolado em `/estudo/materiais.html`, com autenticação administrativa. Não faz parte da navegação de Passageiro, Motorista ou Gestão.
