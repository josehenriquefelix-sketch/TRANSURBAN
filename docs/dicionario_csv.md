# Dicionário do CSV — TransUrban

Arquivo principal: `data/atrasos_analise.csv`

A massa possui **180 registros acadêmicos** e **13 colunas**. Os dados são sintéticos e servem para análise; não representam rastreamento em tempo real.

| Coluna | Tipo esperado | Descrição | Exemplo de uso |
|---|---|---|---|
| data_registro | Data | Data do registro analisado | análise temporal |
| cidade | Texto | Cidade associada ao registro | agrupamento por cidade |
| codigo_linha | Texto | Código da linha | identificação da linha |
| nome_linha | Texto | Nome da linha | leitura humana |
| trecho | Texto | Trecho analisado | comparação de trajetos |
| tipo_trecho | Categoria | Tipo do trecho | segmentação |
| periodo | Categoria | Período do dia | agrupamento temporal |
| condicao_transito | Categoria | Condição do trânsito | análise de associação com atraso |
| clima | Categoria | Condição climática | análise por clima |
| tempo_programado_min | Inteiro | Tempo planejado em minutos | comparação planejado x real |
| tempo_real_min | Inteiro | Tempo observado em minutos | comparação planejado x real |
| minutos_atraso | Inteiro | Diferença usada como indicador de atraso | estatísticas e classificação |
| observacao | Texto | Observação sobre o registro e sua natureza acadêmica | contexto |

## Qualidade verificada

A análise do projeto verifica:

- quantidade de registros e colunas;
- valores nulos;
- duplicidades;
- atrasos negativos;
- data inicial e final;
- consistência temporal;
- agregações por cidade, período, trânsito, clima e linha.

Os resultados gerados ficam em `ia/resultados/`.
