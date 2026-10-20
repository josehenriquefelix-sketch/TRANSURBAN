# TRANSURBAN — Roteiro completo de IA

Apresentação de Ciência de Dados • 20/10/2026 • Sem slides

Apresentadoras: Jullyany e Camila. Duração sugerida: 6 a 8 minutos, incluindo consultas. Este roteiro é independente de DS e trata do CSV e da análise disponibilizada pela API. Jullyany ou outra pessoa da equipe pode operar os cliques enquanto a colega fala.

## Como usar este documento

Os parágrafos iniciados por “FALA” são para apresentar. As instruções “NA TELA” e “APOIO” não precisam ser lidas. Esperem a resposta real da API e apontem o campo explicado; não leiam todo o JSON. Os valores de referência abaixo pertencem ao snapshot incluído no pacote.

## Preparação antes de o público entrar

Extraia o pacote inteiro e abra backend_escola no VS Code. A primeira instalação exige internet e Python 3.12. Não execute dentro do ZIP nem copie um ambiente virtual Windows para Linux.

No Windows:

```powershell
py -3.12 iniciar_apresentacao.py --preparar
py -3.12 iniciar_apresentacao.py --testar
py -3.12 iniciar_apresentacao.py --diagnostico
py -3.12 iniciar_apresentacao.py
```

No Linux, com python3 --version indicando 3.12:

```bash
python3 iniciar_apresentacao.py --preparar
python3 iniciar_apresentacao.py --testar
python3 iniciar_apresentacao.py --diagnostico
python3 iniciar_apresentacao.py
```

Espere Application startup complete e deixe o terminal aberto. No navegador DESSE computador, abra http://127.0.0.1:8000/docs. Trabalhe somente no grupo “IA — Dados públicos: Curitiba (histórico)”. O modo apresentação oculta as rotas sintéticas anteriores do Swagger.

Este modo não precisa de .env nem Supabase. A análise utiliza arquivos locais. Depois de instalar as dependências, o Swagger e as consultas deste CSV podem funcionar sem internet. A fonte precisa ter sido incluída no pacote inteiro. A suíte completa foi validada com 41 testes na nuvem Linux; isso não significa “41 testes só de IA”. Confiram também no equipamento da apresentação.

## 1. Jullyany — abertura

FALA: “Bom dia, pessoal! Eu sou a Jullyany, e junto com a Camila vou apresentar a parte de Ciência de Dados do projeto TRANSURBAN.

FALA: Nosso objetivo foi organizar uma fonte de dados, verificar sua qualidade, produzir indicadores e disponibilizar os resultados pela API.

FALA: Para isso, usamos Python e a biblioteca Pandas. Vamos mostrar o arquivo utilizado, explicar os cálculos e consultar os resultados ao vivo.”

## 2. Jullyany — origem e período da fonte

NA TELA: abra GET /ia/dados-publicos/fonte → Try it out → Execute. Mostre cidade, feed_oficial, publicador_gtfs e periodo_declarado_feed. Não precisa ler a URL ou o hash inteiro em voz alta.

FALA: “O TRANSURBAN é um projeto voltado a Maringá e Sarandi. Porém, não tínhamos uma base local de atrasos reais disponível para essa análise.

FALA: Por isso, utilizamos uma base pública histórica de programação do transporte de Curitiba, disponibilizada em um GTFS comunitário. GTFS é um formato usado para organizar informações de transporte público.

FALA: Esse conjunto é comunitário e não é uma publicação oficial da URBS. O período declarado vai de 28 de setembro a 5 de outubro de 2026.

FALA: Estamos estudando uma programação publicada. Não estamos mostrando rastreamento dos ônibus nem comprovando que todas as viagens aconteceram.”

APOIO: o publicador comunitário declara origem em dados URBS espelhados pelo C3SL/UFPR; a equipe conferiu o derivado publicado, o código do conversor e a catalogação na Mobility Database. Não diga que a equipe coletou GPS ou obteve certificação da URBS. O período é o declarado no feed, não uma lista de datas de operação observada.

## 3. Jullyany — o que há no CSV

NA TELA: se necessário, mostre apenas o cabeçalho de data/dados_publicos/programacao_curitiba.csv no VS Code. Não abra milhares de linhas durante a fala.

FALA: “O CSV é um arquivo organizado como uma tabela. As colunas representam informações, e cada linha representa um registro.

FALA: Nosso arquivo tem o identificador de programação, o código e o nome da linha, o tipo de serviço, a operadora e informações sobre cidade e período da fonte.

FALA: Cada linha do arquivo representa um registro de programação publicado. Não significa um passageiro, um ônibus diferente ou uma viagem comprovadamente realizada.

FALA: Também podemos dizer que esse CSV é desnormalizado: ele reúne informações relacionadas em um mesmo arquivo. Por exemplo, o nome da linha e a operadora aparecem junto de cada registro de programação. Isso facilita certas análises, mas exige conferir a consistência das informações repetidas.”

APOIO — dicionário das colunas:

| Coluna | Significado e cuidado |
|---|---|
| id_programacao | Identificador do registro, derivado do trip_id publicado; lido como texto. |
| codigo_linha | Código da linha; texto, para não perder zeros ou interpretar como medida numérica. |
| nome_linha | Nome associado ao código da linha. |
| tipo_servico | Categoria: dias_uteis, sabado ou domingo. Não prova operação em uma data específica. |
| operadora | Informação associada à agência do feed; não prova validação oficial da publicação comunitária. |
| cidade_fonte e uf_fonte | Curitiba e PR; não são Maringá e Sarandi. |
| periodo_feed_inicio e periodo_feed_fim | Período declarado pelo feed, não datas de medições de atraso. |

O arquivo tem nove colunas; a tabela agrupa alguns pares de colunas para facilitar a explicação. Todas são inicialmente lidas como texto. As medidas numéricas são calculadas a partir das contagens.

## 4. Jullyany — Pandas e qualidade dos dados

NA TELA: volte ao Swagger e execute GET /ia/dados-publicos/qualidade. Aponte registros_lidos, ausentes_por_coluna, ids_duplicados, hash_csv_confere e apta_para_calculos_do_snapshot.

FALA: “Usamos o Pandas para ler e organizar o CSV. Antes de calcular, conferimos se as colunas esperadas estão presentes, se existem campos vazios ou identificadores repetidos e se o mesmo código aparece com nomes divergentes.

FALA: Também verificamos as categorias de serviço e se a cidade e o período continuam compatíveis com a fonte documentada.

FALA: Outro cuidado foi conferir a integridade dos arquivos por meio de um hash. Ele funciona como uma assinatura do conteúdo: se o arquivo mudar, a assinatura também muda.

FALA: Se essas verificações encontrarem uma divergência, a API bloqueia os indicadores para revisão. Não descartamos ou substituímos registros silenciosamente.

FALA: Agora a Camila vai mostrar as perguntas que conseguimos responder e os indicadores produzidos.”

APOIO: não fale que todos os campos são perfeitos apenas porque um indicador apareceu. Mostre os resultados reais da auditoria. Não confunda o hash com certificação de verdade do conteúdo: ele detecta alteração de bytes, não comprova sozinho que a programação foi cumprida.

## 5. Camila — perguntas e contagens

NA TELA: execute GET /ia/dados-publicos/resumo. Mostre registros_programacao, linhas_distintas e tipos_servico_distintos.

FALA: “Depois de entender e verificar a fonte, formulamos perguntas que esses dados conseguem responder. Quantos registros de programação existem? Quantas linhas aparecem? Como esses registros estão distribuídos entre as linhas e as categorias de serviço?

FALA: Nosso conjunto possui 71.086 registros de programação e 309 códigos de linha distintos, em três categorias de serviço.

FALA: Esses números descrevem o conteúdo do arquivo. Eles não representam passageiros transportados, ônibus diferentes ou viagens comprovadamente realizadas.

FALA: Definir corretamente o que estamos contando é uma parte essencial da análise.”

## 6. Camila — soma, média e mediana

NA TELA: continue no resumo. Aponte soma_registros_nos_grupos_linha, media_registros_programacao_por_linha e mediana_registros_programacao_por_linha.

FALA: “Ao somar as contagens dos grupos de linha, voltamos ao total de 71.086 registros. Essa conferência ajuda a verificar a consistência do agrupamento.

FALA: A média é aproximadamente 230,05 registros por linha. Para calculá-la, dividimos o total de registros pela quantidade de linhas.

FALA: A mediana é 162. Ela é encontrada depois de ordenar as quantidades e identificar o valor central.

FALA: A média pode ser influenciada por linhas com quantidades muito maiores. A mediana ajuda a observar o centro da distribuição. Por isso, as duas medidas oferecem uma visão mais completa.

FALA: Esses indicadores consideram o conjunto de categorias de serviço do arquivo. Não são médias diárias, minutos de atraso nem viagens efetivamente realizadas.”

APOIO: 71.086 dividido por 309 resulta em aproximadamente 230,0518. A mediana é calculada sobre as 309 contagens por código de linha; ela não é a mediana dos códigos numéricos.

## 7. Camila — agrupamento por linha

NA TELA: abra GET /ia/dados-publicos/agrupamentos/{dimensao}. Em dimensao, selecione linha. No parâmetro chamado limite, preencha 5. Clique Execute. O nome correto do parâmetro é limite, não limit.

FALA: “Nesta consulta, agrupamos os registros por linha. Agrupar significa reunir registros que têm uma característica em comum e calcular informações para cada grupo.

FALA: Isso permite comparar a distribuição da programação entre as linhas presentes no arquivo.

FALA: Estamos mostrando cinco grupos para facilitar a leitura no telão. O limite reduz a lista exibida, mas não transforma cinco no total da base. A resposta identifica o total de grupos e a quantidade que está sendo mostrada.”

APOIO: leia total_grupos, grupos_exibidos e resultados. soma_registros_nos_grupos é o total completo; soma_registros_dos_grupos_exibidos corresponde somente à amostra exibida. Não troque essas duas somas.

## 8. Camila — agrupamento por serviço

NA TELA: na mesma operação, selecione dimensao = servico e mantenha limite = 5, ou abra o endereço /ia/dados-publicos/agrupamentos/servico?limite=5. Execute.

FALA: “Também agrupamos os dados por categoria de serviço: dias úteis, sábado e domingo.

FALA: Essa separação permite comparar a composição da programação publicada. Ainda assim, estamos descrevendo o arquivo, e não confirmando o que aconteceu nas ruas.”

APOIO — valores do snapshot, leia somente se aparecerem:

| Categoria | Registros de programação |
|---|---|
| dias_uteis | 33.425 |
| sabado | 20.754 |
| domingo | 16.907 |
| Total | 71.086 |

Não interprete esse total como viagens de uma semana específica ou como número de passageiros. Os rótulos de categoria, sozinhos, não comprovam operação em cada data.

## 9. Camila — API, JSON e informação indisponível

NA TELA: volte a GET /ia/dados-publicos/resumo. Aponte viagens_realizadas e atraso_medio_min, ambos null.

FALA: “Os resultados são disponibilizados pela API em JSON. É um formato organizado que pode ser utilizado por um site ou dashboard para construir cartões, tabelas e gráficos.

FALA: Tivemos o cuidado de não calcular informações que a fonte não permite. O atraso médio aparece como null porque não temos medições reais suficientes para produzir esse indicador. Isso significa informação indisponível, e não atraso zero.

FALA: Nossa análise não prevê quando um ônibus vai chegar e não identifica causas de atraso. Ela descreve a programação do arquivo.”

## 10. Jullyany e Camila — conclusão

JULLYANY — FALA: “Com esse trabalho, percorremos as etapas de uma análise de dados: entender a fonte, organizar o CSV, verificar a qualidade, formular perguntas e calcular indicadores.”

CAMILA — FALA: “A API disponibiliza esses resultados para uma próxima etapa de dashboard. Nosso cuidado foi apresentar informações sustentadas pelos dados disponíveis, deixando claras a origem, a unidade de contagem e as limitações. Obrigada pela atenção!”

## Apoio: como explicar os códigos de IA

| Arquivo ou função | Explicação simples |
|---|---|
| importar_dados_publicos.py | Converte o conjunto GTFS publicado para o CSV da análise, preservando origem e identificadores. |
| dados_publicos.py | Lê, verifica e analisa o CSV; contém as rotas /ia/dados-publicos. |
| pd.read_csv | Lê o arquivo em uma tabela do Pandas. |
| dtype='string' | Preserva os campos como texto, inclusive códigos e identificadores. |
| groupby | Reúne registros pela dimensão escolhida, como código de linha ou tipo de serviço. |
| size | Conta quantos registros existem em cada grupo. |
| sum | Soma as contagens dos grupos. Não soma códigos de linha. |
| mean e median | Calculam média e mediana das contagens. |
| hashlib.sha256 | Produz o hash usado na verificação de integridade dos arquivos. |
| FastAPI | Disponibiliza os resultados por rotas HTTP, devolvendo JSON. |

A base apresentada é programacao_curitiba.csv. analise.py, ia_routes.py e atrasos_analise.csv pertencem à base sintética anterior de testes. Não usem os atrasos sintéticos como medições reais no palco.

## Perguntas que podem aparecer

| Pergunta | Resposta curta |
|---|---|
| Por que Curitiba? | Não tínhamos uma base local de atrasos reais disponível. Utilizamos uma fonte pública histórica e documentamos essa diferença. |
| A base é oficial? | Não. É um derivado comunitário publicado em GTFS. A origem declarada e as limitações estão documentadas. |
| Os dados são inventados? | Esta análise utiliza registros publicados de programação. A base sintética anterior fica separada para testes e não é anunciada como dado real. |
| Vocês mediram os atrasos? | Não. Não há medições suficientes nessa fonte para calcular atraso real. |
| O que é null? | Informação indisponível; não significa zero. |
| Qual a diferença entre média e mediana? | Média usa todos os valores na divisão; mediana é o valor central depois de ordenar as contagens. |
| Onde entra o Python? | Na conversão, leitura, verificação e análise dos dados, além da API. |
| Onde entra o Pandas? | No trabalho com a tabela CSV, contagens e agrupamentos. |
| Vocês treinaram uma IA? | Não. Nesta avaliação, trabalhamos Ciência de Dados: preparação, análise e disponibilização dos indicadores. |
| Por que não agrupar por data de viagem? | As datas disponíveis são do período declarado do feed, não datas de operação observada de cada registro. Não inventamos uma série diária. |
| O que vem depois? | Utilizar os resultados no dashboard e buscar fontes locais adequadas às perguntas que ainda não podem ser respondidas. |

## Referências para conferência

Publicação comunitária: https://github.com/benaytms/urbs-gtfs

Metadados, período, URLs e hashes desta cópia: backend_escola/data/dados_publicos/fonte.json. O arquivo registra também a catalogação na Mobility Database e a versão do código usada na conferência. Consulte a operação /ia/dados-publicos/fonte durante a apresentação.

## Se uma consulta falhar

Confira se o servidor permanece aberto no mesmo computador. Não invente um resultado nem apresente um JSON salvo como se tivesse acabado de ser calculado.

FALA DE APOIO: “A consulta não respondeu como esperado neste momento. Temos evidências de uma execução anterior e vamos identificá-las como evidências, sem confundir com o teste ao vivo.”

O roteiro é apoio para compreender e ensaiar. Se o professor fizer uma pergunta fora do que foi verificado, digam que precisam conferir a fonte ou o código antes de responder.
