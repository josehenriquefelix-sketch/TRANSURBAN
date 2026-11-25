# Linhas que atendem Sarandi

Decisão de interface revisada em 25/11/2026, a pedido da equipe: selecionar **Sarandi** mostra os serviços documentados cujo campo `cidades` inclui Sarandi, incluindo as ligações metropolitanas com Maringá. Esses registros mantêm o âmbito metropolitano e a identificação na interface. Não foram criados nomes de bairros, códigos, horários ou novas linhas para preencher a lista.

O catálogo existente, consultado em 12/11/2026, contém 22 entradas ou variantes metropolitanas que atendem Sarandi e 66 municipais de Maringá. Uma entrada pode ser variante de um mesmo serviço. Isso não representa 22 linhas municipais de Sarandi, nem comprova programação operacional atual em todos os pontos. A data do documento e a fonte continuam disponíveis em cada registro. A relação municipal completa de Sarandi ainda não foi confirmada.

## Evidências e limites

- Catálogo interno: `data/catalogo_publico_verificado.json`; campos `ambito`, `cidades`, `fonte_url`, `vigencia` e `sentidos`.
- DER/PR: [Maringá–Sarandi (Conjunto Vale Azul), linha 001.0254-470](https://www.der.pr.gov.br/sites/der/arquivos_restritos/files/documento/2026-02/Maringa_Sarandi_Cj_Vale_Azul_REG0511_Linha0010254470_010226.pdf). Documento com vigência indicada de 01/02/2026, conferido na web em 25/11/2026; identifica o serviço e saídas das duas cidades. Não é prova de passagem em cada ponto neste momento.
- Prefeitura de Sarandi: [página de horários de transporte público](https://www.sarandi.pr.gov.br/web/index.php/servicos/horarios-transporte-publico). A existência de uma página municipal não confirma a vigência atual de uma relação completa. A consulta complementar apresentou indisponibilidade; nenhum horário novo foi extraído para o aplicativo nesta revisão.

Maringá continua mostrando apenas seu catálogo municipal. A opção **Maringá ↔ Sarandi** continua reunindo as ligações metropolitanas. A aba Sarandi também permite encontrar essas ligações, sem alterar sua classificação. Não é necessário executar migrações SQL nem mudar as 12 tabelas para essa melhoria.
