# Base Ciência de Dados — TRANSURBAN

## O que representa cada linha

Uma linha representa uma observação acadêmica de atraso em um trecho de uma linha de ônibus, em uma data e condição registradas. Ela não representa necessariamente uma viagem completa nem um ônibus ou passageiro único.

## Códigos que não devem ser contados repetidamente

- `codigo_linha` pode aparecer em diversas observações; a chave para identificar uma linha no conjunto é o par **cidade + código da linha**.
- `data_registro` pode se repetir em diferentes observações. Como a fonte não tem `id_observacao`/`id_viagem`, não é possível afirmar que cada linha corresponda a uma viagem distinta.
- Os endpoints contam observações e somam `minutos_atraso` por observação. Não contam viagens, ônibus, passageiros nem pessoas únicas.
- Duplicatas completas do CSV são sinalizadas e bloqueiam os cálculos para evitar contagem duplicada silenciosa.

## Quatro perguntas respondidas pela API

1. **Quanto atraso foi observado em cada cidade?** `GET /ia/totalizacao/cidade`
2. **Como o total e a média de atraso se distribuem entre os períodos do dia?** `GET /ia/totalizacao/periodo`
3. **Qual o total e a média observados em cada condição de trânsito?** `GET /ia/totalizacao/transito`
4. **Qual o total e a média observados em cada condição de clima?** `GET /ia/totalizacao/clima`

Cada resposta JSON apresenta a dimensão, a quantidade de observações, a soma, a média, a mediana e o maior atraso em minutos. `GET /ia/resumo` apresenta cobertura e limitações da base.

## Origem e limites

O arquivo `data/atrasos_analise.csv` é uma massa sintética para validação acadêmica, conforme `data/ORIGEM_DADOS.txt`. Os valores não descrevem operação real de transporte em Maringá/Sarandi e não permitem inferir causalidade ou prever horários.
## Resultado conferido com o CSV entregue

Os resultados abaixo foram calculados localmente sobre as 180 linhas sintéticas. Há 180 observações válidas, nenhuma linha excluída e nenhuma duplicata completa; o período vai de 1 a 31 de agosto de 2026. Foram somados **1.362 minutos** de atraso observados, com média de **7,57 minutos** por observação. Isso é uma soma da base demonstrativa, não um indicador operacional real.

| Pergunta | Grupo | Observações | Soma (min) | Média (min) | Mediana (min) | Máximo (min) |
|---|---|---:|---:|---:|---:|---:|
| Cidade | Maringá | 120 | 927 | 7,73 | 8 | 12 |
| Cidade | Sarandi | 60 | 435 | 7,25 | 8 | 11 |
| Período | Entre picos | 45 | 409 | 9,09 | 9 | 11 |
| Período | Noite | 45 | 320 | 7,11 | 7 | 9 |
| Período | Pico manhã | 45 | 190 | 4,22 | 5 | 6 |
| Período | Pico tarde | 45 | 443 | 9,84 | 10 | 12 |
| Trânsito | Intenso | 45 | 443 | 9,84 | 10 | 12 |
| Trânsito | Leve | 45 | 190 | 4,22 | 5 | 6 |
| Trânsito | Moderado | 45 | 320 | 7,11 | 7 | 9 |
| Trânsito | Muito intenso | 45 | 409 | 9,09 | 9 | 11 |
| Clima | Chuva | 45 | 320 | 7,11 | 7 | 9 |
| Clima | Sem chuva | 135 | 1.042 | 7,72 | 8 | 12 |

O CSV contém 26 observações acima de 10 minutos (14,44%). Os agrupamentos descrevem a distribuição nesta amostra sintética; não provam que essas condições causaram atrasos.
