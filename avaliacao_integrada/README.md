# TRANSURBAN — site e API locais

Consulte primeiro o [passo a passo da escola](PASSO_A_PASSO_ESCOLA.md) e o [resumo da revisão atual](docs/REVISAO_20261124.md). Os três painéis usam o mesmo FastAPI e o mesmo Supabase, com permissões diferentes. O modelo ativo tem 12 tabelas.

## Executar no VS Code

1. Tenha Python 3.10 ou superior e internet; esta instalação foi testada com Python 3.13 no Windows.
2. Abra esta pasta ou `TRANSURBAN.code-workspace`.
3. Coloque o `.env` privado em `backend/.env`. O `.env.example` contém apenas exemplos fictícios.
4. Execute `iniciar_local.cmd` ou pressione Ctrl+Shift+B. O iniciador cria o ambiente e instala o requirements na primeira vez.
5. Mantenha o terminal aberto. Use `/`, `/motorista/`, `/gestao/` e `/docs` em `http://127.0.0.1:8000`.

Os atalhos em `ACESSOS/` também abrem as áreas. O cadastro público é de passageiro. Motorista e gestão usam contas com vínculo autorizado, sem uma senha coletiva no código.

## Banco

O banco atual da equipe já está migrado. Ao baixar o código em outro computador, configure a conexão; não execute SQL de criação novamente. As [instruções SQL](database/README.md) distinguem banco novo, migração e teste. A [estrutura conferida](docs/BANCO_CONFERIDO.md) e o arquivo local `ferramentas/estrutura_banco.html` mostram as 12 tabelas. O banco não aparece no painel da gestão.

Históricos de atendimento e notificações ficam no registro correspondente. O schema privado de arquivo guarda as tabelas anteriores; não é servido pela API. As senhas são gerenciadas pelo Supabase Auth. As tabelas internas do serviço não fazem parte das 12 tabelas do aplicativo.

## Validação

Da pasta deste README:

```powershell
.\VERIFICAR_TRANSURBAN.cmd
.\backend\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
node --test tests/localizacao.test.cjs tests/uso.test.cjs tests/catalogo_regiao.test.cjs
```

Node serve apenas para testes; não é necessário para executar o site. A conferência real opcional `ferramentas/validar_entrega.py` exige a conta privada de teste configurada no `.env`; cria e remove somente um chamado explicitamente descartável. Não projete as credenciais.

Em 24/11/2026, passaram 54 testes Python, 13 testes JavaScript e 34 verificações reais de login, leitura e atendimento. Os testes de fila no SQL usaram ROLLBACK e não enviaram e-mail. O [relatório atual](docs/VALIDACAO_ENTREGA_20261124.json) distingue resultados e limites.

Em 25/11/2026, passaram novamente 54 testes Python, agora 27 testes JavaScript e 34 verificações reais da API e do banco. Veja o [relatório da conferência real](docs/VALIDACAO_ENTREGA_20261125.json), o [teste de login e logout](docs/VALIDACAO_LOGINS_20261125.json), o [guia de cadastro e aprovação](docs/EMAIL_E_CONTAS_LOCAL.md) e o [roteiro resumido da equipe](docs/ROTEIRO_APRESENTACAO.md). O controle do Google Chrome externo não esteve disponível; esses resultados não são uma comprovação de teste visual completo nele.

## Informações e limites

O catálogo é um snapshot documentado em 12/11/2026; o índice DER foi revisto em 24/11. Não significa todas as linhas municipais de Sarandi. Partida de terminal não é previsão em qualquer ponto. A posição do ônibus depende do motorista autorizado compartilhando o dispositivo e da precisão recebida; não existe integração oficial à frota da operadora.

O CSV da atividade de Ciência de Dados é sintético. As quatro totalizações e o chat numérico ficam separados em `/dados/`; não estimam viagens ou passageiros. Sem Ollama configurado, o resultado numérico continua disponível e a explicação de nuvem não é inventada.

SMTP está preparado, mas não configurado. Não há entrega no Gmail confirmada. Login Google depende do provedor e dos endereços permitidos no Supabase. GPS em celular precisa de HTTPS e permissão, além de rede adequada; veja [o guia](docs/COMPUTADOR_E_CELULAR.md).

O banner local foi revisado em 25/11/2026 em PDF e SVG editável. A versão original foi preservada. O conector não teve permissão para atualizar o design do Canva nesta rodada. O arquivo local é A4; o enunciado integral do banner não estava acessível, portanto tamanho de impressão e conformidade exata com a rubrica da escola ainda precisam ser confirmados. Os exercícios de materiais e a carteira demonstrativa foram retirados da API por solicitação de manter apenas o essencial em 12 tabelas; suas fontes estão em `historico/`.

## Arquivos para compartilhar com a equipe

- [Roteiro em Word sem slides](docs/ROTEIRO_TRANSURBAN_SEM_SLIDES.docx): cinco falas e indicação do que demonstrar nos sites.
- [Tabela de conferência e guia de acessos](docs/CONFERENCIA_E_ACESSOS_TRANSURBAN.docx): resultados, limites e passos para cadastro e autorização, sem senhas compartilhadas.
- [Banner revisado em PDF](docs/BANNER_TRANSURBAN_REVISADO_20261125.pdf) e [fonte SVG editável](docs/BANNER_TRANSURBAN_REVISADO_EDITAVEL.svg).
- Com o servidor iniciado, os downloads ficam em `/equipe/roteiro.docx`, `/equipe/conferencia.docx` e `/equipe/banner.pdf`.

Os DOCX foram abertos no Word e suas provas de impressão foram renderizadas e inspecionadas. Na mesma rodada, uma falha registrada de streams HTTP/2 foi mitigada configurando o cliente do Supabase para HTTPS com HTTP/1.1. Passaram 16 consultas com quatro acessos simultâneos; isso não comprova ausência de falhas em qualquer carga. Veja [a conferência dos documentos e da conexão](docs/VALIDACAO_DOCUMENTOS_20261125.json).
