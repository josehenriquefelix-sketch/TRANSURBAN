# Conectar ao Supabase

1. Em backend/.env, preencha SUPABASE_URL (Project URL HTTPS, sem /rest/v1) e SUPABASE_KEY (chave secreta ou service_role do mesmo projeto). DATABASE_URL não substitui essas variáveis.
2. Rode database/01_auditar_esquema.sql no SQL Editor. Se faltarem tabelas ou a chave estrangeira, revise e execute database/05_preparar_crud.sql. Se não houver geração automática de IDs, revise database/04_ids_automaticos_existentes.sql.
3. Execute database/06_mobilidade_supabase.sql para instalar avaliações e GPS.
4. Inicie com PORT=8092 bash iniciar_linux.sh, sem --demo. Confira /health/banco e /health/mobilidade: devem mostrar conectado=true e modo=supabase.
5. Confira as consultas no Swagger e a gravação de um registro fictício no Table Editor. Para GPS físico, configure o código do motorista e HTTPS conforme GUIA_MOBILIDADE.md.

O .env fica privado. Não publique credenciais nem copie a chave para o frontend.
