# Fontes dos dados da apresentação

Consulta em 20/10/2026.

Os nomes Maringá e Sarandi e os códigos municipais 4115200 e 4126256 constam na [tabela de municípios do IBGE](https://www.ibge.gov.br/explica/codigos-dos-municipios.php). Os códigos IBGE são referências da fonte; as PKs desta API são geradas pelo PostgreSQL.

As três linhas abaixo constam nos [horários vigentes publicados pelo DER-PR](https://www.der.pr.gov.br/Pagina/Horarios-Vigentes). Cada link abre o documento oficial da respectiva linha.

| Código oficial | Nome cadastrado | Vigência do documento | Fonte |
|---|---|---|---|
| 001.0254-420 | Maringá - Sarandi (Parque Alvamar) | 01/02/2026 | [DER-PR](https://www.der.pr.gov.br/sites/der/arquivos_restritos/files/documento/2026-02/Maringa_Sarandi_Pq_Alvamar_REG0511_Linha0010254420_010226.pdf) |
| 001.0254-470 | Maringá - Sarandi (Cj. Vale Azul) | 01/02/2026 | [DER-PR](https://www.der.pr.gov.br/sites/der/arquivos_restritos/files/documento/2026-02/Maringa_Sarandi_Cj_Vale_Azul_REG0511_Linha0010254470_010226.pdf) |
| 002.0254-470 | Maringá - Sarandi (Monte Rey) | 15/04/2026 | [DER-PR](https://www.der.pr.gov.br/sites/der/arquivos_restritos/files/documento/2026-04/Maringa_Sarandi_Monte_Rey_REG0511_Linha0020254470_150426.pdf) |

Os nomes foram transcritos com capitalização normalizada. O campo `codigo` utiliza o código completo do DER-PR. Sarandi foi escolhida como cidade de referência dessas linhas no recorte Cidade → Linha de Ônibus; as linhas atendem os dois municípios, como seus nomes indicam. Essa associação é uma decisão de modelagem do projeto.

Os documentos publicam horários planejados. Eles não comprovam medições de atrasos ou localização de veículos em tempo real. Esta API cadastra e consulta cidades e linhas.

## Banco e evidências

O `.env` local aponta para o schema `transurban_caderno` no Supabase. O schema foi criado para esta reconstrução. Ele contém duas cidades e três linhas com fontes verificadas. Os registros anteriores do schema `public` foram preservados.

`evidencias/supabase_dados_reais.json` registra os testes da base da apresentação. `resultado_cidade.json` e `resultado_linha.json` registram os testes das duas etapas em um schema isolado de PostgreSQL local; os nomes e códigos de linha dessas duas evidências são dados de teste. `resultado_supabase.json` e `conferencia_supabase.json` registram a inspeção inicial da base anterior e podem conter registros demonstrativos antigos.
