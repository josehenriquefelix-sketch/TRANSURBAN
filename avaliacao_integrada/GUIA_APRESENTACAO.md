# TRANSURBAN — apresentação de DS + IA

Na pasta `avaliacao_integrada`, no Linux, execute `PORT=8092 bash iniciar_linux.sh` para usar o Supabase. Reaproveite `backend/.env` se ele já contém a URL e a chave secreta do Supabase. O iniciador cria um modelo caso o arquivo ainda não exista. A chave fica no backend local.

Para ensaiar sem credenciais, execute `PORT=8092 bash iniciar_linux.sh --demo`. A tela indica **ENSAIO LOCAL · SQLite, sem Supabase**. O modo de ensaio não comprova conexão com o Supabase. No Windows, para conectar ao Supabase, execute `set PORT=8092` seguido de `iniciar_local.cmd` no Prompt de Comando.

- Painel: http://127.0.0.1:8092/
- Swagger: http://127.0.0.1:8092/docs
- Verificação do banco: http://127.0.0.1:8092/health/banco

1. Abra **Cidades** e cadastre uma cidade de demonstração com nome único.
2. Abra **Linhas**, selecione a cidade pelo nome e cadastre uma linha de demonstração. Mostre na aba Rede que o POST envia `id_cidade`, e que a resposta devolve também o nome da cidade.
3. Consulte pelo ID, edite a linha e tente excluir a cidade vinculada. O banco deve bloquear com 409. Exclua apenas a linha fictícia e confira que a cidade permanece cadastrada.
4. No Supabase, confirme o registro e o vínculo usando o SELECT ao final de `database/05_preparar_crud.sql`. Execute a preparação somente se o esquema da equipe precisar dela; leia primeiro a auditoria em `database/01_auditar_esquema.sql`.

Esboço da demonstração: **menu → formulário de cidade e tabela → formulário de linha com seletor e tabela → Swagger**. Divisão sugerida: HTML (estrutura e campos), CSS (responsividade), JS (CRUD), backend (CORS, validação e Supabase). Revisem em conjunto o vínculo antes de apresentar.

Evidência: `docs/TESTES_AUTOMATICOS_20261109.txt` registra os testes locais da versão anterior. O navegador confirmou o cadastro de cidade e de linha vinculada no modo de ensaio. A confirmação desta versão no Supabase remoto depende da configuração privada do projeto.
