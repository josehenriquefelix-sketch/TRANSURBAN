# Fonte pública usada na apresentação — Curitiba, PR

**Não é uma base de atrasos de Maringá/Sarandi.** É um snapshot público de programação de transporte de Curitiba, usado como estudo externo do TRANSURBAN. O feed comunitário declara o período de 28/09 a 05/10/2026. É histórico, não programação atual.

## Fonte e conferência

- Publicador do GTFS: Benay Tomas, projeto público URBS-GTFS: https://github.com/benaytms/urbs-gtfs
- Snapshot baixado: https://github.com/benaytms/urbs-gtfs/releases/download/latest/gtfs_curitiba.zip
- Catalogação independente: Mobility Database, MDB-3225. O registro `is_official` é `False`, não um feed oficial da URBS.
- O publicador declara usar dados abertos URBS espelhados em C3SL/UFPR: https://dadosabertos.c3sl.ufpr.br/curitibaurbs/
- Nesta sessão foram consultados o ZIP, o código/README do conversor e o catálogo; o espelho primário não foi consultado diretamente. Não atribuir certificação oficial ao derivado.
- URLs fixadas por commit, data de coleta e hashes estão em `fonte.json` e são exibidos por GET `/ia/dados-publicos/fonte`.

Os arquivos `trips.txt`, `routes.txt`, `agency.txt`, `feed_info.txt` e `calendar.txt` foram preservados em `originais/`. O CSV `programacao_curitiba.csv` resulta de joins many-to-one de trips, routes e agency. Acrescentamos município/UF da catalogação e período de feed_info. Não criamos horários ou registros de transporte.

**Atenção ao conversor:** ele propaga horários conhecidos para extremos do itinerário. Por isso `stop_times.txt` NÃO integra nossa análise. Não calculamos duração, pontualidade, atrasos, trajetos reais ou previsões a partir desse feed.

## O que cada linha representa

Um registro `trip_id` da programação GTFS convertida. O identificador é preservado. Não equivale a uma viagem efetivamente realizada, ônibus único, passageiro ou necessariamente uma partida operacional distinta: a conversão parte de tabelas de horários e terminais. Os nomes de linha e operadora são repetidos para formar o CSV desnormalizado.

## Resultados conferidos diretamente nos arquivos

- 71.086 registros de programação e 309 códigos de linha no snapshot.
- Categorias: dias úteis 33.425; sábado 20.754; domingo 16.907. A soma reconcilia 71.086.
- Média de registros por código de linha, somando categorias: 71.086 / 309 = 230,0518.
- Mediana das 309 contagens por linha: 162.
- Essas medidas não são minutos e não representam oferta realizada por dia/semana.
- Datas do período são metadados do feed, não datas observadas de cada viagem.
- Não há medição de atraso: o campo correspondente é null, que significa indisponível, não zero.

## Perguntas que a análise responde

1. Quantos registros e códigos de linha existem no snapshot?
2. Como esses registros se distribuem por linha e categoria de serviço?
3. Qual a média e mediana do número de registros por linha?

Não responde quantos ônibus rodaram, quantos passageiros viajaram, qual a demora real ou como funciona Maringá/Sarandi. A adaptação ao projeto é da técnica de backend e análise; a cobertura geográfica da fonte não muda.

## Reproduzir

Com o ZIP original baixado, use Python da venv e:

```text
python importar_dados_publicos.py CAMINHO_DO_ZIP --destino OUTRA_PASTA
```

O importador recusa sobrescrever o CSV. Para esse snapshot, confronte o SHA256 do ZIP com `fonte.json`; o link latest pode mudar. A API usa o snapshot incluído, sem baixar arquivos durante a apresentação. A licença Apache-2.0 do conversor não foi atribuída aos dados; o feed não declara licença própria. Fontes e autoria são preservadas.
