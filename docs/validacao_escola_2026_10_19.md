# Validação da entrega escolar — 19/10/2026

## API Python enviada

- Instaladas as versões fixadas em `backend_escola/requirements.txt` usando Python 3.12.14.
- Executado o teste fornecido: **1 teste de integração aprovado**, com verificações de POST/GET, nome relacionado, persistência, FK, 404 e 422. Uma advertência de depreciação do TestClient foi emitida.
- Iniciador Linux executado, configuração SQLite local criada em pasta de preparação separada e Uvicorn iniciado.
- GET `/`, `/docs`, `/openapi.json`, `/cidades` e `/linhas`: **200** em requisições HTTP locais.
- Os arquivos Python, as dependências e o teste enviado foram preservados; iniciador e documentação foram acrescentados separadamente.
- O iniciador foi testado novamente com ambiente já existente, sem recriar nem remover a venv.

Essa validação não usa o Supabase remoto nem o banco que está no computador da escola.

## Site V2 enviado

- Dependências instaladas com `npm ci`, preservando o lockfile e sua verificação de integridade.
- `npm test`: **10 testes aprovados**, zero falhas, zero ignorados. Inclui API, permissões, concorrência, HTTP local, renderização e cenários de apresentação.
- `npx --no-install tsc --noEmit`: aprovado.
- `npm run build`: aprovado.
- A compilação foi gerada localmente para validação; `dist` e `node_modules` não são incluídos no Git.

## Apresentações e revisão

- Preservados os dois conjuntos HTML/CSV/roteiros enviados e os slides PPTX V3.
- O navegador desta sessão bloqueou a abertura `file://` da apresentação (`ERR_BLOCKED_BY_ADMINISTRATOR`). Portanto a passagem visual e interativa no navegador da escola permanece pendente. Os testes de renderização aprovados não substituem essa passagem.
- O modo de apresentação mantém a identificação de dados, perfis, posições e tempos simulados.
- Aplicada busca por padrões comuns de credenciais nos arquivos de texto importados, sem imprimir valores; nenhum padrão revisável foi encontrado nessa busca. Isso não equivale a uma auditoria de segurança completa.
- `.env`, bancos locais, ambientes virtuais, caches e saídas de compilação foram excluídos do conjunto de origem para GitHub.

## Limitações

Não houve controle remoto nem instalação no computador da escola. Não houve envio ao Classroom, conexão remota com Supabase ou publicação do site em hospedagem. Os três componentes (API escolar, avaliação DS/IA e site V2) não compartilham automaticamente servidor, autenticação ou banco.

Os relatórios históricos dos arquivos enviados foram preservados. Resultados de 07/10 e 08/10 não são apresentados como execuções desta sessão.
