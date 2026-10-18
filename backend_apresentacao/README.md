# TRANSURBAN — painel da API e avaliação DS + IA

Este diretório integra o painel com a análise Pandas já versionada em
`avaliacao_backend/backend/analise.py`. Preserva as seis entidades da demonstração.
Dados fictícios e CSV sintético; sem login, GPS ou previsão de atrasos validada.

## Iniciar e encerrar

No Windows, abra `ABRIR_MODO_LOCAL.cmd` para SQLite ou `ABRIR_TRANSURBAN.cmd`
para usar a conexão privada `.env`, quando configurada. Instalação inicial:
`python preparar.py --testes`. Requer Python 3.11+ e internet para instalar.
Abra http://127.0.0.1:8000/apresentacao. Encerre com Ctrl+C na janela do servidor.
Se houve atualização de código, encerre e abra novamente o iniciador.
Não copie o ambiente virtual para outro computador: recrie-o com preparar.py.

## Responsabilidades

| Arquivo | Responsabilidade |
|---|---|
| database.py | Conexão, engine, sessões e Base; lê .env sem publicar a senha |
| models.py | Tabelas, PK, FK, unicidade e restrições |
| schemas.py | Tipos, campos obrigatórios e validações de entrada |
| main.py | Rotas HTTP, relacionamentos e respostas |
| analise.py | Pandas: leitura, qualidade, resumo e agrupamentos |
| static/index.html | Interface que consome as rotas |

GET/POST `/cidades` e `/linhas` demonstram PK/FK. A consulta de linhas inclui
o nome da cidade. Cidade inexistente: 404; duplicidade: 409; entrada inválida: 422.
Rotas adicionais tratam trechos, percursos, faixas e atrasos.

## Ciência de Dados

| Rota GET | Resultado |
|---|---|
| /indicadores | Resumo compatível com o painel, incluindo soma e mediana |
| /ia/qualidade | Ausentes, tipos, duplicatas e inconsistências |
| /ia/resumo | Contagem, soma, média, mediana, período e limites |
| /ia/agrupamentos/linha | Estatísticas por cidade + código da linha |
| /ia/agrupamentos/data | Estatísticas por data |
| /ia/agrupamentos/transito | Estatísticas por condição de trânsito |
| /ia/maiores-atrasos | Todos os empates no maior atraso |

Também é possível agrupar por cidade, período, clima e trecho. Veja
`docs/IA_E_DASHBOARD.md` para o dicionário, perguntas e regras. Cada linha é uma
observação por trecho/data/linha, não uma viagem completa. Minutos somados não
representam tempo perdido por passageiros. Não há imputação silenciosa de zero.
Indicadores interrompem com 422 se a fonte estiver vazia, inválida, duplicada
ou apresentar nomes conflitantes. CSV indisponível: 503. `/ia/qualidade` permite
inspecionar problemas quando o arquivo e o cabeçalho podem ser lidos.

## Testes e evidências

Na pasta deste README: `python -m unittest discover -s tests -v`.
Foram executados 43 testes em SQLite isolado, sem alterar Supabase.
A conferência dos cálculos usa também csv/statistics, independentemente do Pandas.
As evidências anteriores do Supabase referem-se ao ensaio indicado nesses arquivos.
As evidências desta integração ficam em `evidencias/TESTES_DS_IA_2026-10-18.txt`
e `evidencias/IA_RESPOSTAS_2026-10-18.json`.

## Versionamento

Este código está na pasta `backend_apresentacao` do repositório TRANSURBAN.
Os commits desta integração são atuais; não se atribuem datas ou execução aos
integrantes retroativamente. `.env`, `.venv` e bancos locais ficam fora do Git.
Em um clone: `git status`, `git add <arquivos>`, `git commit -m "descrição"`,
`git push`. Confira o diff antes do commit. Não envie senhas ou notas pessoais.

Fichas individuais e entrega no Classroom dependem do acesso autenticado à conta
e da atuação real da equipe. Este README não declara a atividade entregue.
