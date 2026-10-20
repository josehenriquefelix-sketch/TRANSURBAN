# Guia do líder — API primeiro, site como complemento, sem slides

Equipe: José Henrique, Bruno, Kauan, Gustavo, Jullyany, Camila e Ana Carolina.

## Abertura de José Henrique

“Bom dia, pessoal! Quem aqui já ficou em dúvida sobre qual ônibus pegar ou saiu de casa sem saber como seria a viagem? Foi pensando nessas situações que desenvolvemos o TRANSURBAN, um projeto acadêmico voltado à experiência de passageiros e motoristas em Maringá e Sarandi.

Hoje vamos mostrar o que construímos e testar ao vivo. Primeiro, a API: a parte que recebe os pedidos, valida os dados e conversa com o banco. Depois, uma demonstração de como essas funções podem aparecer em um site.

Vamos separar com clareza o que já funciona no nosso protótipo e o que ainda depende de integração com a operadora. Não temos acesso ao GPS da frota nem processamos pagamentos. Na parte de Ciência de Dados, usamos uma fonte pública histórica de Curitiba para estudar a programação do transporte, com origem e limitações documentadas.”

Para o grupo: Bruno e Kauan mantêm as falas curtas do roteiro. José Henrique opera o computador; os demais explicam suas partes sem precisar procurar comandos. As falas completas continuam em `api-sem-slides/FALAS_PARA_TREINAR.txt`.

## Antes de chamar a equipe

Extraia o pacote, prepare Python 3.12 e execute o diagnóstico no equipamento da apresentação. Abra o servidor e espere `Application startup complete`. No navegador desse mesmo notebook, abra `/docs`. Para o site, abra `/app/`; use janela normal e anônima para sessões separadas. Confira fonte de energia, internet, projeção e tamanho das letras. Não mostre `.env`, senha do banco ou dados pessoais no telão.

`PREPARAR-WINDOWS.cmd` instala e verifica; `APRESENTAR-WINDOWS.cmd` inicia. No Linux, os mesmos modos usam `python3 iniciar_apresentacao.py`. `--diagnostico` confere a instalação em banco descartável. O diagnóstico não substitui testar o projetor e o GPS físico.

Se uma cidade já existe, o cadastro pode responder 409. Consulte `GET /cidades`, copie o ID existente e explique que a restrição impede duplicidade. Não apague o banco antes da apresentação. Para uma linha nova, use um código de demonstração ainda não cadastrado, como `DEMO-20-1430`, respeitando o limite do campo.

## Como explicar o caminho de uma requisição

1. No Swagger ou site, enviamos um pedido HTTP. `GET` consulta; `POST` cria um registro ou executa uma ação.
2. O FastAPI escolhe a função pela rota, por exemplo `POST /linhas`.
3. O Pydantic valida o JSON: campos obrigatórios, tipos, tamanho e espaços em branco.
4. A função aplica a regra do sistema. Antes de cadastrar uma linha, consulta se a cidade existe.
5. O SQLAlchemy envia comandos ao banco. `commit` confirma a gravação; `rollback` desfaz uma transação que falhou.
6. A API devolve um JSON e um código HTTP. O site transforma a resposta em informações visuais.

Exemplo: uma cidade recebe `id_cidade`. A linha guarda esse ID como chave estrangeira. Assim, várias linhas podem pertencer à mesma cidade. A consulta da linha traz também o nome da cidade, evitando obrigar a pessoa a interpretar somente números.

Exemplo conceitual de consulta SQL:

```sql
SELECT l.codigo, l.nome, c.nome AS cidade
FROM linha_onibus AS l
JOIN cidade AS c ON c.id_cidade = l.id_cidade;
```

A aplicação utiliza o relacionamento SQLAlchemy para obter essas informações; a consulta acima ajuda a explicar a relação no banco.

## O que cada arquivo faz

| Arquivo | Explicação para a equipe |
|---|---|
| `database.py` | Abre a conexão e fornece uma sessão de banco por operação. No SQLite, ativa o uso das chaves estrangeiras. |
| `models.py` | Define cidade e linha como tabelas, com colunas, chaves e relacionamentos. |
| `schemas.py` | Define os dados aceitos e devolvidos nas rotas DS; valida antes da gravação. |
| `main.py` | Monta o FastAPI, registra rotas e disponibiliza Swagger e site. No banco local, cria as tabelas ausentes; não migra o Supabase automaticamente. |
| `dados_publicos.py` | Lê e valida o conjunto público usado na análise IA; calcula resumo e agrupamentos. |
| `importar_dados_publicos.py` | Converte os arquivos GTFS publicados para o CSV de análise, preservando identificadores e origem. |
| `models_web.py` | Define contas, sessões, percursos, viagens, embarques, avaliações e lançamentos de demonstração. |
| `web_api.py` | Aplica permissões por perfil, autenticação, regras de viagem, carteira e consultas de clima e vias. |
| `web/app.js` | Controla telas, formulários e chamadas JSON à API; atualiza o mapa e mostra as respostas. |
| `web/styles.css` | Define cores, espaçamento, cartões e adaptação para celular. |
| `web/vendor/leaflet` | Biblioteca que apresenta o mapa. As imagens geográficas vêm do OpenStreetMap. |
| `iniciar_apresentacao.py` | Prepara, testa e inicia a apresentação com banco local; preserva `.env`. |
| `diagnosticar_apresentacao.py` | Confere arquivos e funcionamento em banco temporário, sem usar os cadastros da apresentação. |
| `test_*.py` e `gerar_evidencias.py` | Verificam regras e registram respostas; não garantem que um projetor ou serviço externo nunca falhará. |

`analise.py` e `ia_routes.py` preservam a base sintética anterior para testes. Não apresentem os seus atrasos como medições reais. O estudo público desta entrega está em `/ia/dados-publicos/`.

## IA: o que podemos afirmar

A fonte utilizada é um GTFS comunitário histórico de Curitiba, com período declarado de 28/09 a 05/10/2026. Não é uma base oficial da URBS nem de Maringá ou Sarandi. O arquivo tem 71.086 registros de programação e 309 códigos de linha. Isso não comprova viagens realizadas, ônibus distintos ou passageiros transportados.

O Pandas lê o CSV. A validação verifica colunas, identificadores, duplicidades, referências e integridade dos arquivos. Depois a API conta registros e agrupa por linha ou serviço. `groupby` reúne registros com a mesma dimensão; `count` conta, `sum` soma, `mean` calcula média e `median` encontra o centro dos valores ordenados.

A média de registros por linha é aproximadamente 230,05 e a mediana é 162, considerando o conjunto de categorias de serviço. Essas medidas descrevem a distribuição da programação do arquivo. Não são minutos de atraso e não devem ser anunciadas como viagens diárias efetivamente realizadas.

O resumo deixa atraso médio como `null`: significa que essa informação não está disponível nessa fonte. `null` não significa atraso zero. `limit=5` limita a lista exibida, mantendo explícitos o total global e a quantidade mostrada.

## Site: demonstração de dois minutos

No motorista, escolha pontos no mapa com o veículo parado, salve o percurso e inicie uma viagem de demonstração. Se autorizar o GPS, o navegador fornece sua posição real; o sistema aceita somente sinal com precisão de até 100 m e deixa de mostrar localização com mais de 90 segundos. Não diga que esse marcador é um ônibus da operadora.

No passageiro, encontre essa viagem, registre embarque, escolha pontos quando disponíveis e informe a lotação. Depois registre desembarque e avalie de 1 a 5 estrelas, com descrição. Mostre a avaliação no perfil do motorista.

“Aqui as contas e avaliações são realmente salvas no nosso banco local. A viagem é declarada por nós. O mapa é geográfico real; o cálculo do percurso usa as ruas entre pontos escolhidos. Ainda não está integrado ao itinerário oficial nem ao GPS da frota.”

Na carteira: “A tarifa integral urbana de Maringá publicada pela Prefeitura é R$ 5,80, com início em 12/07/2026. O site usa esse valor apenas como referência para a equivalência do saldo de teste. A recarga, o PIX, as parcelas e o vale-transporte aqui são demonstrações; não transferem dinheiro nem liberam a catraca.”

Se o saldo demonstrativo for R$ 150, a divisão inteira por R$ 5,80 resulta em 25 tarifas e sobra de R$ 5. Não são 25 bilhetes comprados. Sarandi e benefícios podem ter regras diferentes; não generalizamos esse valor.

Fonte: [notícia da Prefeitura de 10/07/2026](https://www.maringa.pr.gov.br/noticias/com-investimento-de-r-60-milhoes-prefeitura-de-maringa-garante-menor-tarifa-de-transporte-coletivo/42651). A fonte cita o decreto 1262/2026; não auditamos o texto do decreto.

O clima vem do Open-Meteo. Probabilidade de chuva é previsão, não certeza. Sem acesso ao serviço, o site informa indisponibilidade, sem criar um número.

## Perguntas que podem aparecer

**API é o site?** A API recebe e devolve dados; o site apresenta telas e usa esses dados. Nesta entrega, o mesmo servidor Python disponibiliza ambos.

**Onde estão os dados?** Na apresentação, em SQLite no notebook. Supabase é um serviço com PostgreSQL que requer configuração privada e migração compatível. Não afirmamos conexão remota quando `/health` informa `sqlite_local`.

**Por que 404 e 422 aparecem na demonstração?** São testes intencionais: cidade inexistente e entrada inválida. Comprovam que a API rejeita pedidos incorretos. 201 indica criação e 200 indica consulta concluída.

**O sistema sabe a lotação real?** Recebe relatos dos usuários e motorista. Não possui sensores nem contagem física confiável. Embarques registrados no app não representam todas as pessoas dentro do ônibus.

**É igual ao Waze?** Não. O traçado usa OSRM e dados OpenStreetMap, perfil de automóvel, sem trânsito ao vivo nem todas as restrições de ônibus. Não substitui navegação profissional ou orientação da operadora.

**As senhas ficam em texto?** Não. O servidor armazena hash PBKDF2 com sal aleatório. A sessão usa token aleatório em cookie HttpOnly; o banco guarda o hash desse token. Não há recuperação de senha nesta demonstração.

**Por que não podem garantir zero erros?** Rede, geolocalização, serviços externos e equipamento podem falhar. Por isso há testes, diagnóstico, mensagens de erro e evidências de apoio. Explicamos o limite e não inventamos resultados.

**O que vem depois?** Validar itinerários e pontos oficiais, integrar autenticação operacional e frota, contratar provedor de pagamentos e validar VT com a operadora, revisar implantação e privacidade. São etapas de integração, não funções já prontas por terem uma tela.
