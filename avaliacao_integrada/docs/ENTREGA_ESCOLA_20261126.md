# Conferência para usar na escola

Conferência realizada em 26/11/2026 para a apresentação de 27/11/2026.

Foi baixada uma cópia nova do GitHub, no commit de código `017295e`. Em um ambiente virtual novo, no Windows com Python 3.13, a instalação de `backend/requirements.txt` terminou e `pip check` não encontrou incompatibilidades. Os 62 testes Python passaram nessa cópia. Os 47 testes JavaScript também passaram na árvore de trabalho com o mesmo código. As alterações posteriores desta entrega são documentos e nomes da equipe, sem alteração do código da aplicação.

Na cópia nova, foi iniciado um servidor separado para conferir os três painéis, as duas documentações de API, o catálogo, a entrada de recuperação e o banner: todas as oito consultas retornaram HTTP 200. Foram testados login e logout nos três papéis com a conta privada já autorizada. As 12 tabelas da aplicação responderam HTTP 200 a consultas de leitura com limite zero, sem retornar registros de pessoas.

O `.env` foi copiado temporariamente para essa conferência, permaneceu ignorado pelo Git e foi removido da cópia de teste ao terminar. A tentativa de acessá-lo pela API retornou 404. O arquivo real do projeto de trabalho continua privado, fora do GitHub.

## Arquivos para levar

- Guia direto na raiz: `COMECE_AQUI_ESCOLA.txt`.
- Falas: `docs/ROTEIRO_TRANSURBAN_SEM_SLIDES.docx` e `docs/ROTEIRO_APRESENTACAO.md`.
- Banner com nome corrigido: `docs/BANNER_TRANSURBAN_ORIGINAL_90x120cm_KAUAN_CELSO.pdf`.
- Resultados: `docs/VALIDACAO_ESCOLA_20261126.json`.
- Versões instaladas: `docs/DEPENDENCIAS_TESTADAS_WINDOWS_20261126.txt`. É um registro da instalação neste Windows, não substitui o requirements multiplataforma.

## Procedimento na escola

Baixar o GitHub pelo VS Code, abrir `avaliacao_integrada`, copiar o `.env` real para `backend` e executar `iniciar_local.cmd`. Manter o terminal aberto. Em outro terminal, executar `VERIFICAR_TRANSURBAN.cmd` e conferir pessoalmente os três acessos com as contas já autorizadas. O banco já existe no Supabase; não executar scripts de criação novamente.

## Limites confirmados

A rede, as permissões e os programas do computador da escola não foram testados à distância. O resultado valida a instalação neste Windows. GPS físico, entrega de novos e-mails e uma troca real de senha pessoal não foram realizados nesta conferência. Avisos por SMTP próprio ainda dependem de configuração. A base de Ciência de Dados é sintética. Não há integração oficial com telemetria, pagamento ou bilhetagem da operadora. O catálogo completo municipal atual de Sarandi ainda não foi confirmado.

O roteiro identifica José, Bruno, Kauan Celso, Ana Carolina e Gustavo nessa ordem. A apresentação é feita no site, sem slides. Vídeos anteriores não foram narrados novamente nesta etapa e podem conservar a pronúncia anterior do nome; o roteiro e o banner corrigidos são as referências atuais da equipe.
