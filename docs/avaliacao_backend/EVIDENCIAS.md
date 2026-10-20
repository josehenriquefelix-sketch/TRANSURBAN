# Evidências de verificação

Data: 20/10/2026. Ambiente Windows, Python 3.13.15, PostgreSQL 17.11 e dependências registradas nos locks. Resultados de arquivos antigos não foram reaproveitados como comprovação.

## Implementado e testado

A suíte foi executada na .venv de backend da entrega. Resultado: **18 passed**. O arquivo evidencias/testes.txt registra o comando e os casos; evidencias/pytest.xml registra o resultado estruturado. pip check: No broken requirements found.

Foram verificados POST e GET das duas entidades, IDs gerados pelo banco, saída da linha com nome de cidade, FK real PostgreSQL, cidade inexistente com 404, dados inválidos com 422, duplicidade com 409, rollback após conflito, código igual permitido em outra cidade, outra sessão/conexão lendo a gravação e resposta 503 sem divulgar detalhes do driver.

Um aviso de descontinuação vem da biblioteca Starlette TestClient usando um alias do AnyIO. Não é falha de teste. A execução normal da API e do site funcionou. As versões efetivamente utilizadas estão fixadas nos arquivos lock.

No navegador, foram realizados cadastro de Maringá, cadastro de linha TESTE-001, consulta com cidade por nome, duplicidade de Maringá, cadastro de Sarandi e atualização das tabelas. O console consultado não apresentou erros de JavaScript. A captura evidencias/site.png mostra 2 cidades e 1 linha no banco local. O ID de Sarandi é 3 porque a tentativa duplicada consumiu um valor da sequência; IDs automáticos não precisam ser contínuos.

## Supabase real

O painel do projeto informado pelo usuário foi acessado após autenticação feita por ele. A auditoria mostrou PKs identity nas duas tabelas, FK válida e unicidades já existentes. Não foi necessário migrar IDs.

Divergência encontrada: linha_onibus.nome estava definido como VARCHAR(150), enquanto docs/dicionario_dados.md define VARCHAR(120). Antes da alteração havia 6 cidades e 4 linhas; maior nome de linha: 30 caracteres; linhas sem cidade: zero.

Após autorização do usuário para resolver problemas no Supabase, foi aplicada em transação a alteração para VARCHAR(120), com lock_timeout de 3 segundos e sem conversão que truncasse texto. O resultado confirmou limite 120, mesmos 6 registros de cidades e 4 de linhas e nenhuma linha órfã. Os objetos JSON observados antes/depois preservam os mesmos valores de todos os registros dessas duas tabelas.

Arquivos: evidencias/supabase_antes.json, supabase_depois.json, supabase_migracao.sql e supabase_depois.png. A cópia dessas duas tabelas é evidência de preservação do recorte; não é um backup completo do projeto Supabase.

## Preparação e limitações

As primeiras tentativas de inicializar/conectar ao PostgreSQL local aconteceram antes da extração completa e depois encontraram o processo encerrado ao final do comando de inicialização. Foram corrigidas mantendo o servidor em sessão ativa; as verificações completas posteriores passaram. A organização do runtime local exigiu parar e reiniciar os processos. A verificação HTTP final confirma os dados após esse reinício.

A suíte automatizada foi testada contra PostgreSQL local. Após o usuário salvar a configuração privada, a API foi reiniciada e conectou-se ao Supabase. GET /cidades retornou 6 cidades e GET /linhas retornou 4 linhas, ambos com HTTP 200. As respostas coincidiram integralmente com SELECTs diretos ao Supabase. Esta verificação externa foi somente de leitura; os testes positivos de POST, validações, FK e persistência continuam comprovados na suíte local, sem apresentar isso como novos cadastros no Supabase.

O VS Code foi aberto com o workspace correto; .env e .venv foram vistos no Explorer. A confiança foi confirmada manualmente pelo usuário. Após aviso inicial de interpretador, foi selecionada explicitamente a .venv (3.13.15) do backend; a barra de problemas mostrou zero problemas no main.py aberto. Não confunda a configuração entregue com uma execução de depuração já comprovada pelo editor.

O frontend anterior com Flask/Ollama foi preservado em frontend/historico. Não é a página ativa desta avaliação; as funcionalidades de IA/atrasos não fazem parte da API do caderno. A página ativa implementa cidades e linhas.

## Pendências reais

- Publicação no GitHub: não executada por restrição explícita do usuário. O código é entregue localmente; push exige autorização.
- Apresentação individual: estudante deve executar o roteiro e explicar os conceitos do checklist. A geração de código não comprova aprendizagem individual.

Não há declaração de ausência absoluta de erros. Estas evidências cobrem os fluxos efetivamente verificados.

## Verificação HTTP após reinício

O utilitário backend/verificar_http.py aprovou 12 checagens e salvou respostas reais em evidencias/http.json. GET /cidades preservou Maringá (1) e Sarandi (3); GET /linhas preservou a linha TESTE-001 ligada a Maringá. Foram testados também os arquivos da página, o favicon, /docs, /openapi.json e entradas com 404/422.

O utilitário configurar_supabase.py foi compilado/verificado. Após a configuração privada pelo usuário, a conexão real foi confirmada sem imprimir a senha. TEST_DATABASE_URL permaneceu apontando para PostgreSQL local.

## Conexão final ao Supabase concluída

Evidências: supabase_conexao_api.json registra conexão, contagens, limite 120 e ausência de linhas órfãs; http_supabase.json registra HTTP 200 e a comparação com SELECTs; site_supabase.png mostra o site com Banco conectado, 6 cidades e 4 linhas. Nenhum registro foi criado, alterado ou excluído nesta verificação de conexão. A API mantém o título TRANSURBAN - API. A senha não foi incluída nas evidências, no Git ou no ZIP.
