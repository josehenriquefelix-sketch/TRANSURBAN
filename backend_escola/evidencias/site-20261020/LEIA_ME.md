# Validação de 20/10/2026

- Diagnóstico: dependências, hashes do mapa, banco descartável, site, Swagger e resumo IA aprovados; consultas reais a Open-Meteo, OSRM e imagem OpenStreetMap com validação TLS ativa.
- Mapa no Chromium: oito imagens carregadas por relay de QA usando cliente HTTPS Playwright com validação TLS ativa. O relay não integra o aplicativo. Esse ensaio substitui o anterior com exceção de certificado.
- Suíte após a referência oficial de tarifa: 41 testes aprovados, 1 aviso de depreciação da biblioteca de testes, em 26,82 s.
- Referência de tarifa: fonte oficial em `../../data/site/tarifa.json`; Maringá urbana integral, R$ 5,80 desde 12/07/2026. Não generalizada para Sarandi.

Não substitui teste de GPS físico, Windows ou projetor no equipamento da apresentação. Não há conexão Supabase nem pagamentos reais.

- Fluxo Chromium repetido após a atualização da tarifa: duas contas, saldo de teste R$ 150, avaliação e encerramento aprovados, sem erros JavaScript. Na tela: equivalência de 25 tarifas integrais de R$ 5,80 e resto R$ 5, sem bilhetes reais.
- Falhas previstas de diagnóstico: cópia temporária de arquivo adulterado e fixture de dependências ausentes foram detectadas; arquivos originais preservados.
