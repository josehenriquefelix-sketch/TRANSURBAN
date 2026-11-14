# TRANSURBAN — Recuperação DS e integração DS + IA

## Ficiências 2026

O [guia do evento](docs/FICIENCIAS_2026.md) descreve a preparação do computador e o percurso pelo sistema. Na raiz do repositório, `INICIAR_TRANSURBAN.cmd` abre a aplicação e `VERIFICAR_TRANSURBAN.cmd` confere dependências, configuração, tabelas, arquivos da interface e documentação. O verificador realiza somente consultas.

## Portal de mobilidade — 13/11/2026

O TRANSURBAN é uma plataforma independente para passageiros, motoristas autorizados e gestão do transporte entre Maringá e Sarandi. A interface usa HTML, CSS e JavaScript; a API usa Python/FastAPI; os registros ficam no Supabase/PostgreSQL por HTTPS.

- Passageiro: início, dashboard pessoal, cidades/linhas, horários e mapa, favoritas, manifestações com protocolo e resposta, conta e recuperação de senha.
- Motorista autorizado: perfil e veículo, notas das próprias viagens, início/encerramento e compartilhamento consentido da localização do dispositivo. O perfil público é opcional.
- Gestão autorizada: fila por competência, filtros, resposta ao cidadão e histórico persistido. Passageiros não recebem acesso profissional ao criar conta.
- Site e API usam uma única origem: `http://127.0.0.1:8000/`. A documentação técnica está em `/docs`, sem link no portal público. Ciência de Dados fica separada em `/dados/docs`.
- O catálogo contém as 66 linhas municipais de Maringá visíveis na consulta oficial Na Hora e 22 atendimentos de Sarandi, incluindo variantes, extraídos de 12 tabelas DER/PR. Foram conferidas 1.064 partidas documentais antes de separar variantes. Horários e pontos de Maringá são abertos na consulta oficial incorporada; o seletor de Maringá não mistura as ligações metropolitanas. O catálogo municipal interbairros completo de Sarandi não foi confirmado.
- Horários documentais não são previsões de passagem. O mapa próprio TRANSURBAN só exibe posição quando um motorista autorizado inicia viagem e envia sua localização. A consulta oficial incorporada é um serviço externo distinto e pode oferecer recursos ao vivo conforme a disponibilidade do provedor. Não há integração de GPS/ETA da TCCC ou Mobilibus.
- Recarga e pagamento dependem de adesão à bilhetagem e ao provedor de pagamentos. A tela informa essa pendência e não vende créditos fictícios.
- Google está configurado com PKCE e o fluxo foi concluído no navegador em 13/11/2026, retornando ao portal com sessão de passageiro. E-mails de confirmação/recuperação dependem de SMTP e da confirmação de entrega em caixa postal real.

Os ambientes estão separados: passageiro em `/`, motorista em `/motorista/` e gestão em `/gestao/`. A gestão não aparece na navegação pública. Cada ambiente possui logo e paleta próprios. O suporte tem protocolo privado, resposta por escopo e histórico; os alertas no mapa são publicações manuais com validade, sem inferência automática do trânsito. Pedidos de acesso profissional ficam pendentes até a aprovação administrativa, com proibição de autoaprovação.

### Abrir no computador da escola

1. No VS Code, pressione `Ctrl+Shift+P`, escolha **Git: Clone** e cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`. Escolha uma pasta e abra o repositório. Se já estiver clonado, execute `git pull` no terminal, sem sobrescrever mudanças locais.
2. Copie `avaliacao_integrada/backend/.env.example` para `avaliacao_integrada/backend/.env`. Preencha URL e chave privada do mesmo projeto Supabase, sem aspas extras. Transfira essas informações por meio privado. O `.env` fica fora do GitHub.
3. Na raiz do repositório, execute `INICIAR_TRANSURBAN.cmd`. Na primeira vez ele cria o ambiente e instala as dependências. Mantenha a janela do servidor aberta.
4. Abra `http://127.0.0.1:8000/`; a documentação técnica é acessada diretamente em `/docs`. Use uma conta já confirmada. A conta profissional precisa ter vínculo previamente autorizado no banco.
5. Execute `VERIFICAR_TRANSURBAN.cmd` para conferir a configuração antes do uso.

Windows: Python 3.10+ no PATH, Git e internet. Linux/macOS: entre em `avaliacao_integrada`, execute `python3 -m venv backend/.venv`, ative com `source backend/.venv/bin/activate`, instale `pip install -r backend/requirements.txt` e inicie `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`.

`127.0.0.1` é o próprio computador. Para vários dispositivos acessarem o mesmo sistema, hospede a API/interface em um endereço **HTTPS**, configure `APP_URL`, `COOKIE_SECURE=true`, URLs de retorno do Supabase e proxy confiável. Celular acessando um IP de rede HTTP não tem a mesma garantia de acesso à geolocalização. O navegador precisa permanecer aberto; GPS contínuo em segundo plano exige aplicativo/solução específica.

### Banco, papéis e integrações

No projeto Supabase da equipe, os scripts 05, 06 e 07 foram aplicados. Ao usar **o mesmo banco**, não execute novamente a instalação. Em projeto novo, siga os scripts SQL da pasta `database` na ordem, incluindo `05_portal.sql` `06_operacao_e_manifestacoes.sql` e `07_suporte_e_aprovacoes.sql`.

Consulte [operação e integrações](docs/MOBILIDADE_OPERACAO.md) para autorizar vínculos, configurar Google e e-mail, entender os limites do mapa e consultar as fontes. A chave de serviço fica somente no backend. As tabelas novas têm RLS e não oferecem acesso direto a `anon`/`authenticated`; o backend verifica a sessão, o papel e o escopo em cada operação.

A senha nova exige no mínimo 8 caracteres, maiúscula, minúscula, número e símbolo. O Supabase administra o hash das senhas; o backend converte a rejeição de senha igual à anterior em mensagem clara. A busca de login por CPF usa SHA-256 do CPF validado. Esse resumo ainda é dado pessoal e permanece protegido no backend/banco.

### Evidências

A revisão de 13/11/2026 passou em 31 testes automatizados. O suporte foi validado com Supabase real em `docs/VALIDACAO_SUPORTE_20261113.json`. Trocar de cidade limpa os resultados anteriores; dia e sentido atualizam a consulta automaticamente; manifestações são validadas contra as cidades atendidas pela linha. Respostas antigas de consultas sobrepostas não substituem a seleção mais recente.

Os testes automatizados verificam CRUD/FK, CORS, documentação, cookies e permissões. A validação adicional com Supabase real está em `docs/VALIDACAO_MOBILIDADE_20261112.json`; as contas e os registros sintéticos usados nela são descartados ao final. Coordenadas sintéticas validam o envio/consulta e não provam GPS de aparelho ou localização de frota real. Evidências anteriores permanecem datadas e podem descrever versões anteriores da interface.

Entrega acadêmica integrada com FastAPI, pandas, Supabase por HTTPS, HTML, CSS e JavaScript. A documentação cobre o CRUD, a base de Ciência de Dados, as quatro perguntas, o CORS e o roteiro de conferência.

**Projeto da equipe:** sistema acadêmico sobre transporte coletivo de Maringá e Sarandi. **Professor responsável:** Erinaldo Sanches Nascimento. **Grupo:** preencher os nomes dos integrantes antes da apresentação.

## Conteúdo

- `backend/`: FastAPI, modelos Pydantic, CRUD de cidade e linha por Supabase Data API HTTPS, leitura/validação do CSV, quatro totalizações e configuração de CORS.
- `database/`: consulta de auditoria e DDLs para uma instância vazia. O backend não cria nem modifica tabelas automaticamente.
- `data/atrasos_analise.csv`: base de demonstração e `ORIGEM_DADOS.txt` com a procedência e os limites.
- `frontend/`: portal responsivo de mobilidade com áreas de passageiro, motorista e gestão. O CRUD acadêmico continua na API protegida.
- `docs/`: explicação sobre linha da base e perguntas, resultados conferidos, verificação local e roteiro de apresentação.

## Escopo do CRUD

Em auditoria somente de leitura do projeto Supabase `transurban`, em 28/10/2026, foram encontradas as tabelas públicas `cidade`, `faixa_exclusiva`, `linha_onibus`, `linha_trecho`, `registro_atraso` e `trecho`. As PKs observadas são `cidade.id_cidade`, `faixa_exclusiva.id_faixa`, `linha_onibus.id_linha` e a PK composta de `linha_trecho` (`id_linha`, `id_trecho`). As FKs observadas incluem `faixa_exclusiva.id_trecho`, `linha_onibus.id_cidade`, `linha_trecho.id_linha`/`id_trecho` e `registro_atraso.id_linha`/`id_trecho`. `trecho` e `registro_atraso` não apresentaram PK nessa auditoria. Assim, **`cidade` é a única tabela observada com PK e sem FK**, e é a única incluída no CRUD da recuperação. `linha_onibus` fica disponível na avaliação integrada e preserva sua FK para cidade. O banco não foi alterado durante a auditoria.

## Atividade de chave estrangeira (DS)

O relacionamento autoral aplicado é `cidade` → `linha_onibus`: `cidade.id_cidade` é PK; `linha_onibus.id_linha` é PK e `linha_onibus.id_cidade` é FK. O endpoint `/linhas` guarda o ID da cidade e inclui seu nome consultado na resposta. O CRUD de linhas valida a cidade e a FK do banco impede excluir uma cidade que ainda tenha linhas vinculadas. Consulte o [passo a passo e roteiro de teste da atividade](docs/RELACIONAMENTO_FK_CIDADE_LINHA.md).

No Supabase atual essas tabelas já existem. Não execute DDL de criação sobre elas; os scripts em `database/` são para uma base de demonstração vazia e devem ser revisados após a auditoria.

## Requisitos

- Python 3.10 ou superior.
- Projeto Supabase da equipe com Data API habilitada, esquema `public` exposto e tabela `public.cidade` compatível.
- A chave secreta do Supabase deve ficar apenas em `backend/.env`; nunca no HTML/JavaScript ou no GitHub.
- Git não deve receber `.env`, `.venv` ou senhas. O `.env.example` contém apenas valores fictícios.

## Início rápido no Windows

Guia passo a passo para clonar pelo VS Code, configurar o Supabase e iniciar o site no computador do auditório: [GUIA_RAPIDO_AUDITORIO.md](GUIA_RAPIDO_AUDITORIO.md).

Dê duplo clique em `iniciar_local.cmd` (ou no atalho `ABRIR TRANSURBAN`, se já tiver sido criado). Na primeira execução, o iniciador cria o ambiente, instala as dependências e abre a configuração local se detectar uma URL ou chave de exemplo. Preencha os dados do Supabase neste computador. O iniciador sobe um único serviço que entrega a interface, a API e o Swagger. O painel abre em `http://127.0.0.1:8000/`; a documentação fica em `/docs`. Mantenha a janela da API aberta durante a apresentação. Enquanto o serviço estiver ativo, ele solicita ao Windows que não suspenda o sistema; ao encerrar a API, a solicitação é liberada.

Para usar no computador da escola ou do auditório, atualize ou clone o repositório, abra `avaliacao_integrada` no VS Code e execute o mesmo `iniciar_local.cmd`. Cada computador precisa de sua própria configuração em `backend/.env`; esse arquivo privado não é transferido pelo GitHub. O repositório fornece apenas o `.env.example` fictício.
## Preparação no Windows (PowerShell)

Abra o terminal na pasta `TRANSURBAN_ENTREGA`:

```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

Edite `backend/.env` com a Project URL e a chave secreta do **projeto Supabase correto**. Não use a senha PostgreSQL como chave da API. Em um terminal, na raiz do projeto, inicie o backend:

```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

A FastAPI serve também a interface no mesmo endereço. Abra `http://127.0.0.1:8000/`; o Swagger fica em `http://127.0.0.1:8000/docs`. Mantenha o serviço em `127.0.0.1`; esta versão acadêmica não tem autenticação e não deve ser publicada para acesso público.

No Linux/macOS, crie o ambiente com `python3 -m venv backend/.venv`, instale `backend/requirements.txt`, copie o `.env.example` para `.env` dentro de `backend` e inicie `uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000` na raiz. A própria API serve a interface em `/`.

## Supabase: auditar antes de alterar

1. No projeto correto, abra **SQL Editor** e execute `database/01_auditar_esquema.sql`. Ele somente lê metadados de `public`.
2. Confirme que `cidade` tem `id_cidade` como PK gerada automaticamente e `nome` como texto obrigatório e único. A consulta também lista chaves estrangeiras do esquema.
3. **Não execute DDL de criação em tabela existente.** Se as tabelas não existirem em uma instância vazia de demonstração, revise e então execute `database/02_criar_cidade_banco_novo.sql` seguido de `database/03_criar_linha_banco_novo.sql`. Se a auditoria mostrar uma PK existente sem `IDENTITY` e sem `DEFAULT`, revise o script `database/04_ids_automaticos_existentes.sql`; ele bloqueia escrita durante a sincronização e deve ser executado em período sem alterações.
4. Mantenha RLS habilitada e use a chave secreta só no backend local. O script concede privilégios a `service_role`; não crie política pública `anon` nem desative RLS para esconder erro de configuração.
5. Se a tabela atual usar nomes/tipos/IDs diferentes, pare e adapte o modelo e as rotas ao resultado real. O projeto anterior registra divergências históricas entre versões do DER; este DDL não deve ser aplicado sem auditoria.

## Rotas de Ciência de Dados

| Método | Rota | Pergunta |
|---|---|---|
| GET | `/ia/resumo` | Quantas observações válidas há, qual o período e quais os limites da base? |
| GET | `/ia/totalizacao/cidade` | Quanto atraso foi observado em cada cidade? |
| GET | `/ia/totalizacao/periodo` | Como total e média se distribuem por período do dia? |
| GET | `/ia/totalizacao/transito` | Qual total e média para cada condição de trânsito? |
| GET | `/ia/totalizacao/clima` | Qual total e média para cada condição de clima? |

Todas as respostas são JSON. Cada agrupamento apresenta contagem de observações, soma, média, mediana e máximo em minutos. O script `backend/analise.py` valida campos, datas, números, consistência de atrasos, ausentes e duplicatas antes de calcular.

## Modelo da base e contagem sem duplicidade

Cada linha do CSV representa uma observação acadêmica de atraso em um trecho, em determinada data e contexto. Não representa necessariamente uma viagem completa, um ônibus ou uma pessoa. O identificador composto para reconhecer uma linha de ônibus é `cidade + codigo_linha`; o código isolado pode se repetir entre cidades ou observações. Como não há `id_viagem` nem identificador único da observação, não é correto chamar a contagem de viagens distintas. As rotas somam minutos observados e não estimam atraso de passageiros. A base é sintética, como descreve `data/ORIGEM_DADOS.txt`; não representa telemetria real.

## CORS e comunicação

A tela e a API usam a mesma origem local (`127.0.0.1:8000`), então a abertura padrão não depende de um segundo servidor nem de CORS no navegador. O middleware CORS permanece configurável para desenvolvimento com frontend separado. O segredo do Supabase não é entregue ao navegador.

## Roteiro manual de conferência e evidências

Confira a [verificação atualizada](docs/VERIFICACAO_LOCAL.md) e o [relatório das 37 verificações com Supabase real](docs/EVIDENCIAS_FK_20261106.json).

Use apenas nomes fictícios de cidades e confirme os registros no Table Editor do Supabase. No Swagger (`/docs`):

1. `GET /cidades` — confirma conexão e lista inicial.
2. `POST /cidades` com `{"nome":"Cidade de Teste DS"}` — esperado `201` e `id_cidade` gerado.
3. `GET /cidades/{ID}` e depois `GET /cidades` — esperado `200` e registro na lista.
4. `PUT /cidades/{ID}` com `{"nome":"Cidade de Teste DS Atualizada"}` — esperado `200`; consulte novamente.
5. `DELETE /cidades/{ID}` — esperado `204`; `GET /cidades/{ID}` depois retorna `404`. Se estiver referenciada por uma linha, espere `409` e não apague a FK.
6. `POST /cidades` com nome vazio ou `id_cidade` extra — esperado `422`; nenhum cadastro indevido deve ser gravado.
7. Repita o ciclo CRUD para `linha_onibus`: `POST /linhas` com `id_cidade`, `codigo` e `nome`; consulte, edite com `PUT`, exclua e confirme que uma cidade inexistente retorna `400` ao criar linha.
8. Abra as cinco rotas `/ia` e confira o JSON com os valores apresentados na interface.
9. Salve capturas do Swagger e do Table Editor antes/depois. Os espaços reservados desta pasta não afirmam que testes remotos foram executados; preencha seu relatório com capturas obtidas no seu projeto.

### Testes locais reproduzíveis

Os testes automatizados usam uma tabelas em memória para o CRUD, sem alterar o Supabase. Com as dependências instaladas, execute na raiz: `backend\.venv\Scripts\python.exe -m unittest discover -s tests -v`. Eles verificam o fluxo CRUD, as validações, as quatro totalizações sobre o CSV e o preflight CORS. Isso não substitui os testes no Swagger/Supabase do roteiro acima.

## Apresentação em equipe

- **HTML:** estrutura, campos, navegação, acessibilidade e tabelas.
- **CSS:** cores, tipografia, responsividade e leitura em celular/computador.
- **JavaScript:** chamadas `fetch`, validações visuais, CRUD de cidades e linhas, consulta da API de dados e exibição das totalizações.
- **API/CORS:** FastAPI, Pydantic, rotas, variáveis privadas, comunicação HTTPS com Supabase e origens autorizadas.
- **Ciência de Dados:** significado de cada linha, chave usada para distinguir linhas, limitações da fonte e interpretação das quatro perguntas.

A distribuição depende do tamanho do grupo. Com duas pessoas, combinar HTML/CSS e JavaScript/CORS. Com três, dividir HTML, CSS e JavaScript/CORS. Todos devem acompanhar o teste integrado e explicar a própria parte.

## Repositório da equipe

Repositório identificado no material local: [github.com/josehenriquefelix-sketch/TRANSURBAN](https://github.com/josehenriquefelix-sketch/TRANSURBAN). O pacote está pronto localmente. O link de entrega do GitHub será a branch publicada para revisão; confira também as instruções de integração da pasta no repositório.









## Publicação HTTPS

A configuração de hospedagem está no `render.yaml` da raiz do repositório. Veja [PUBLICACAO_HTTPS.md](docs/PUBLICACAO_HTTPS.md). O site e a API são servidos juntos; os registros continuam no Supabase. A revisão de preparação passou em 32 testes. Nenhum endereço público é anunciado antes de verificar o deploy real.

No atendimento, cidadãos e motoristas relatam ocorrências à gestão. Relato recebido é informação para análise, visível somente ao autor e à gestão competente. O alerta público exige verificação e publicação separada pela gestão.
