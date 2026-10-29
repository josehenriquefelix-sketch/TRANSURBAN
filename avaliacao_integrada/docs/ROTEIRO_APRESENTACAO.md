# Roteiro de apresentação — TRANSURBAN

## Preparação nos computadores da escola e do auditório

1. No GitHub, atualize ou clone o repositório `josehenriquefelix-sketch/TRANSURBAN` e abra a pasta `avaliacao_integrada` no VS Code.
2. Confirme que o computador tem Python 3.10 ou superior e acesso à internet para instalar as dependências e acessar o Supabase.
3. Na primeira execução, abra `iniciar_local.cmd`. Ele cria o ambiente, instala as dependências e, se detectar valores de exemplo, abre a configuração local. Preencha a URL e a chave privada do projeto Supabase nesse computador. Não coloque a chave no GitHub nem a mostre na apresentação.
4. O iniciador sobe um único serviço e abre o painel. A interface fica em `http://127.0.0.1:8000/`; o Swagger fica em `http://127.0.0.1:8000/docs`. Mantenha a janela da API aberta.
5. Antes de demonstrar alterações reais, use nomes fictícios e combine quem vai excluir cada registro de teste.

## Fala de abertura

“Eu vou apresentar o TRANSURBAN, um projeto acadêmico sobre mobilidade em Maringá e Sarandi. A aplicação integra o painel de dados, o cadastro de cidades e linhas, uma API e o Supabase. A base de análise é sintética, então usamos seus resultados para demonstrar o funcionamento, não para descrever a operação real do transporte.”

> Personalize esta fala para explicar sua contribuição real no grupo. Não diga que escreveu uma parte que não consegue explicar.

## Demonstração do painel

1. Mostre o cabeçalho, o indicador de conexão e o desenho conceitual da conexão urbana. Explique que a ilustração não é uma rota operacional.
2. Abra **Ciência de Dados** e mostre os indicadores: observações válidas, soma e média do atraso por observação e cidades analisadas.
3. Apresente as quatro perguntas: total e média por cidade, período, condição de trânsito e clima. Os resultados vêm da API e são organizados por pandas.
4. Explique a unidade: cada linha do CSV é uma observação de atraso em um trecho, não necessariamente uma viagem completa. `codigo_linha` se repete; o par cidade + código identifica uma linha distinta. Sem `id_viagem`, não afirmamos contar viagens, ônibus ou passageiros únicos. Duplicatas exatas são verificadas.
5. Reforce que o arquivo é uma base sintética didática. Os agrupamentos mostram associações dentro do CSV e não provam causas nem preveem horários.

## Demonstração do CRUD

1. Em **Cadastro de cidades**, mostre o campo obrigatório e a lista carregada do Supabase. Cadastre uma cidade fictícia e anote o ID.
2. Consulte pelo ID, edite o nome, atualize a lista e exclua o registro de teste. Se uma linha estiver vinculada, a chave estrangeira pode impedir a exclusão.
3. Em **Linhas de ônibus**, escolha uma cidade existente, cadastre código e nome, consulte e edite a linha. Exclua o registro de teste ao terminar.
4. Explique a regra da avaliação: cidade é a tabela observada com PK e sem FK, por isso atende ao CRUD obrigatório da recuperação. Linhas têm FK e fazem parte do CRUD integrado.
5. Se necessário, abra `/docs` e mostre as rotas. Campo inválido retorna 422, ID inexistente retorna 404 e conflito de integridade pode retornar 409.
6. No Supabase Table Editor, confira os registros criados e removidos. Nunca mostre a chave privada.

## Como explicar a tecnologia

- **HTML:** estrutura as seções, formulários, indicadores e tabelas.
- **CSS:** define cores, espaçamento, hierarquia visual e adaptação para telas menores.
- **JavaScript:** consulta a API, envia JSON, atualiza listas e dá retorno para cadastrar, consultar, editar e excluir.
- **Python e FastAPI:** validam as entradas, disponibilizam as rotas CRUD e de análise e servem os arquivos da interface pela mesma origem local.
- **Pandas:** valida o CSV e calcula os agrupamentos.
- **Supabase/PostgreSQL:** guarda os registros; o backend acessa a Data API por HTTPS com a chave mantida só localmente.
- **CORS:** está configurado para desenvolvimento com frontend separado. No iniciador de apresentação, tela e API usam a mesma origem e não dependem de uma segunda janela de servidor.

## Roteiro curto em primeira pessoa

“Eu entendi o fluxo desta forma: a tela envia uma solicitação em JSON; a FastAPI valida os campos; para os cadastros, o backend acessa o Supabase por HTTPS e devolve o resultado. Para a parte de dados, a API lê o CSV com pandas, calcula as totalizações e envia os resultados para a tela. No computador de apresentação, a interface e a API são abertas pelo mesmo iniciador. A chave privada fica no arquivo local de configuração e nunca no navegador.”

## Encerramento

“Com o TRANSURBAN, apresentamos operações de cadastro integradas ao banco e quatro totalizações sobre uma base acadêmica. O CRUD de cidade atende à regra de tabela com PK sem FK; o CRUD de linhas demonstra o relacionamento com cidade. Os resultados são descritivos e sintéticos.”

