# TRANSURBAN — apresentação de DS + IA

Na pasta `avaliacao_integrada`, no Linux, execute `bash iniciar_linux.sh` para usar o Supabase. Reaproveite `backend/.env` se ele já contém a URL e a chave secreta do Supabase. O iniciador cria um modelo caso o arquivo ainda não exista. A chave fica no backend local.

Para ensaiar sem credenciais, execute `bash iniciar_linux.sh --demo`. A tela indica **ENSAIO LOCAL · SQLite, sem Supabase**. O modo de ensaio não comprova conexão com o Supabase. No Windows, para conectar ao Supabase, execute `iniciar_local.cmd`.

- Painel: http://127.0.0.1:8091/
- Swagger: http://127.0.0.1:8091/docs
- Verificação do banco: http://127.0.0.1:8091/health/banco

1. Abra **Cidades** e cadastre uma cidade de demonstração com nome único.
2. Abra **Linhas**, selecione a cidade pelo nome e cadastre uma linha de demonstração. Mostre na aba Rede que o POST envia `id_cidade`, e que a resposta devolve também o nome da cidade.
3. Consulte pelo ID, edite a linha e tente excluir a cidade vinculada. O banco deve bloquear com 409. Exclua apenas a linha fictícia e confira que a cidade permanece cadastrada.
4. Mostre o painel: são 180 observações sintéticas, com atraso médio de 7,57 min e total de 1.362 min. Os quatro gráficos Chart.js usam os resultados da API por cidade, período, trânsito e clima.
5. No Supabase, confirme o registro e o vínculo usando o SELECT ao final de `database/05_preparar_crud.sql`. Execute a preparação somente se o esquema da equipe precisar dela; leia primeiro a auditoria em `database/01_auditar_esquema.sql`.

Esboço da demonstração: **menu → painel com indicadores e gráficos → formulário de cidade e tabela → formulário de linha com seletor e tabela → Swagger**. Divisão sugerida: HTML (estrutura e campos), CSS (responsividade), JS (CRUD e gráficos), backend (CORS, validação e Supabase). Revisem em conjunto os números e o vínculo antes de apresentar.

Evidência: `docs/TESTES_AUTOMATICOS_20261109.txt` registra 10 testes locais. O navegador confirmou o cadastro de cidade e de linha vinculada no modo de ensaio. A confirmação desta versão no Supabase remoto depende da configuração privada do projeto.
