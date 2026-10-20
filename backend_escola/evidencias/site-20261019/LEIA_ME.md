# Evidências do site — 19/10/2026

- `site-web-browser.json`: ensaio Chromium em duas sessões. GPS emulado somente no teste, serviços externos bloqueados propositalmente para verificar degradação sem dados inventados.
- `site-servicos-externos.json`: consultas posteriores reais a Open-Meteo (Maringá/Sarandi) e OSRM (pontos escolhidos para teste, não paradas oficiais). Fonte e horários nas respostas.
- Suíte Python: 41 aprovados e 1 aviso de depreciação em biblioteca de testes.

Não foram publicados banco de contas, cookies, senha pessoal, `.env` nem dados de cartão. Estes resultados não substituem o ensaio no notebook e projetor do auditório.

- `site-mapa-online.json`: imagem OpenStreetMap carregada no navegador via proxy de QA; exceção de certificado apenas no navegador de teste, descrita no relatório. Não comprova a rede do auditório.

Atualização 20/10: o ensaio anterior do mapa com exceção de certificado foi substituído por `../site-20261020/mapa-tls-validado.json`, com validação TLS ativa. Use o novo resultado para a entrega atual.
