# TRANSURBAN: do GitHub ao ensaio no VS Code

Leia este guia antes da apresentação. A preparação e o download das dependências devem ser feitos com internet, antes de ir ao auditório. A apresentação oral está em `docs/apresentacao/ROTEIRO_COMPLETO.md`.

## O que precisa estar instalado

Git, Python 3.13 e VS Code. Confirme no terminal:

```powershell
git --version
python --version
code --version
```

O Python precisa mostrar `3.13.x`. Nesta máquina, `python` funciona; o comando `py -3.13` não localizou a instalação, por isso ele não é usado neste guia.

Também é necessário PostgreSQL. Na máquina de José, o banco local já foi preparado. Em outro computador, uma opção é Docker Desktop em execução, usando o container descrito abaixo. Ter somente o código e a `.venv` não substitui um servidor PostgreSQL.

## Baixar o projeto em um computador novo

Escolha uma pasta de trabalho e abra o terminal nela:

```powershell
git clone https://github.com/josehenriquefelix-sketch/TRANSURBAN.git
cd TRANSURBAN
python preparar.py
code TRANSURBAN.code-workspace
```

`preparar.py` cria `backend/.venv`, instala as versões registradas, verifica as dependências e cria `backend/.env` somente se ele ainda não existir. Um `.env` existente é preservado. A instalação precisa de internet. Não copie uma `.venv` de outro computador.

Se já tiver uma cópia, confirme a pasta e a branch antes de atualizar. `git pull --ff-only` deve ser executado em uma `main` limpa. Se houver alterações suas, preserve-as e não use comandos de descarte.

## Banco local em computador novo, com Docker

Com Docker Desktop instalado e em execução, na raiz do repositório:

```powershell
docker compose up -d banco
docker compose ps
```

Aguarde o banco ficar saudável. O `.env.example` usa a conexão local desse container, na porta `54329`. A credencial pública do exemplo é exclusivamente de desenvolvimento local. Não use essa credencial em serviços públicos.

Se seu `.env` já existir, ele não será modificado por `preparar.py`. Configure privadamente `TEST_DATABASE_URL` para seu PostgreSQL local. Nunca aponte essa variável para o Supabase.

O container foi configurado conforme o padrão de PostgreSQL local; Docker não está instalado na máquina usada nesta revisão, então esta rota de instalação ainda precisa de ensaio em um computador com Docker. A execução da API e dos testes com PostgreSQL local foi verificada nesta máquina.

## Banco já preparado na máquina de José

Se o banco local estiver parado, abra um terminal na raiz do projeto:

```powershell
.\.local-postgres\runtime\pgsql\bin\postgres.exe -D .\.local-postgres\data -h 127.0.0.1 -p 55439
```

Mantenha esse terminal aberto. Se a porta já estiver ocupada por esse banco, use a instância existente. A pasta `.local-postgres` contém dados privados locais e não faz parte do GitHub nem do pacote de código.

## Iniciar o modo de apresentação local

Na raiz, dê duplo clique em `INICIAR_AUDITORIO.cmd`. Ou use o terminal:

```powershell
cd backend
.\.venv\Scripts\python.exe executar_auditorio.py
```

Abra:

- API: http://127.0.0.1:8001/docs
- Site: http://127.0.0.1:8001/site/

Esse modo usa somente `TEST_DATABASE_URL` em um host local. Ele cria o schema persistente `transurban_auditorio`, prepara as duas tabelas e cadastra Maringá e Sarandi se ainda não existirem. Não cria linhas fictícias automaticamente. O `.env` e o Supabase são preservados. Os dados cadastrados nesse modo permanecem após reiniciar.

O Swagger, o site e seus arquivos de estilo e JavaScript são servidos localmente. Depois da preparação, esse modo não depende do Supabase ou de uma CDN para apresentar. O PostgreSQL local precisa continuar ativo.

Se a porta 8001 já estiver em uso, abra a página existente ou escolha outra porta com `executar_auditorio.py --port 8002`. Nesse caso, troque a porta também nos links e no comando de verificação.

## Executar todos os testes

Em outro terminal, dentro de `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe verificar_http.py --base-url http://127.0.0.1:8001
```

Resultado esperado para esta revisão: `18 passed`, um aviso de depreciação de dependência e nenhuma falha; `No broken requirements found`; `13 verificações HTTP aprovadas`.

Confira o resultado da sua execução, sem anunciar sucesso antes de ela terminar. A suíte testa POST, GET, persistência, FK, duplicidade, entradas inválidas, falha de banco sem vazamento de senha e documentação local. Os cadastros da suíte usam schemas temporários e são removidos ao final. O teste HTTP confirma as páginas e os arquivos necessários e envia duas requisições inválidas, que devem ser rejeitadas sem criar registros.

## Demonstração manual no Swagger

1. Use GET `/cidades` e anote o ID real de Sarandi. Não presuma que o ID será 1 ou 2.
2. Em POST `/linhas`, use o exemplo de identificação abaixo, substituindo `id_cidade` pelo ID anotado.
3. Confira HTTP 201 e o nome da cidade na resposta. Em GET `/linhas`, confirme o registro.
4. Repita exatamente o cadastro: deve retornar 409. A duplicidade é por código e cidade.
5. Para 404, informe uma cidade que não conste na consulta. Para 422, envie `id_cidade: 0`.
6. Pare a API com Ctrl+C, execute novamente o mesmo comando e consulte a linha. O registro deve permanecer no banco local.

```json
{
  "codigo": "001.0254-410",
  "nome": "Maringá - Sarandi (Jardim Independência L03)",
  "id_cidade": 2
}
```

O ID 2 é apenas ilustrativo. O código e a identificação da ligação têm como referência a [lista oficial do DER/PR](https://www.der.pr.gov.br/Pagina/Horarios-Vigentes), consultada em 20/10/2026. A vinculação a Sarandi serve à demonstração do cadastro; o modelo atual não descreve todo o trajeto intermunicipal nem comprova horários de circulação. Não invente horários ou atrasos. Antes de uma nova apresentação, confira a vigência da fonte.

## Executar a configuração do Supabase

Esse é um modo diferente, dependente de internet e de uma credencial privada configurada. A autenticação fica a cargo de José. Não compartilhe `.env`, senha de banco nem a conexão completa com o grupo.

Dentro de `backend`, depois da configuração privada:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Neste modo, os links usam a porta **8000**. Não execute `init_db.py` no Supabase existente. Os dados desse banco ainda incluem demonstrações. Use o modo local na porta **8001** para ensaiar novos cadastros.

## Usar os atalhos do VS Code

Abra `TRANSURBAN.code-workspace`. Em Python: Select Interpreter, escolha `backend/.venv/Scripts/python.exe`. Em Terminal → Run Task, há tarefas para modo auditório local, testes completos e execução da configuração normal da API. Não inicie dois servidores na mesma porta.

## Se alguma coisa falhar

| Situação | Conferência |
|---|---|
| `python` não encontrado | Instalar/selecionar Python 3.13 e reabrir o terminal |
| `.venv` não existe | Executar `python preparar.py` na raiz |
| Módulo ausente | Repetir a preparação e conferir `pip check` |
| Banco local indisponível | Iniciar PostgreSQL; conferir privadamente TEST_DATABASE_URL |
| Porta ocupada | Usar a instância existente ou uma porta livre |
| 503 em cidades/linhas | Conferir conexão e estrutura do banco, não só GET `/` |
| 409 no ensaio | O registro já existe; consultar ou usar outro cadastro conferido |
| Aviso do AnyIO/Starlette | Conferir que o resultado final continua sem falhas |

Não altere o ambiente ou baixe dependências durante os 9 minutos. Antes de ir, ensaie o mesmo fluxo com o mesmo computador, carregador e arquivos locais. O vídeo e os logs servem de apoio, identificados como evidência gravada, caso a demonstração ao vivo falhe.

## Limites da versão

As operações desta avaliação são criar e listar cidades e linhas. Edição, exclusão, autenticação de usuários, GPS e horários ao vivo não foram implementados neste recorte. A conciliação completa do catálogo com dados oficiais continua pendente. Publicar o código no GitHub não hospeda a API na internet.
