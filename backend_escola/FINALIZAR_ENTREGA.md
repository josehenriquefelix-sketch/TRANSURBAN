# Entrega DS + IA — API escolar integrada

A versão 1.1 reúne cadastro, consulta, análise do CSV e dashboard no mesmo servidor. Execute `bash iniciar-linux.sh` na pasta `backend_escola`. Não é necessário iniciar o Vite para usar esse dashboard.

## Atualizar a cópia recuperada da escola

Pare somente o servidor da API com Ctrl+C no terminal correspondente. Na cópia baixada nesta preparação:

```bash
cd "$HOME/TRANSURBAN-recuperado"
git pull --ff-only
cd backend_escola
bash iniciar-linux.sh
```

Se o Git informar alterações locais, pare e revise; não use reset, clean ou force. O `.env`, a venv e `transurban_escola.db` são locais, ficam fora da atualização versionada e são preservados pelo iniciador. Após a inicialização, abra no mesmo computador:

- `http://127.0.0.1:8000/painel/`: dashboard, cadastros e qualidade da fonte.
- `http://127.0.0.1:8000/docs`: demonstração de DS e IA no Swagger.
- `http://127.0.0.1:8000/health`: conexão identificada como SQLite local ou PostgreSQL.

## Demonstrar IA aos professores

Execute GET `/ia/qualidade`, `/ia/resumo`, `/ia/agrupamentos/linha` e `/ia/agrupamentos/data`. Cada resposta deve retornar 200 com JSON. O CSV incluído tem 180 observações válidas, soma de 1.362 minutos, média de 7,5667 minutos, mediana de 8 e máximo de 12 minutos.

Cada registro é uma observação por trecho/data/linha, não uma viagem completa. Os dados são sintéticos, e a soma não representa tempo perdido por passageiros. Os agrupamentos descrevem associações, não causalidade. Cadastros DS e o CSV são fontes independentes.

Para demonstrar a análise antes da API:

```bash
./.venv-escola/bin/python analise.py
```

Perguntas autorais: qual é o atraso típico, quais linhas apresentam maiores médias e como os atrasos variam por data? O dashboard oferece os indicadores e gráficos correspondentes. O dicionário e a interpretação completos estão em `../avaliacao_backend/docs/IA_E_DASHBOARD.md`.

## Testes e evidências automáticas

```bash
bash iniciar-linux.sh --testar
bash iniciar-linux.sh --evidencias
```

O segundo comando inicia e encerra seu próprio servidor, usa SQLite temporário, faz 16 requisições e salva um diretório novo em `evidencias/`, com resumo, linhas, datas, qualidade e respostas HTTP. Ele não usa a conexão Supabase nem o banco dos cadastros da demonstração. Não substitui capturas manuais nem comprova o banco remoto.

O workflow `.github/workflows/escola-ds-ia.yml` executa os testes e produz um artefato de evidências no GitHub Actions. Uma execução local não comprova uma execução CI.

## Concluir Supabase privadamente

Não há DATABASE_URL privada do Supabase disponível nesta preparação. O link do painel não permite conectar ao banco. No computador da escola, obtenha a URI no painel **Connect** e execute:

```bash
bash iniciar-linux.sh --supabase
```

Cole a URI completa na entrada oculta do terminal; não a cole na conversa nem mostre esse terminal durante a apresentação. Use senha do banco codificada, não chave anon. Preserve usuário, host, porta e banco do método informado pelo painel. O código mantém TLS e rejeita modos que o desativam; configurações verify-ca e verify-full são preservadas.

O assistente faz somente leituras para conferir conexão, campos, tipos, tamanhos, obrigatoriedade, PK, geração de IDs e FK. Não cria nem migra tabelas remotas. Se a auditoria falhar, o `.env` não é substituído e a URI não é impressa. Se passar, preserva as outras variáveis e faz backup privado do `.env` anterior em `.env-backups/` antes de salvar.

DATABASE_URL exportada no terminal tem prioridade sobre `.env`; atualize essa configuração privada antes de reiniciar. Reinicie a API, confira `/health` com `postgresql`, cadastre cidade e linha em banco autorizado para testes e confira os mesmos IDs no Table Editor. Só depois registrem a persistência remota como comprovada. O esquema escolar requer capacidade de 150 caracteres para o nome da linha e geração de IDs. Incompatibilidades precisam de revisão separada, sem apagar tabelas automaticamente.

## Frontend da escola: estado observado

As capturas confirmam carregamento do frontend React/Vite, escolha de embarque/destino, mapa com pontos ilustrativos, detalhes, avanço manual até 100%, encerramento e confirmação de avaliação de demonstração. A avaliação exibiu nota 5/5, lotação Normal e comentário “22”. O aviso opcional de chegada estava desmarcado na captura final e não foi confirmado. GPS, previsões e avaliações dessas telas são simulados, sem gravação no banco.

O código desse `frontend-app` não está nas branches remotas conferidas em 19/10 e é diferente de `site_v2`. Motorista, passe e versionamento dessa versão dependem dos arquivos locais. Para revisão, forneça a pasta compactada com `src`, `public`, `index.html`, `package.json`, `package-lock.json` e `vite.config.js`, excluindo `.env`, `.git`, `node_modules` e `dist`. Não atribuímos a esse código os testes do site V2.

## Classroom e apresentação

Inclua o link da branch, código, JSONs e capturas de rota/status/resposta. O roteiro atual, sem slides, está em `../apresentacoes/ROTEIRO_API_SEM_SLIDES_20_10.md`, com os sete integrantes confirmados. O modelo brModelo do recorte anterior fica em `../avaliacao_backend/modelagem/TRANSURBAN_Cidade_Linha.brM3`; o nome de linha naquele pacote tem limite de 100 caracteres, enquanto esta API escolar usa 150. Para explicar o esquema atual, mostre `models.py` desta pasta. A atuação individual deve corresponder ao trabalho real de cada pessoa.

Não há acesso autenticado ao Classroom nesta sessão e não foi realizado envio. Publicar no GitHub não envia a atividade nem instala a atualização no computador da escola.
