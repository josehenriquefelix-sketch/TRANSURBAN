# TRANSURBAN — Roteiro completo de DS

Apresentação de Desenvolvimento de Sistemas • 20/10/2026 • Sem slides

Equipe desta parte: José Henrique, Bruno, Kauan, Gustavo e Ana Carolina.
Duração sugerida: 7 a 9 minutos, incluindo cliques e respostas da API. José Henrique pode operar o computador durante todas as falas. Bruno e Kauan ficam com as partes mais curtas. Esta divisão de falas não atribui autoria individual do código.

## Como usar este documento

Os parágrafos iniciados por “FALA” são para apresentar. “NA TELA” e “APOIO” são instruções: não precisam ser lidos ao público. Esperem a resposta real antes de explicar o resultado. Este roteiro é somente de DS; a apresentação de IA está em outro documento.

## Preparação antes de o público entrar

Extraia o pacote inteiro e abra a pasta backend_escola no VS Code. Python 3.12 e internet são necessários para a primeira instalação. Não execute dentro do ZIP e não copie ambiente virtual Windows para Linux.

No Windows, execute um comando de cada vez:

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

Aguarde Application startup complete. Deixe o terminal aberto. No navegador DESSE computador, digite http://127.0.0.1:8000/docs. Confira também http://127.0.0.1:8000/health: status ok e banco sqlite_local. Se a porta estiver ocupada, use iniciar_apresentacao.py --port 8002 e troque 8000 por 8002 nas URLs.

O inicializador usa SQLite local e preserva o .env. Não exige senha de Supabase. A conexão remota não foi comprovada; não a anunciem no palco. Depois da preparação, Swagger, cadastros e consultas locais podem funcionar sem internet. Isso não significa que mapa e clima do site funcionem sem rede.

A suíte completa da entrega foi validada com 41 testes na nuvem Linux; a contagem inclui outras partes do projeto. Não anunciem “41 testes só de DS”. Confiram a execução no notebook da equipe e ensaiem a projeção. Windows, GPS físico e projetor exigem conferência no equipamento real.

Abra no VS Code: database.py, models.py, schemas.py e main.py. Não mostre .env ou senhas. No navegador, ajuste o zoom para leitura no telão. Não instale dependências durante a fala.

## 1. José Henrique — abertura

FALA: “Bom dia, pessoal! Eu sou o José Henrique e, junto com o Bruno, o Kauan, o Gustavo e a Ana Carolina, vou apresentar a parte de Desenvolvimento de Sistemas do TRANSURBAN.

FALA: Nosso projeto foi pensado para a mobilidade em Maringá e Sarandi. Nesta apresentação, vamos mostrar a API: a parte que recebe os pedidos, valida as informações, conversa com o banco e devolve uma resposta.

FALA: Vamos cadastrar uma cidade, vincular uma linha a ela e consultar o que foi salvo. Depois, vamos enviar dados inválidos de propósito para verificar como o sistema reage.

FALA: A demonstração usa um banco local neste computador. O código DEMO-20 será apenas um cadastro de teste, não uma linha operacional verificada. O Bruno vai explicar o objetivo desse cadastro.”

NA TELA: Swagger aberto. Se necessário, mostre GET /health, Try it out e Execute. Leia a resposta em Server response; Example Value é só um exemplo.

## 2. Bruno — objetivo dos cadastros, fala curta

FALA: “Nosso sistema organiza cidades e linhas de ônibus. Primeiro cadastramos a cidade. Depois, cadastramos uma linha ligada a ela. Assim conseguimos consultar a linha e saber a qual cidade ela está vinculada. Agora o Kauan vai explicar a consulta.”

APOIO: Bruno não precisa operar o computador nem explicar bibliotecas. Pode falar com calma, em aproximadamente 20 segundos.

## 3. Kauan — o que é GET, fala curta

FALA: “Consultar é pedir para ver uma informação que já está salva. Na API, usamos GET para isso. Ele mostra os dados sem fazer um novo cadastro. O José Henrique vai mostrar como cadastramos e consultamos na prática.”

APOIO: Kauan não precisa executar comandos. A fala pode durar aproximadamente 20 segundos.

## 4. José Henrique — organização dos arquivos

NA TELA: mostre brevemente os quatro arquivos no VS Code, sem percorrer todo o código.

FALA: “Organizamos o código em arquivos com responsabilidades diferentes. O database.py configura a conexão com o banco. O models.py define as tabelas e os relacionamentos. O schemas.py valida os dados recebidos e organiza as respostas. O main.py disponibiliza as rotas da aplicação.

FALA: Usamos Python com FastAPI para a API. O SQLAlchemy trabalha com o banco de dados, e o Pydantic faz as validações. Essa separação facilita entender o código e encontrar onde uma alteração deve ser feita.”

APOIO: uma sessão de banco é fornecida para a operação e depois encerrada. commit confirma a transação; rollback desfaz uma transação que falhou. Não é necessário falar esses detalhes se o professor não perguntar.

## 5. José Henrique — cadastrar a cidade

NA TELA: volte ao Swagger. Abra POST /cidades → Try it out. Envie:

```json
{"nome":"Sarandi"}
```

NA TELA: clique Execute. Espere 201 e anote o id_cidade que realmente apareceu. Não assuma que é 1. Se já existem cadastros do ensaio, os IDs podem ser outros.

FALA: “Agora cadastramos Sarandi. POST é o método que usamos para enviar esse cadastro. O código 201 indica que o registro foi criado.

FALA: O campo id_cidade é a identificação da cidade no banco. Ele é a chave primária: permite identificar cada registro de forma única.”

APOIO: no SQLite deste recorte, nome da cidade e código da linha não têm restrição UNIQUE. Repetir o cadastro pode criar outro registro com outro ID. Não prometam erro de duplicidade que esta configuração não implementa. Isso é diferente de outros esquemas PostgreSQL que possam ter restrições adicionais.

## 6. José Henrique — cadastrar a linha e explicar a chave estrangeira

NA TELA: abra POST /linhas → Try it out. Substitua o 1 abaixo pelo id_cidade realmente retornado:

```json
{
  "codigo": "DEMO-20",
  "nome": "Linha da apresentação",
  "id_cidade": 1
}
```

NA TELA: clique Execute. Espere 201. Aponte id_cidade e o nome da cidade na resposta.

FALA: “Agora cadastramos uma linha de demonstração usando a identificação da cidade. O campo id_cidade faz a ligação entre as duas tabelas: ele é a chave estrangeira.

FALA: Neste recorte do sistema, uma cidade pode ter várias linhas cadastradas, e cada linha aponta para uma cidade existente. A API verifica essa existência antes de salvar.

FALA: Essa relação evita deixar uma linha apontando para um registro de cidade que não existe.”

APOIO: esta relação é o recorte cadastral da avaliação. Não representa, sozinha, todos os municípios atravessados por uma linha intermunicipal ou todas as paradas de seu itinerário.

## 7. José Henrique — consultar os registros

NA TELA: execute GET /cidades e depois GET /linhas. Espere 200. Localize o registro criado; não suponha que a lista terá somente um item.

FALA: “Agora consultamos o que acabamos de salvar. O código 200 indica que a consulta foi atendida. A linha aparece acompanhada do nome da cidade, facilitando a leitura da informação.

FALA: Esse formato de campos e valores é chamado JSON. Uma interface pode usar essa resposta para mostrar os dados ao usuário. O Gustavo vai testar o que acontece quando as informações estão erradas.”

## 8. Gustavo — cidade inexistente, erro esperado 404

NA TELA: confira por GET /cidades que o ID 999999 não existe. Em POST /linhas, envie:

```json
{
  "codigo": "TESTE-ERRO",
  "nome": "Tentativa inválida",
  "id_cidade": 999999
}
```

FALA, antes de clicar: “Até aqui usamos dados válidos. Agora vamos informar uma cidade inexistente, de propósito, para testar a validação.”

NA TELA: clique Execute. Esperado: 404 e detail: Cidade não encontrada. Se esse ID existir, escolha outro ID positivo comprovadamente ausente.

FALA: “A API identificou que a cidade não existe e recusou o cadastro. O 404 é o resultado esperado deste teste.”

NA TELA: execute GET /linhas. Confirme que essa tentativa não criou um novo registro TESTE-ERRO. Compare com a lista anterior se já havia testes antigos.

FALA: “A consulta confirma que essa tentativa inválida não foi salva.”

## 9. Gustavo — nome vazio, erro esperado 422

NA TELA: em POST /cidades, envie exatamente um nome com espaços:

```json
{"nome":"   "}
```

NA TELA: clique Execute. Esperado: 422. O texto técnico da resposta pode aparecer em inglês; não precisa ser lido inteiro.

FALA: “Agora enviamos um nome formado apenas por espaços. A validação rejeitou a entrada e retornou 422. Isso evita guardar uma cidade sem nome.

FALA: Os dois erros foram provocados de propósito. Eles mostram que o sistema verifica as entradas e devolve respostas para orientar quem está usando a API.”

## 10. José Henrique — persistência, se houver tempo

NA TELA: memorize o id_linha criado. No terminal da API, pressione Ctrl+C. Inicie novamente com o mesmo comando usado antes, sem --preparar. Aguarde Application startup complete e execute GET /linhas.

FALA: “Encerramos apenas o servidor e iniciamos novamente. O cadastro continua no banco local. Isso mostra a persistência dos dados: eles não ficam guardados apenas na tela ou na memória do programa.”

APOIO: não apague apresentacao_local.db e não rode uma configuração de banco diferente. Se o tempo estiver curto, explique a persistência e mantenha esse teste como apoio para perguntas.

## 11. Ana Carolina — testes, GitHub e conclusão

FALA: “Além da demonstração, usamos testes automatizados e registramos evidências das respostas da API. Isso ajuda a conferir o funcionamento depois de alterações no código.

FALA: O código está versionado no GitHub, permitindo acompanhar as mudanças e compartilhar a entrega.

FALA: Nesta apresentação, mostramos a organização do backend, o cadastro e a consulta de duas entidades relacionadas, a validação das entradas e os testes de situações de erro.

FALA: O site pode utilizar essas respostas para apresentar as informações visualmente. Aqui, nosso foco foi demonstrar que a API recebe os pedidos, aplica as regras e trabalha com o banco de dados. Obrigada pela atenção!”

## Apoio para perguntas dos professores

| Pergunta | Resposta curta |
|---|---|
| API e site são a mesma coisa? | A API recebe pedidos e devolve dados. O site apresenta telas e utiliza esses dados. O mesmo servidor pode servir ambos. |
| O que é uma rota? | Um endereço da API associado a uma operação, como GET /linhas. |
| Qual a diferença entre POST e GET? | POST envia o cadastro; GET consulta informações. Neste recorte, GET não cria registros. |
| PK e FK significam o quê? | Chave primária identifica o registro; chave estrangeira liga esse registro a outra tabela. |
| Qual a relação entre cidade e linha? | Neste recorte, uma cidade pode ter várias linhas; cada linha aponta para uma cidade cadastrada. |
| Por que aparece o nome da cidade na linha? | A consulta usa o relacionamento entre as tabelas para produzir uma resposta mais compreensível. |
| Onde os dados ficam? | Nesta demonstração, em um arquivo SQLite local. Não estamos demonstrando gravação remota no Supabase. |
| O que o ambiente virtual faz? | Isola as bibliotecas Python necessárias ao projeto. |
| O que significam 200, 201, 404 e 422? | Consulta atendida; registro criado; cidade não encontrada; entrada inválida. |
| O banco impede nomes repetidos? | Não neste modelo SQLite atual. Cada novo registro recebe outro ID. Não confundir com esquemas remotos que tenham UNIQUE. |
| O que falta para uso operacional? | Integrações, autenticação operacional, regras e infraestrutura precisam ser validadas para cada função. Ter uma tela não comprova uma integração. |

## Se algo falhar no auditório

Se 127.0.0.1 recusar conexão, confira se o servidor continua aberto no mesmo computador. Se o terminal mostrar erro, não anuncie sucesso. Não tente corrigir senhas ou trocar de banco no palco.

FALA DE APOIO: “A execução não respondeu como esperado neste momento. Temos evidências de uma execução anterior e vamos identificá-las como evidências, sem confundir com o teste ao vivo.”

Depois da apresentação, Ctrl+C encerra o servidor. Saia do WhatsApp Web se o computador for compartilhado.
