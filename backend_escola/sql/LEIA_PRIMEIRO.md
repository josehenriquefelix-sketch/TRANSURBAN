# Supabase: somente o necessário para a API escolar

Projeto informado pelo usuário: `lsnpvokfnvyjkvqzkvof`. Os scripts foram preparados para revisão; não foram executados nesse projeto nesta sessão.

As instruções SQL passaram por análise estática de sintaxe PostgreSQL com pglast. Isso não verifica o conteúdo do projeto remoto nem substitui a auditoria ou um teste real de execução. O bloco procedural de permissões também precisa ser executado em banco de testes autorizado antes de ser apresentado como comprovado.

## Estrutura esperada

| Tabela | Campo | Tipo | Regra |
|---|---|---|---|
| cidade | id_cidade | INTEGER | PK com geração automática |
| cidade | nome | VARCHAR(100) | Obrigatório |
| linha_onibus | id_linha | INTEGER | PK com geração automática |
| linha_onibus | id_cidade | INTEGER | FK obrigatória para cidade.id_cidade |
| linha_onibus | codigo | VARCHAR(20) | Obrigatório; texto preserva zeros à esquerda |
| linha_onibus | nome | VARCHAR(150) | Obrigatório |

Essas regras correspondem a `backend_escola/models.py`. Esta versão não declara unicidade de nome da cidade ou código da linha. Não invente uma restrição de duplicidade na apresentação. As outras tabelas do projeto não precisam ser removidas para demonstrar este recorte.

## Ordem correta

1. Abra o projeto correto no Supabase e execute **somente `01_auditar_supabase.sql`** no SQL Editor. São consultas de leitura sobre campos, PK/FK, geração de IDs, RLS e permissões.
2. Se as tabelas já existem, compare o resultado com a estrutura acima. Não execute o script de criação sobre elas. Diferenças precisam de revisão com base na saída real da auditoria; não fornecemos uma migração genérica que presume o conteúdo do banco.
3. Se as duas tabelas estão ausentes e o banco de testes está autorizado, `02_criar_em_banco_novo.sql` cria somente esse recorte em transação. Se alguma tabela existir, a transação falha. O script não contém DROP, TRUNCATE ou remoção de registros.
4. O script de criação mantém RLS habilitado e não cria políticas públicas. O backend usa conexão PostgreSQL privada com um papel autorizado para consulta, inserção e uso das sequências. Não use a chave anon ou service_role como senha de PostgreSQL nem exponha a URI no frontend.
5. Depois de conferir a compatibilidade, `03_cidades_essenciais_opcional.sql` pode acrescentar Maringá e Sarandi em banco autorizado para escrita. Ele preserva as cidades existentes e não semeia ônibus, horários ou viagens fictícias como dados operacionais.
6. No terminal privado da escola, execute `bash iniciar-linux.sh --supabase`, informe a URI do painel Connect em entrada oculta e deixe o assistente auditar antes de salvar o `.env`. Reinicie a API.
7. Confira `/health` com banco `postgresql`, faça POST/GET em banco de testes e compare os IDs com o Table Editor. Somente então registrem persistência no Supabase como verificada.

Nenhum script conecta automaticamente o site V2 ou o frontend local à API escolar. As rotas de IA continuam lendo o CSV sintético; não exigem importar as 180 observações para o Supabase.

Se compartilhar a saída da auditoria, envie somente as tabelas de metadados; não envie senha, URI privada ou `.env`. A configuração privada do banco é o requisito externo que ainda falta para o agente verificar o projeto remoto.
