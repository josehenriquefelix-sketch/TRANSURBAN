# TRANSURBAN — entrega para a escola e apresentação de 20/10/2026

Os pacotes enviados foram organizados sem substituir o backend antigo nem os arquivos privados do computador da escola. A entrega anterior de frontend/API também foi incorporada ao histórico desta branch.

| Pasta | Conteúdo | Como abrir |
|---|---|---|
| `backend_escola/` | API Python enviada em `TRANSURBAN_BACKEND.zip`, com iniciador Linux | Na pasta, execute `bash iniciar-linux.sh`; depois abra `/docs` no servidor local |
| `avaliacao_backend/` | Avaliação DS + IA, CSV, dashboard e modelo brModelo da entrega anterior | Siga `avaliacao_backend/docs/FRONTEND.md` |
| `site_v2/` | Código-fonte do site V2 enviado, catálogo e testes | Node.js >=22.13, `npm ci`, `npm test`, `npm run preview:local` |
| `apresentacoes/terca-20-10/` | Demonstração offline e roteiro de terça-feira | Abra `01-ABRIR-APRESENTACAO.html` no navegador |
| `apresentacoes/equipe/` | Demonstração e falas individuais da equipe | Veja `02-COMECE-AQUI.txt` e a pasta `integrantes/` |
| `apresentacoes/TRANSURBAN_Apresentacao_Profissional_V3.pptx` | Slides enviados pelo usuário | Abra no PowerPoint ou LibreOffice Impress |

## API Python no Linux da escola

Em uma cópia desta branch, abra a pasta `backend_escola` no VS Code. No terminal:

```bash
bash iniciar-linux.sh
```

O script usa `.venv-escola`, evitando o conflito com o arquivo `.venv` identificado anteriormente. Preserva a configuração de banco existente e cria configuração SQLite local somente se não houver `.env` nem variável DATABASE_URL. Não importa nem apaga registros do backend antigo. Não precisa ativar manualmente a venv.

Deixe o terminal aberto depois de `Application startup complete`. No navegador do mesmo computador, abra `http://127.0.0.1:8000/docs`. Se já houver um servidor seu nessa porta, encerre-o com Ctrl+C no terminal correspondente antes de iniciar o novo.

Para executar o teste existente em banco descartável:

```bash
bash iniciar-linux.sh --testar
```

## O que permanece separado

A API escolar, o dashboard DS/IA e o site V2 são componentes distintos. O site V2 não foi automaticamente ligado à API Python nem ao Supabase; ele tem regras de servidor e persistência próprias. Não inicie os componentes imaginando que compartilham o mesmo banco ou login.

A apresentação offline é uma demonstração: seus passageiros, motoristas, posições e tempos são fictícios. O catálogo de 84 linhas é pesquisado em fontes secundárias e não garante cobertura integral ou operação atual. A fonte de atrasos de DS/IA é sintética. Não há integração oficial com operadoras nem previsão operacional de chegada validada.

## Versionamento e privacidade

Código-fonte, apresentações, catálogos, migrações e documentação foram organizados para GitHub. Dependências instaladas, `.env`, bancos locais, caches e compilação `dist` não são necessários no versionamento e foram excluídos da entrega de origem. Os ZIPs foram extraídos em pastas próprias; os pacotes originais enviados não foram modificados.

Publicar arquivos no GitHub não instala nada no computador da escola, não envia ao Classroom e não publica o site em produção. A validação do Supabase remoto continua pendente de acesso/configuração privada. Nunca envie senha ou string de conexão em mensagens ou commits.

Os relatórios que vieram nos arquivos preservam as datas e resultados das sessões anteriores. A verificação desta sessão está em `docs/validacao_escola_2026_10_19.md`.
