# TRANSURBAN — guia da equipe

Pacote local preparado em 19/10/2026 para apresentação em 20/10/2026.
Site demonstrativo offline e API local são componentes separados. O console consulta a API; o site mantém seu próprio cenário no navegador.
A base deste pacote é sintética. O pacote backend_escola e a base pública de Curitiba citados no texto não foram encontrados.

## Abrir neste notebook

Extraia o ZIP e execute ABRIR-APRESENTACAO.cmd. O inicializador abre http://127.0.0.1:8000/docs, /app/ e /apresentacao.
Em outro computador, instale Python 3.12 ou 3.13 e execute PREPARAR-OUTRO-COMPUTADOR.cmd com internet. Depois execute ABRIR-APRESENTACAO.cmd.
Se o Swagger não carregar sem internet, use http://127.0.0.1:8000/console.
O servidor registra mensagens em servidor.log. Não é necessário configurar Supabase nem credenciais.

## Videoaula e transcrição

videoaula.mp4 usa narração sintética em português e telas didáticas. Não é uma gravação da operação do navegador. As legendas estão no arquivo videoaula.vtt.

### 1. TRANSURBAN · aula do grupo — 00:00:00

Olá, equipe. Esta aula explica o pacote local de apresentação do Transurban. Vamos entender o site, a API, o banco de dados e a análise do arquivo CSV. A aula usa os arquivos realmente encontrados neste computador e a adaptação preparada para a apresentação. O objetivo é conseguir demonstrar cada parte e explicar o caminho dos dados. O site é uma demonstração acadêmica. O banco e as requisições da API funcionam localmente.

### 2. Como abrir a apresentação — 00:00:27

Neste notebook, abra o arquivo chamado abrir apresentação, com extensão CMD. Ele usa o ambiente Python já existente e inicia o servidor na porta oito mil. O inicializador abre três páginas: a documentação da API, o site e o painel da apresentação. O servidor roda em segundo plano e registra mensagens no arquivo servidor ponto log. Em outro computador, é necessário ter Python instalado, executar primeiro preparar outro computador e ter internet para instalar as bibliotecas. Faça isso antes da aula, nunca na hora de apresentar.

### 3. Arquitetura: caminho do pedido — 00:01:01

A API é uma ponte para o sistema conversar com os dados. O navegador envia uma requisição HTTP. A biblioteca FastAPI escolhe a função responsável pela rota. O Pydantic verifica se o corpo enviado possui os campos e tipos esperados. O SQLAlchemy acessa o banco SQLite. A função devolve uma resposta em JSON. No console e no Swagger, conseguimos observar esse caminho. Atenção: o site demonstrativo em barra app usa dados próprios no navegador e não foi integrado aos cadastros dessa API. O painel e o console, sim, consultam a API local.

### 4. database.py · conexão e sessão — 00:01:37

O arquivo database ponto py configura o banco. Neste pacote, usamos SQLite para dispensar Supabase e credenciais durante a apresentação. O banco fica no arquivo apresentação ponto sqlite três. A engine representa o acesso ao banco. SessionLocal cria sessões para consultar e salvar dados. A instrução pragma foreign keys igual on ativa a verificação de chaves estrangeiras. Isso evita cadastrar uma linha ligada a uma cidade inexistente, mesmo quando alguém tenta inserir o registro diretamente no banco. Esta escolha facilita a demonstração local, sem comprovar que o sistema já está preparado para produção.

### 5. models.py · tabelas e relações — 00:02:14

O arquivo models ponto py descreve as tabelas. Cidade possui um identificador inteiro e um nome. Linha de ônibus possui identificador, código, nome e o identificador da cidade. A chave primária identifica cada registro. A chave estrangeira conecta uma linha à cidade correta. Uma cidade pode ter várias linhas, e cada linha cadastrada aponta para uma cidade. O relacionamento do SQLAlchemy permite acessar o nome da cidade a partir do objeto da linha. Por isso usamos o identificador da cidade no cadastro da linha: ele é a referência do relacionamento, não o nome digitado livremente.

### 6. schemas.py · validação — 00:02:50

O arquivo schemas ponto py define os formatos aceitos pela API. O model descreve o banco. O schema descreve os dados que entram e saem. CidadeCreate exige um nome válido. LinhaCreate exige código, nome e um identificador de cidade maior que zero. Espaços no início e no fim são removidos. Há limites de tamanho para os textos. Os schemas de resposta mostram os campos devolvidos ao navegador. Quando enviamos nome vazio, tipo errado ou identificador zero, o FastAPI devolve código quatrocentos e vinte e dois. Isso indica falha na validação da entrada.

### 7. main.py · GET, POST e erros — 00:03:26

No arquivo main ponto py estão as rotas originais de cadastro. GET consulta os registros sem criar novos. POST cria um registro e retorna duzentos e um. Ao cadastrar uma linha, a função verifica se a cidade existe. Se não existir, devolve quatrocentos e quatro. A função salvar adiciona o objeto, confirma a transação com commit e atualiza seus campos com refresh. Se ocorrer uma violação de restrição, ela desfaz a transação com rollback e devolve quatrocentos e nove. A sessão é fechada ao terminar o pedido. O lifespan cria as tabelas necessárias na inicialização.

### 8. Demonstração da API — 00:04:02

Para demonstrar, abra barra docs. Em post cidades, clique em Try it out, preencha o nome Maringá e execute. Copie o identificador recebido na resposta. Depois abra post linhas. Informe código DEMO zero um, nome Linha de demonstração e o identificador real da cidade que acabou de criar. Execute e confira o código duzentos e um. Por fim, execute get linhas e mostre o registro com o nome da cidade. Se o Swagger não carregar por falta de internet, use barra console. Esse console é um arquivo local e envia as mesmas requisições para a API, sem depender de uma biblioteca externa de interface.

### 9. CSV · origem e limites — 00:04:39

Na parte de Ciência de Dados, usamos o arquivo atrasos ponto CSV. CSV é uma tabela em texto, com linhas e colunas. Esta versão contém uma massa de teste sintética, identificada nas observações do próprio arquivo. Ela não é uma medição de atrasos reais nem a base pública de Curitiba mencionada na conversa anterior. Não apresentem os números daquele roteiro como se fossem os resultados desta versão. Antes de falar os indicadores, consultem a rota barra IA barra resumo e usem os valores realmente exibidos. Os cálculos são reais sobre uma amostra fictícia.

### 10. Pandas · qualidade e indicadores — 00:05:15

O arquivo dados acadêmicos ponto py lê o CSV com Pandas. O campo código da linha é lido como texto para preservar zeros à esquerda. A rota qualidade conta valores ausentes, duplicados, datas inválidas e atrasos negativos. Também verifica se o tempo real menos o programado corresponde ao atraso registrado. A rota resumo calcula a quantidade de registros, a média, a mediana e o maior atraso. Média é a soma dividida pela quantidade. Mediana é o valor central dos dados ordenados. A função groupby agrupa os registros por cidade, clima, período, trânsito ou código da linha.

### 11. Fonte, hash e Ciência de Dados — 00:05:52

A rota fonte mostra a natureza sintética e o hash SHA duzentos e cinquenta e seis do arquivo atual. O hash identifica o conteúdo: se o arquivo mudar, a assinatura muda. Nesta versão, ele serve para rastrear a fonte usada, mas não há comparação automática com uma assinatura oficial confiável. Para a apresentação, Jullyany pode explicar o CSV, a origem e a qualidade. Camila pode mostrar o resumo e o agrupamento por cidade. Se perguntarem onde está a inteligência artificial, expliquem com precisão: esta etapa trabalha preparação e análise descritiva de dados. Não treinamos um modelo de previsão de chegada.

### 12. Demonstração do site — 00:06:29

No site, comecem pela página inicial. Abram explorar linhas, pesquisem zero dez e mostrem os detalhes. Entrem no perfil demonstrativo de passageiro, selecionem o ponto fictício e simulem o embarque. Mostrem a chegada simulada e a avaliação com nota, descrição e lotação. Depois troquem para o perfil de motorista, encerrem a viagem e iniciem outra. Esses perfis não são contas autenticadas de produção. O mapa, a posição do ônibus e os tempos do cenário são simulados. Não apresentem essa tela como rastreamento de frota, integração oficial ou navegação real de ônibus.

### 13. Arquivos que unem o pacote — 00:07:06

O arquivo apresentação ponto py reúne a API original, as rotas de análise e os arquivos estáticos do site. O inicializador iniciar ponto py verifica a saúde do servidor e o inicia quando necessário. O painel organiza os links para a equipe. O console usa a função fetch do JavaScript para enviar requisições reais. Os códigos da API estão em Python. O banco é acessado com SQLAlchemy. A interface usa HTML para a estrutura, CSS para o visual e JavaScript para as interações. O arquivo de requisitos lista as bibliotecas necessárias. A execução é local e restrita ao próprio computador.

### 14. Ensaio final · o que dizer — 00:07:45

Antes da apresentação, façam um ensaio completo no computador da sala. Confiram a abertura do site, uma consulta na API e o resumo do CSV. Não apaguem a pasta enquanto o servidor estiver em execução. Se ocorrer erro, consultem servidor ponto log. Cada participante deve entender o fluxo navegador, rota, validação, banco e resposta. Expliquem que pagamentos, frota e previsão operacional ainda exigem integrações externas e não foram validados neste pacote. A melhor apresentação é mostrar o que funciona, explicar como funciona e distinguir claramente o protótipo das funções que ainda precisam ser desenvolvidas.

### 15. Leia o código · rotas e sessão — 00:08:24

Vamos olhar algumas linhas importantes do código. A instrução from fastapi import carrega os recursos que vamos usar. FastAPI cria a aplicação. O símbolo arroba antes de app ponto get é um decorador: ele associa a função logo abaixo a uma rota HTTP. O nome da função pode ser listar cidades, mas é o caminho barra cidades que o cliente usa. Na assinatura da função, Depends, recebendo get db, pede ao FastAPI uma sessão do banco. A função get db abre a sessão e usa yield para entregá-la à rota. O bloco finally fecha a sessão quando o trabalho termina, mesmo quando ocorre uma exceção. As linhas indentadas pertencem ao bloco acima. Essa organização evita conexões esquecidas e separa a infraestrutura da regra da rota.

### 16. Leia o código · salvar e responder — 00:09:09

No cadastro, models ponto Cidade cria um objeto Python representando o novo registro. O valor cidade ponto nome já passou pelo schema de validação. A função salvar recebe esse objeto. Add coloca o registro na sessão. Commit confirma a transação, gravando a mudança no banco. Refresh busca os valores atualizados, incluindo o identificador gerado pelo banco. Se houver um erro de integridade, o except captura essa situação e rollback desfaz a transação. Depois, a API devolve um erro HTTP controlado. Quando a rota retorna o objeto salvo, o schema de resposta escolhe os campos e o FastAPI os transforma em JSON. Chaves e valores formam um objeto JSON; uma consulta de vários registros devolve uma lista desses objetos. Cadastro e consulta usam o mesmo banco local, por isso os registros continuam disponíveis depois de uma nova requisição.

### 17. Leia o código · Pandas e agrupamento — 00:10:02

Na leitura do CSV, pd é o apelido da biblioteca Pandas e read CSV produz uma tabela chamada DataFrame. O argumento dtype informa que o código da linha deve ser texto. Assim, zero dez não perde o zero inicial. A expressão df ponto minutos atraso seleciona uma coluna. Mean calcula a média e median calcula a mediana. No agrupamento, groupby reúne os registros pelo campo escolhido. Depois selecionamos a coluna de atraso e usamos agg para calcular contagem, média, mediana e máximo de cada grupo. Reset index transforma a chave de cada grupo em uma coluna comum. Rename dá nomes claros aos resultados. Por fim, to dict, com orient igual a records, transforma cada linha em um dicionário, formando uma lista que pode ser devolvida como JSON. A lista de campos permitidos impede agrupamentos por colunas inexistentes.

### 18. Como comprovamos o funcionamento — 00:10:53

O arquivo verificar ponto py inicia uma instância da API usando um banco temporário. Ele não apaga nem substitui os cadastros da apresentação. Os testes verificam páginas, cadastro de cidade, cadastro de linha, consulta, entradas inválidas, cidade inexistente e chave estrangeira. Também comparam contagem, média e mediana do CSV com cálculos independentes da biblioteca statistics. Cada agrupamento precisa preservar o total de registros. O material da aula precisa abrir, e o vídeo precisa aceitar leitura parcial para reprodução. São trinta e nove verificações nessa versão. O pacote também é extraído e testado novamente. Esses testes dão evidência do comportamento verificado, mas não são uma promessa de ausência de qualquer erro em qualquer computador. Para amanhã, ensaiem também no equipamento da sala. Nenhum commit ou envio ao GitHub foi realizado nesta etapa; a entrega aqui é o pacote local, com código, guia, evidências e videoaula.


## Resultados conferidos nesta versão

33 verificações HTTP e de integridade passaram em banco temporário isolado (ver EVIDENCIAS-TESTES.json).
CSV: 180 registros, 17 códigos de linha, média de atraso 7,57 minutos, mediana 8 minutos e máximo 12 minutos.
Não foram encontrados nulos, duplicados, datas inválidas, atrasos negativos nem inconsistências entre os tempos.
Todos esses indicadores se referem exclusivamente à amostra sintética de agosto de 2026.

## O que foi preservado e adaptado

main.py, models.py e schemas.py foram copiados da API local existente, sem alterações de comportamento.
database.py foi adaptado para SQLite local. apresentacao.py integra as páginas e as novas rotas de análise.
dados_academicos.py calcula os resultados efetivamente disponíveis no CSV encontrado.
O site foi copiado da apresentação offline disponível em Downloads/apresentacao-transurban.
O texto REFERENCIA-analise-original.txt é uma cópia de consulta do script antigo. Seus caminhos pertencem ao projeto antigo. O código executado pela API neste pacote é backend/dados_academicos.py.

## Checklist da equipe

- Extraia o pacote; não execute dentro do ZIP.
- Neste notebook, abra ABRIR-APRESENTACAO.cmd.
- Confira /health, /docs e /app/. Use /console se o Swagger não carregar.
- No site, reinicie o cenário pelo botão Reiniciar antes de ensaiar.
- Cadastre uma cidade na API e copie o ID para cadastrar a linha. Não presuma que o ID será sempre 1.
- Para verificar novamente: execute o Python do ambiente com verificar.py. Os testes não alteram o banco da apresentação.
- Faça um ensaio no computador da sala e no projetor. A primeira instalação em outra máquina exige internet e Python.
- Não use o roteiro antigo com 71.086 registros de Curitiba para explicar este CSV de 180 registros sintéticos.

## Divisão sugerida para Ciência de Dados

Jullyany: explique o que é CSV, informe a origem sintética e abra /ia/fonte e /ia/qualidade.
Camila: abra /ia/resumo e /ia/agrupamentos/cidade, explique média, mediana e agrupamento.
Fala final: “Esta análise descreve uma amostra de teste. Não treinamos um modelo de IA e não estimamos chegadas reais.”

## Versionamento

Este trabalho foi salvo como pacote local. Nenhum commit, envio ao GitHub ou publicação em hospedagem foi realizado nesta etapa.
O serviço é restrito ao próprio computador, no endereço 127.0.0.1. O site continua demonstrativo; não há GPS real, pagamento real nem integração operacional à frota.
