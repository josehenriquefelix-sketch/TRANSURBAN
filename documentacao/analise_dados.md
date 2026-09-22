# Módulo 6 IA — Do CSV à informação

## Fonte analisada

Arquivo: `database/dados.csv`

O arquivo possui 180 registros acadêmicos. Cada linha representa um registro de viagem/atraso utilizado para estudar o comportamento do transporte coletivo no projeto TransUrban. Os dados são sintéticos e não representam telemetria em tempo real.

## Coluna numérica escolhida

`minutos_atraso`

Essa coluna foi escolhida porque está diretamente relacionada ao problema do projeto: compreender os atrasos no transporte coletivo.

## Pergunta estatística

**Como os minutos de atraso se comportam na massa acadêmica do TransUrban?**

Resultados:

| Medida | Resultado |
|---|---:|
| Média | 7,57 min |
| Mediana | 8 min |
| Moda | 8 min |
| Mínimo | 2 min |
| Máximo | 12 min |
| Amplitude | 10 min |
| Variância amostral | 6,76 |
| Desvio padrão amostral | 2,60 min |

### Interpretação

A média de 7,57 minutos e a mediana de 8 minutos são próximas, o que indica que o centro da distribuição não está sendo fortemente distorcido por valores extremos. O menor atraso é 2 minutos e o maior é 12 minutos. O desvio padrão de aproximadamente 2,60 minutos mostra que existe variação entre os registros, mas dentro de uma faixa relativamente limitada nessa massa sintética.

## Pergunta de agregação

**Como muda o atraso médio de acordo com a condição de trânsito?**

Foi usado `groupby("condicao_transito")` com média de `minutos_atraso`.

| Condição de trânsito | Atraso médio |
|---|---:|
| Leve | 4,22 min |
| Moderado | 7,11 min |
| Muito intenso | 9,09 min |
| Intenso | 9,84 min |

### Interpretação

Na massa acadêmica, os registros classificados como trânsito intenso ou muito intenso apresentam médias de atraso maiores que os registros de trânsito leve. Isso é uma associação observada na massa de teste e não prova, sozinha, uma relação causal.

## Classificação baseada em regras

Critério usado pelo projeto:

- até 5 minutos: **Baixo**
- de 6 a 10 minutos: **Moderado**
- de 11 a 15 minutos: **Alto**
- acima de 15 minutos: **Muito alto**

Resultados:

| Classe | Registros |
|---|---:|
| Baixo | 43 |
| Moderado | 111 |
| Alto | 26 |
| Muito alto | 0 |

### Justificativa

As classes foram criadas para transformar os minutos em categorias fáceis de interpretar no contexto acadêmico do dashboard. Elas não representam um padrão oficial do transporte público; são uma regra definida para a análise do projeto e devem ser apresentadas dessa forma.

## Visualização

A visualização principal do Módulo 6 compara o atraso médio por condição de trânsito. O gráfico é gerado pelo código em `backend/analise.py` e salvo em `ia/resultados/grafico_02_transito.png`.

## Caminho do dado

```text
database/dados.csv
        ↓
backend/analise.py
        ↓
DataFrame do Pandas
        ↓
estatística + agregação + classificação
        ↓
interpretação
        ↓
gráfico / informação
```

## Como executar

Na raiz do projeto:

```powershell
python backend/main.py
```

A execução mostra as primeiras linhas, nomes das colunas, quantidade de registros, estatísticas, agregação, classificação e salva a visualização.

## Conclusão

A camada de IA do Módulo 6 transforma o CSV em informação por meio de técnicas adequadas ao problema. O resultado mais relevante é que, dentro da massa sintética utilizada, condições de trânsito mais intensas aparecem associadas a atrasos médios maiores. A análise permanece acadêmica e deve ser interpretada apenas dentro dos dados utilizados.
