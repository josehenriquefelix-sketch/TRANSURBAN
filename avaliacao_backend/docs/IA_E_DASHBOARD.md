# Ciência de Dados e contrato para o dashboard

## Fonte e unidade de análise

`data/atrasos_analise.csv` foi recuperado do pacote TRANSURBAN_Modulo6_Revisado.zip, sem modificar seus bytes. O aviso original acompanha em ORIGEM_DADOS.txt. A fonte é sintética e foi reproduzida no pacote anterior; nesta revisão, seus bytes foram comparados com o GitHub e são idênticos ao arquivo data/atrasos_analise.csv do commit 2d3d554e4153ffc8cc3e39cbaf6b5d5385b87dee.

SHA-256: `adbb2b83ae59d8e5862b9ee949e3fdce215fb695e2073a3ceec05e7feed257f3`.

Uma linha representa uma observação por trecho/data/linha. O CSV não possui id_viagem: 180 registros **não comprovam 180 viagens completas**. Para a mesma razão, repetições idênticas são sinalizadas na auditoria e interrompem os indicadores HTTP até revisão da fonte.

## Dicionário do CSV

| Coluna | Tipo/Significado |
|---|---|
| data_registro | Data ISO AAAA-MM-DD da observação |
| cidade | Texto, cidade associada à linha |
| codigo_linha | Texto, preserva zeros à esquerda como 001 |
| nome_linha | Texto descritivo da linha |
| trecho | Texto, segmento observado |
| tipo_trecho | Texto, como urbano/intermunicipal |
| periodo | Texto, faixa do dia |
| condicao_transito | Texto, categoria de intensidade |
| clima | Texto, condição climática |
| tempo_programado_min | Número finito maior que zero, minutos previstos |
| tempo_real_min | Número finito não negativo, minutos observados |
| minutos_atraso | Número finito não negativo, atraso da observação |
| observacao | Texto opcional, contexto do registro |

Todas as colunas são obrigatórias no cabeçalho. Campos vazios em observacao são permitidos. Campos de identificação/dimensões vazios, data inválida, não numéricos/infinitos, tempo programado não positivo, tempo real negativo e atraso negativo sinalizam a linha na auditoria e interrompem os indicadores HTTP com 422. Não há imputação de zero. Verifica-se atraso = max(tempo_real − tempo_programado, 0), com tolerância absoluta de 0,01 minuto. A tolerância não significa precisão operacional dos dados.

## Perguntas, indicadores e rotas

| Pergunta do projeto | Indicador / API |
|---|---|
| Qual a qualidade da base? | GET /ia/qualidade: ausentes, inconsistências, duplicatas e exclusões |
| Quantas observações existem? | GET /ia/resumo: observacoes_validas, registros_lidos, observacoes_excluidas |
| Qual o atraso típico? | GET /ia/resumo: média e mediana |
| Qual o maior atraso e onde ocorre? | GET /ia/maiores-atrasos: todas as observações empatadas |
| Quais linhas/cidades concentram atrasos? | GET /ia/agrupamentos/linha e /cidade |
| Como o atraso varia no tempo? | GET /ia/agrupamentos/data e /periodo |
| Como se distribui por condições? | GET /ia/agrupamentos/transito e /clima |
| Quais trechos merecem análise? | GET /ia/agrupamentos/trecho |

Agregações trazem contagem, soma, média, mediana e máximo. A chave de agrupamento de linha é cidade + codigo_linha, evitando misturar códigos iguais de cidades diferentes. Nomes divergentes são sinalizados na qualidade e concatenados na resposta.

## Cálculos efetivamente conferidos

| Indicador | Valor da fonte incluída |
|---|---:|
| Registros lidos e válidos | 180 |
| Excluídos / duplicatas exatas adicionais | 0 / 0 |
| Soma dos atrasos por observação | 1.362 min |
| Média = 1.362 ÷ 180 | 7,5667 min |
| Mediana | 8 min |
| Máximo | 12 min |
| Observações empatadas no máximo | 7 |
| Atraso > 10 minutos | 26 (14,4444%) |
| Pares distintos cidade/código | 17 |
| Cidades | 2 |
| Período | 01/08/2026 a 31/08/2026 |

A conferência independente usa csv/statistics da biblioteca padrão do Python. Em todas as dimensões, a soma das contagens dos grupos é 180 e a soma dos atrasos é 1.362. Não se calcula a média geral como média simples das médias dos grupos; grupos podem ter tamanhos diferentes.

## Tratamento no dashboard da próxima avaliação

Cards: observações válidas, média, mediana e máximo. Barras: média por linha/cidade, sempre mostrando também a contagem. Série temporal: média por dia. Tabela: maiores atrasos com todos os empates. Painel de qualidade: lidos, excluídos e origem sintética.

- Valores de minutos são números; o frontend usa locale pt-BR para formatação.
- A API rejeita fonte vazia ou inválida com 422. A função interna de auditoria pode representar ausência por null; isso nunca autoriza apresentar 0 min como média.
- CSV ausente: 503. Cabeçalho inválido, dados incoerentes, duplicatas, fonte vazia e dimensão não suportada: 422.
- Os JSONs exportados são calculados por função; as respostas HTTP efetivamente executadas estão em evidencias/http/respostas_http.json.
- As rotas não têm CORS amplo configurado. Hospedar o frontend na mesma origem ou adicionar somente a origem de desenvolvimento necessária em etapa posterior.

## Limitações

Os dados não medem a pontualidade real das empresas. A soma não representa minutos perdidos por passageiros. Agrupamentos não provam que clima/trânsito causaram atrasos. Esta etapa realiza Ciência de Dados descritiva; não treina modelo preditivo nem estima chegada em tempo real. IDs e cadastros DS não são sincronizados automaticamente com o CSV: são fontes distintas nesta avaliação.
