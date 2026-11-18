# TRANSURBAN — execução local no VS Code

Sistema de mobilidade entre Maringá e Sarandi. HTML, CSS e JavaScript no frontend; Python e FastAPI no backend; PostgreSQL do Supabase. **A execução atual não depende do Render.**

## Abrir o projeto

1. Instale Python 3.10 ou superior, Git e VS Code no computador, caso não estejam disponíveis.
2. Clone `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git` no VS Code. Se já tiver a cópia, use Git Pull sem sobrescrever alterações locais.
3. Abra o workspace `avaliacao_integrada/TRANSURBAN.code-workspace`.
4. Execute `iniciar_local.cmd` ou pressione **Ctrl+Shift+B**. Na primeira vez o comando cria o ambiente e instala as dependências.
5. Se a configuração for nova, preencha a URL e a chave privada do projeto em `backend/.env`. O iniciador copia o exemplo e abre o editor quando faltam esses valores. O `.env` não vem do GitHub e nunca deve ser publicado.
6. Mantenha o servidor aberto. Use os comandos de `ACESSOS/` para abrir passageiro, motorista ou gestão. Eles reutilizam o mesmo servidor.

| Área | Endereço local |
|---|---|
| Passageiro | http://127.0.0.1:8000/ |
| Motorista | http://127.0.0.1:8000/motorista/ |
| Gestão | http://127.0.0.1:8000/gestao/ |
| Materiais da manutenção | http://127.0.0.1:8000/gestao/materiais.html |
| Estrutura do banco | http://127.0.0.1:8000/gestao/banco.html |
| Dashboard acadêmico | http://127.0.0.1:8000/dados/ |
| Chat do CSV | http://127.0.0.1:8000/dados/chat.html |
| Swagger DS | http://127.0.0.1:8000/docs |
| Swagger IA | http://127.0.0.1:8000/dados/docs |

`127.0.0.1` é o próprio computador. Para usar a cópia no computador da informática, o servidor deve ser iniciado lá. O Supabase, o login Google e o SMTP precisam de internet; o CSV e os gráficos locais não dependem da hospedagem antiga.

## Contas e permissões

O cadastro público cria passageiro. Motorista e gestor precisam de vínculo aprovado por um administrador; não há autoaprovação. A administração da equipe é definida no `.env` privado. Os módulos de materiais e estrutura exigem essa conta administrativa. Senhas seguem o mínimo de oito caracteres, maiúscula, minúscula, número e símbolo.

Os redirecionamentos de cadastro, recuperação e Google usam `APP_URL=http://127.0.0.1:8000`. Cookies locais usam `COOKIE_SECURE=false`. É necessário manter os endereços locais na lista permitida do Supabase.

O responsável informou que ainda não tem SMTP nem chave do Ollama. A configuração está preparada e vazia. **Não se afirma entrega real no Gmail ou explicação real da nuvem.** O chat mantém os cálculos e mostra aviso; a fila de e-mail não é marcada como enviada sem SMTP. Veja [configuração de e-mail](docs/EMAIL_E_CONTAS_LOCAL.md).

## Banco e etapas da escola

Os scripts `database/` não apagam as tabelas anteriores. Em um banco novo, leia primeiro os scripts iniciais. No projeto da equipe, as evoluções 08 e 09 foram aplicadas e conferidas. Não aplique scripts de banco vazio em uma base existente sem conferir a estrutura.

- `08_notificacoes_acesso.sql`: fila privada de notificações do pedido e da decisão.
- `09_materiais_e_ordens.sql`: unidade/oficina, material, ordem e item com PK composta; fechamento transacional.
- [Estrutura conferida do banco](docs/ESQUEMA_BANCO_ATUAL.json): 28 tabelas documentadas pela Data API, sem registros pessoais.
- [Etapas e explicação para a equipe](docs/ETAPAS_ESCOLA_E_EXPLICACAO.md): adaptação dos guias e ordem para estudar o código.

O módulo de materiais adapta o exemplo da Mercearia ao fornecimento para manutenção. O fechamento calcula com NUMERIC, preserva o preço do item, baixa estoque e, no prazo, limite. Uma recusa desfaz a operação. Não há cobrança financeira nem recarga real integrada.

## Ciência de Dados e chat

O mesmo CSV sintético é usado nos resumos, nas séries por dia, na tabela, nos gráficos Chart.js e nas perguntas cadastradas. Cada linha é uma observação de trecho. Sem identificador de viagem não se contam viagens completas ou passageiros. O chat chama funções Python e só depois pode pedir ao Ollama uma explicação dos agregados, sem enviar dados das contas.

O dashboard acadêmico é separado do dashboard público de informações documentadas. Não mistura números sintéticos com o catálogo oficial.

## Conferência

Com o ambiente preparado, execute `VERIFICAR_TRANSURBAN.cmd` ou `backend/.venv/Scripts/python.exe verificar_ambiente.py`.

Para os testes automatizados, execute da pasta deste README:

```text
backend/.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py"
node --test tests/localizacao.test.cjs
```

Node é usado apenas nos testes de comportamento; não é necessário para abrir o projeto. A rodada desta evolução passou em 47 testes Python, 11 testes de localização e 14 verificações reais do módulo de materiais. Veja os relatórios em `docs/`. Os testes não comprovam um GPS físico, o recebimento de e-mail ou todos os navegadores.

## Limites operacionais

O catálogo contém 66 linhas municipais de Maringá e 22 atendimentos/variantes metropolitanos de Sarandi documentados. A cobertura municipal completa de Sarandi não foi confirmada. Horários de terminal não são previsão de passagem em qualquer ponto. O mapa próprio só recebe veículos de motoristas autorizados compartilhando o dispositivo; não há integração autorizada ao GPS/ETA da operadora.

Não há integração financeira com bilhetagem. Localização depende de permissão, sinal e precisão. SMTP e Ollama precisam de configuração autorizada. A leitura integral da turma DS-IA-Meca ainda não foi confirmada; os materiais estudados e a divergência de anexos estão registrados no documento das etapas.
