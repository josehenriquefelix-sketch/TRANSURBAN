# TRANSURBAN
## Guia técnico e roteiro da avaliação de backend DS + IA

Preparado em 05/10/2026 para José Henrique Felix e equipe. CEEP Maringá. Professor de referência: Giuliano Alencar.

O TRANSURBAN propõe melhorar a informação sobre o transporte entre Maringá e Sarandi. Nesta avaliação, a entrega reúne cadastro de cidades e linhas de ônibus, consulta de seus relacionamentos e análise descritiva de atrasos a partir de CSV.

**O que foi feito nesta revisão:** recuperação do pacote anterior; comparação do código existente; instalação das dependências; revisão da validação da fonte; execução de 18 testes; execução de 20 requisições HTTP reais; exportação dos indicadores; conferência do CSV com o GitHub; atualização dos documentos, do roteiro e das evidências.

**Estado comprovado:** API funcionando em Uvicorn com SQLite temporário; cadastros, consultas, nomes relacionados e erros validados; cálculos e agrupamentos conferidos. O CSV é idêntico ao arquivo do repositório no commit 2d3d554e4153ffc8cc3e39cbaf6b5d5385b87dee.

**Etapa ainda dependente do ambiente da equipe:** conectar a API ao PostgreSQL/Supabase e verificar a persistência remota. Não há credenciais privadas neste pacote. SQLite permite o ensaio local, mas não comprova o requisito de PostgreSQL da avaliação DS.

GPS em tempo real, previsão de chegada, recarga de passes e login de motorista/passageiro pertencem à evolução do aplicativo. Este backend não implementa essas integrações. O professor poderá testar o escopo pedido usando /docs ou Postman. A interface visual é prevista para a etapa seguinte no caderno IA.

---

## 1. Como executar e retomar

Extraia o pacote e abra sua pasta no VS Code. Execute os comandos a partir da pasta que contém requirements.txt, backend e data. A pasta BACKEND antiga do computador pode conter outro código; confirme o caminho antes de iniciar.

**Linux, incluindo o ambiente escolar:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m backend.analise
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Abra http://127.0.0.1:8000/docs. Sem DATABASE_URL, a aplicação cria transurban_local.db para ensaio local. Não sobrescreva um .env já configurado; nesse caso, pule o comando de cópia.

**Windows PowerShell, sem depender de ativação:**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Para demonstrar a ativação no Windows, use .venv\Scripts\activate.bat no CMD ou .\.venv\Scripts\Activate.ps1 no PowerShell. Se o PowerShell bloquear a ativação, use o executável explícito acima ou CMD.

**Testes, em outro terminal na mesma pasta:** python -m unittest discover -s tests -v. Para exportar indicadores: python scripts/exportar_ia.py. Para registrar HTTP real: python scripts/capturar_http.py. Esse último usa banco descartável e encerra seu próprio servidor.

Para parar a API, pressione Ctrl+C no terminal do Uvicorn. Depois use deactivate se ativou a venv. Para retomar, reative o ambiente e execute novamente Uvicorn. Parar não apaga os dados. Se a porta 8000 estiver ocupada, use --port 8001 e abra /docs nessa porta.

---

## 2. O que usamos e por quê

| Recurso | Uso no TRANSURBAN |
|---|---|
| Python | Funções, organização em módulos, leitura da fonte e testes |
| FastAPI | Rotas HTTP e documentação interativa |
| Uvicorn | Servidor que executa a aplicação FastAPI |
| SQLAlchemy | Mapeamento de tabelas, consultas, sessões e relacionamentos |
| Pydantic | Validação de entradas e contrato de respostas |
| psycopg2-binary | Driver para PostgreSQL/Supabase |
| python-dotenv | Leitura das configurações privadas no .env |
| Pandas e NumPy | Leitura tabular, validação numérica e agregações |
| unittest e httpx | Verificação automatizada e requisições HTTP |
| SQLite | Banco temporário utilizado no ensaio e nos testes locais |
| Git/GitHub | Versionamento e entrega do código |

requirements.txt registra dependências diretas; requirements.lock.txt registra as versões usadas no ensaio. O ambiente executado utilizou Python 3.12.14. VS Code é o editor recomendado pelo material, e Postman é uma alternativa para testar as rotas com a coleção incluída.

| Arquivo | Responsabilidade |
|---|---|
| database.py | Carrega configuração, cria engine e entrega uma sessão por requisição |
| models.py | Mapeia cidade e linha_onibus; define PK, FK e relationship |
| schemas.py | Define entradas obrigatórias, limites e formato de saída |
| main.py | Recebe HTTP, chama validações, persiste e devolve JSON |
| analise.py | Lê, audita e calcula os indicadores do CSV |
| .env | Conexão privada; ignorada pelo Git |

No cadastro, o JSON passa pelo schema, a rota cria um objeto do model, a sessão confirma a gravação e a API devolve a resposta. Na análise, a rota lê o CSV, verifica sua qualidade e chama as funções de cálculo. As análises IA não consultam o banco DS.

---

## 3. DS: tabelas, chaves e demonstração

O exemplo didático Categoria e Produto foi adaptado para Cidade e Linha de ônibus. Uma cidade pode estar associada a várias linhas; cada linha referencia uma cidade nesse recorte.

| Tabela | Campo | Papel |
|---|---|---|
| cidade | id_cidade | PK: identifica uma cidade |
| cidade | nome | Nome obrigatório |
| linha_onibus | id_linha | PK: identifica uma linha |
| linha_onibus | id_cidade | FK: referencia cidade.id_cidade |
| linha_onibus | codigo e nome | Identificação textual da linha |

ForeignKey estabelece a referência no banco. relationship permite navegar no Python: linha.cidade.nome. O banco guarda o identificador; a API também devolve o nome para facilitar a compreensão do usuário.

**Demonstração em /docs:** abra POST /cidades, clique Try it out, envie {"nome":"Maringá"} e clique Execute. Observe HTTP 201 e copie o id_cidade retornado. Se Maringá já existir, o 409 é esperado; use uma cidade de teste inédita ou consulte GET /cidades e reutilize o ID existente.

Abra POST /linhas e envie {"id_cidade":1,"codigo":"001","nome":"Linha acadêmica"}, substituindo 1 pelo ID real. Observe 201 e o campo cidade com o nome. Consulte GET /linhas: o mesmo registro deve aparecer.

Tente cadastrar uma linha com id_cidade=999999, depois de confirmar que esse ID não existe. A API responde 404. Esse teste prova que ela verifica a entidade referenciada antes da gravação. Os testes também verificam que o banco rejeita uma FK inválida diretamente.

Nome vazio, campos extras ou ID não positivo geram 422. Cidade duplicada ou código repetido na mesma cidade geram 409 no esquema criado pelo pacote. O mesmo código pode existir em cidades diferentes. O estado dessas restrições no Supabase legado precisa ser auditado.

---

## 4. Conexão PostgreSQL e evidências DS

O arquivo .env.example mostra como definir DATABASE_URL com a conexão privada do projeto. Copie a conexão do painel Connect do Supabase; use o usuário, host e porta do método escolhido. Chave anon não substitui a senha PostgreSQL. Caracteres especiais da senha precisam estar codificados na URL.

**Sequência para concluir a verificação remota:**

1. Executar sql/01_auditar_supabase.sql e confirmar as tabelas, campos, PK, FK, geração automática de IDs e restrições existentes.
2. Definir DATABASE_URL no .env local, sem publicar a senha.
3. Reiniciar a API e consultar /health. A resposta deve indicar postgresql.
4. Cadastrar uma cidade de teste e uma linha associada; consultar ambas.
5. Confirmar no Table Editor os mesmos IDs, nomes e id_cidade retornados pela API.
6. Guardar respostas e capturas mostrando rota, status e dados; ocultar a configuração privada.

O servidor não cria nem modifica tabelas PostgreSQL ao iniciar. sql/02_criar_recorte_em_banco_novo.sql serve para um banco de testes vazio. O script de IDs do legado só deve ser aplicado se a auditoria comprovar a necessidade. Não execute todos os SQLs em sequência.

**Evidências desta revisão:** testes_completos.txt registra 18 testes aprovados; respostas_http.json registra 20 requisições reais; servidor.log registra o Uvicorn. Os testes usam SQLite temporário. Eles comprovam o fluxo local, não uma execução no projeto Supabase.

**Como explicar os códigos HTTP:** 200 indica consulta bem-sucedida; 201 indica criação; 404 indica referência ou recurso não encontrado; 409 indica conflito; 422 indica entrada ou fonte inválida; 503 indica fonte inacessível ou erro de banco. O rollback desfaz uma transação que falhou antes de continuar usando a sessão.

GET /health verifica a conexão com SELECT 1; sozinho, não comprova compatibilidade das tabelas. POST e GET das entidades são necessários para demonstrar a persistência.

---

## 5. IA: origem, unidade e dicionário

A base tem 180 observações sintéticas, entre 01/08/2026 e 31/08/2026. Seus bytes são idênticos ao CSV atual do GitHub. Ser o arquivo do repositório não transforma a fonte em dado real: a própria observação de cada registro informa que é massa sintética acadêmica.

Cada linha representa uma observação de atraso de uma linha em um trecho e data. Não existe id_viagem; portanto, não podemos afirmar que são 180 viagens completas, contar passageiros ou ônibus únicos, nem somar minutos perdidos por todos os usuários.

| Campo | Significado e unidade |
|---|---|
| data_registro | Data da observação, AAAA-MM-DD |
| cidade | Cidade associada à linha, texto |
| codigo_linha | Código textual; mantém zeros como 001 |
| nome_linha | Nome descritivo da linha |
| trecho | Segmento observado |
| tipo_trecho | Categoria do segmento |
| periodo | Faixa do dia |
| condicao_transito | Categoria de intensidade do trânsito |
| clima | Condição climática |
| tempo_programado_min | Tempo previsto, minutos positivos |
| tempo_real_min | Tempo observado, minutos não negativos |
| minutos_atraso | Atraso não negativo, em minutos |
| observacao | Contexto opcional do registro |

Antes de calcular, o código verifica cabeçalho, textos obrigatórios, datas, números finitos, sinais e compatibilidade dos tempos. Também identifica duplicatas e códigos com nomes divergentes. Não preenche falhas com zero e não modifica o CSV.

As funções internas auditam os registros e informam seus problemas. Nas rotas de indicadores, fonte vazia, linha inválida, duplicata ou nome divergente interrompem a análise com 422 até correção ou justificativa. /ia/qualidade permite inspecionar os problemas quando o cabeçalho pode ser lido. CSV inacessível gera 503.

---

## 6. Cálculos que você pode explicar

**Um registro:** a primeira observação tem 29 minutos programados e 34 minutos reais. Pela convenção adotada, atraso = max(tempo real - tempo programado, 0). Portanto, max(34 - 29, 0) = 5 minutos. Se o tempo real fosse menor, o atraso seria zero; antecipação não é registrada como atraso negativo.

**Um agrupamento completo:** para Maringá, código 031, há 12 observações. Os atrasos são 9, 10, 7, 7, 11, 9, 8, 9, 11, 11, 8 e 8 minutos; confira evidencias/conferencia_manual.json. A soma é 108 minutos e a média é 108 / 12 = 9 minutos. É um grupo de observações, não uma viagem completa; substitui a compra inteira do exemplo genérico de IA.

| Indicador | Resultado conferido |
|---|---:|
| Observações válidas | 180 |
| Soma dos atrasos das observações | 1362 min |
| Média: 1362 / 180 | 7,5667 min |
| Mediana | 8 min |
| Maior atraso | 12 min |
| Observações empatadas no máximo | 7 |
| Observações acima de 10 minutos | 26 |
| Percentual: 26 / 180 x 100 | 14,4444% |
| Pares distintos cidade/código | 17 |

Para a mediana, ordenamos os 180 atrasos e usamos a média entre os valores nas posições 90 e 91, contando a partir de 1. Ambos são 8; a mediana é 8.

A conferência independente usa csv e statistics, além de somas diretas. Em cada dimensão, a soma das contagens dos grupos deve ser 180 e a soma dos atrasos deve ser 1362. Todos os agrupamentos satisfizeram essas duas relações.

Não use a média simples das médias dos grupos para representar a média geral quando os tamanhos diferem. Use soma dos totais dividida pela soma das contagens. Os cálculos usam a precisão da fonte; os resultados são arredondados para quatro casas na saída. A interface pode mostrar 7,57 min.

---

## 7. Perguntas de negócio e JSON para o dashboard

| Pergunta autoral | Resultado e rota | Visual futuro |
|---|---|---|
| Qual atraso típico aparece na base? | /ia/resumo: média 7,5667 e mediana 8 min | Cartões com unidade |
| Quais linhas têm maior média? | /ia/agrupamentos/linha: 031 e 324 de Maringá empatam em 9 min | Barras com contagem |
| Como os atrasos variam por data? | /ia/agrupamentos/data: contagem e média de cada dia | Série temporal |
| Onde estão os maiores atrasos? | /ia/maiores-atrasos: 7 observações de 12 min | Tabela com todos os empates |

As duas linhas com média 9 têm 12 observações e soma 108 cada. O pico da tarde tem média 9,8444 min sobre 45 observações. Esses valores descrevem esta massa didática; não permitem classificar a operação real das empresas.

**Três respostas obrigatórias adaptadas:** resumo, agrupamento por linha e agrupamento por data. Estão em evidencias/calculos_ia/resumo.json, por_linha.json e por_data.json. As respostas HTTP integrais estão em evidencias/http/respostas_http.json.

/ia/resumo retorna um objeto com contagens, média, mediana, máximo, período e limitações. /ia/agrupamentos/linha e /data retornam um objeto com dimensão, fonte, hash, total válido e a lista resultados. Cada grupo inclui observacoes, atraso_total_min, atraso_medio_min, atraso_mediano_min e maior_atraso_min.

O frontend deverá acessar resultados no JSON dos agrupamentos. Números JSON usam ponto decimal; a exibição em português é responsabilidade da interface. Datas sem registros não são preenchidas com zero, porque ausência de observação não prova pontualidade.

O CSV e os cadastros DS são fontes distintas nesta avaliação. Cadastrar uma cidade ou linha não altera o CSV nem recalcula uma fonte operacional externa. Agrupar por trânsito ou clima mostra associação, sem demonstrar causa. Não há treinamento de modelo preditivo nesta etapa.

---

## 8. Fala pronta para a apresentação

Use este roteiro como apoio, entendendo os arquivos antes de falar. Atribua a cada integrante apenas a ação que ele realmente executou ou consegue demonstrar.

“Boa tarde. Nosso projeto é o TRANSURBAN, voltado à informação sobre o transporte entre Maringá e Sarandi. Nesta avaliação, preparamos o backend de cadastro e consulta e uma análise de atrasos usando CSV.

Na parte de Desenvolvimento de Sistemas, adaptamos o exemplo de Categoria e Produto para Cidade e Linha de ônibus. Cidade tem uma chave primária. Linha tem sua própria chave primária e uma chave estrangeira que aponta para a cidade. Antes do cadastro, verificamos se a cidade existe.

Usamos Python, FastAPI, SQLAlchemy e Pydantic. A conexão fica em database.py; as tabelas, em models.py; os formatos de entrada e saída, em schemas.py; e as rotas, em main.py. O banco guarda id_cidade, e a consulta também devolve o nome da cidade para facilitar a leitura.

Agora vamos demonstrar um cadastro, uma consulta e uma tentativa com cidade inexistente. Os testes verificaram respostas de sucesso e de erro. Nesta preparação, foram aprovados 18 testes automatizados e 20 requisições HTTP reais com banco temporário local. A comprovação no Supabase deve ser feita com a conexão da equipe antes de afirmarmos que houve gravação remota.

Na parte de Ciência de Dados, usamos Pandas para analisar 180 observações de um CSV sintético acadêmico. Cada linha é uma observação por trecho, data e linha de ônibus, e não uma viagem completa. O arquivo foi comparado com o GitHub e é idêntico à fonte do projeto.

A soma dos atrasos é 1362 minutos por observação. Dividindo por 180, obtemos média de aproximadamente 7,57 minutos. A mediana é 8 e o maior atraso é 12 minutos, com sete observações empatadas. Conferimos um registro, um agrupamento inteiro e a reconciliação dos totais.

Essas respostas são entregues em JSON para o dashboard da próxima etapa. A proposta futura do aplicativo inclui localização de ônibus e previsão de chegada, mas essas funções dependem de dados reais e integrações. Nesta avaliação, demonstramos o backend e a análise descritiva, com origem e limitações documentadas.”

---

## 9. Perguntas técnicas prováveis e respostas

Estas perguntas foram selecionadas a partir dos critérios dos cadernos e da documentação técnica oficial. São preparação para a banca, não uma lista comprovada de perguntas feitas pelo professor.

**1. Para que serve a venv?** Isola as bibliotecas do projeto. Outra pessoa pode recriar o ambiente usando requirements.txt.

**2. O que é uma API?** É a interface que recebe requisições e devolve respostas. Aqui, permite cadastrar e consultar cidades e linhas e obter análises em JSON.

**3. Qual a diferença entre GET e POST?** GET consulta dados. POST envia dados para criar um registro nas rotas de cadastro.

**4. O que são PK e FK?** PK identifica um registro de forma única. FK referencia um registro de outra tabela. linha_onibus.id_cidade aponta para cidade.id_cidade.

**5. ForeignKey e relationship são a mesma coisa?** Não. ForeignKey define a referência no banco; relationship permite navegar pelos objetos Python relacionados.

**6. Por que devolver a cidade por nome?** O identificador mantém a relação estável no banco. O nome ajuda o consumidor da API a entender o resultado.

**7. Models e schemas são iguais?** Models representam as tabelas e relações do banco. Schemas validam os dados enviados e definem o formato das respostas.

**8. O que fazem add, commit e refresh?** add coloca o objeto na sessão; commit confirma a transação; refresh relê os valores persistidos, incluindo o ID gerado.

**9. O que acontece se a cidade não existir?** A rota responde 404 e não cria a linha. A FK no banco também protege a integridade.

**10. Por que fechar a sessão?** Para liberar os recursos usados pela requisição. A dependência get_db abre a sessão e o contexto a fecha ao terminar.

**11. Por que não publicar .env?** Ele pode conter a senha do banco. O Git ignora .env; .env.example mostra somente o formato de configuração.

**12. Como provar que funcionou?** Mostrar testes aprovados, respostas HTTP, cadastrar e consultar durante a demonstração. Para Supabase, comparar os mesmos IDs na API e no banco remoto.

---

## 10. Perguntas de dados e de produto

**13. Os dados são reais?** Não. São sintéticos para validação acadêmica, embora estejam no repositório oficial do projeto. Não representam telemetria real.

**14. São 180 viagens?** Não podemos afirmar. São 180 observações; falta um identificador de viagem completa.

**15. Como calcularam o atraso?** max(tempo real - tempo programado, 0). A primeira linha tem 34 - 29 = 5 minutos.

**16. Média e mediana são iguais?** A média é soma dividida pela quantidade. A mediana é o centro dos valores ordenados. Nesta fonte, são 7,5667 e 8 minutos.

**17. Qual linha tem o maior atraso?** O máximo por observação é 12 min e ocorre em sete registros; mostramos todos. A maior média por linha é 9 min, com empate entre 031 e 324 de Maringá. São perguntas diferentes.

**18. Como evitar números incorretos?** Validar a fonte, preservar códigos textuais, usar o mesmo denominador e reconciliar contagens e somas. Os testes também conferem cálculos com csv/statistics.

**19. O trânsito causou os atrasos?** A base permite comparar grupos, mas não provar causalidade. Ela é sintética e não controla outros fatores.

**20. Onde está a inteligência artificial?** Esta etapa é Ciência de Dados descritiva: validação, estatísticas e agregações. Não treinamos um modelo. Uma previsão futura exige dados históricos reais, validação e avaliação do erro.

**21. Como estimariam a chegada do ônibus?** Seria necessário integrar GPS, rota, paradas, horários e histórico de deslocamento. Essa previsão ainda não é uma funcionalidade comprovada deste backend.

**22. O app já recarrega passe?** Não neste escopo. A recarga dependerá de integração com operadora e sistema de pagamento, além de conciliação das transações.

**23. Por que usar CSV em IA se DS tem banco?** A avaliação IA exige analisar a fonte CSV sem conexão de dados ao banco. DS demonstra persistência relacional. O mesmo app FastAPI reúne as rotas, mantendo as responsabilidades separadas.

**24. O sistema está pronto para produção?** Está preparado para demonstração acadêmica local no escopo testado. Produção exige autenticação, autorização, implantação, monitoramento, dados operacionais e validação das integrações.

---

## 11. Checklist antes de apresentar e fontes

1. Extrair o pacote e selecionar a pasta correta no VS Code.
2. Instalar dependências e executar os testes; conferir OK.
3. Executar python -m backend.analise e explicar a origem do CSV.
4. Iniciar a API e acessar /docs.
5. Ensaiar POST/GET de cidade e linha usando IDs realmente retornados.
6. Mostrar 404 de FK inexistente e 422 de entrada inválida.
7. Consultar resumo, agrupamento por linha e por data.
8. Mostrar a conferência manual, média, mediana e empates no máximo.
9. Concluir conexão e teste de persistência Supabase antes de alegar gravação remota.
10. Confirmar o commit GitHub em versionamento/PUBLICACAO.json.
11. Conferir capturas de /docs; se ausentes, capturar rota, status e resposta no computador da equipe.
12. Registrar a atuação individual na ficha; deixar notas para o professor.

**Equipe da ficha:** José Henrique Felix (líder/backend), Kauan Celso Pereira (banco), Bruno Miguel, Ana Carolina e Gustavo Sacardo (frontend), Jullyany de Melo (engenheira de prompts) e Camila Ghezzi (cientista de dados). Números, turmas e cursos constam em EQUIPE_E_ENTREGA.md. Confirmar as ações pessoais no momento da entrega.

**Materiais utilizados:** três PDFs enviados pelo usuário: ficha integradora, caderno DS e caderno IA; pacote anterior TRANSURBAN_Avaliacao_Backend_DS_IA.zip; fonte do repositório no commit 2d3d554e.

**Documentação consultada para as explicações:**

- FastAPI, modelos de resposta: https://fastapi.tiangolo.com/tutorial/response-model/
- FastAPI, dependências com yield: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
- FastAPI, testes: https://fastapi.tiangolo.com/tutorial/testing/
- Pandas, leitura de CSV: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- Pandas 2.2, agrupamentos: https://pandas.pydata.org/pandas-docs/version/2.2/user_guide/groupby.html

O guia usa essas fontes como apoio técnico. A escolha das perguntas e a fala são uma adaptação aos critérios do TRANSURBAN. As evidências permitem distinguir o resultado observado do que ainda precisa ser demonstrado pela equipe.
