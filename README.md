# TRANSURBAN

Projeto de Desenvolvimento de Sistemas sobre transporte coletivo de Maringá e Sarandi. A proposta é organizar cidades, linhas e seus vínculos em uma base integrada, com consulta e manutenção por um site conectado à API.

A etapa atual implementa cadastro e listagem de **Cidade** e **LinhaOnibus**, conforme o documento da avaliação. O site explica a proposta, permite buscar por nome, código e cidade, filtrar as linhas e cadastrar registros. O layout se adapta a celular, tablet e computador.

## Comece aqui

Leia o **[GUIA_AUDITORIO.md](GUIA_AUDITORIO.md)**. Ele separa instalação, banco local, Supabase, testes, ensaio e solução de problemas.

Em um computador com Git e Python 3.13:

```powershell
git clone https://github.com/josehenriquefelix-sketch/TRANSURBAN.git
cd TRANSURBAN
python preparar.py
code TRANSURBAN.code-workspace
```

É necessário PostgreSQL ativo. O guia traz a configuração do container Docker para uma máquina nova e as instruções do banco já preparado na máquina de José. O download das dependências deve ser feito antes do auditório.

## Executar e testar

Com o PostgreSQL local e TEST_DATABASE_URL configurados, dentro de backend:

```powershell
.\.venv\Scripts\python.exe executar_auditorio.py
```

Abra http://127.0.0.1:8001/docs e http://127.0.0.1:8001/site/. O modo auditório usa um schema PostgreSQL local separado e preserva o .env e o Supabase. A documentação também usa arquivos locais, para apresentação sem CDN. Nenhuma linha fictícia é criada automaticamente.

Em outro terminal dentro de backend:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe verificar_http.py --base-url http://127.0.0.1:8001
```

Resultados registrados na revisão de 20/10/2026: **18 testes aprovados**, um aviso de depreciação de dependência, nenhuma falha, dependências sem conflitos e **13 verificações HTTP aprovadas** em cada modo. Confira sempre o resultado de sua própria execução. As evidências estão em [docs/avaliacao_backend/evidencias](docs/avaliacao_backend/evidencias).

## API

| Método | Caminho | Resultado |
|---|---|---|
| GET | / | Informação da aplicação |
| POST | /cidades | Cria cidade com ID automático, HTTP 201 |
| GET | /cidades | Lista cidades, HTTP 200 |
| POST | /linhas | Cria linha vinculada a cidade, HTTP 201 |
| GET | /linhas | Lista linhas com nome da cidade, HTTP 200 |

Há validação dos campos, rejeição de FK inexistente (404), duplicidade (409), entrada inválida (422) e falha de banco com resposta sem credencial (503). Python, FastAPI, SQLAlchemy, Pydantic e PostgreSQL compõem o backend.

A configuração normal pode acessar o Supabase e usa a porta 8000. Isso exige internet e credencial privada. A API não altera tabelas automaticamente ao iniciar. Não execute init_db.py no Supabase existente.

## Falas e apresentação

- [Roteiro completo, previsto para 8min25s](docs/apresentacao/ROTEIRO_COMPLETO.md)
- Falas individuais: [José](docs/apresentacao/JOSE.md), [Kauan](docs/apresentacao/KAUAN.md), [Bruno](docs/apresentacao/BRUNO.md), [Gustavo](docs/apresentacao/GUSTAVO.md), [Ana Carolina](docs/apresentacao/ANA_CAROLINA.md)
- [Resumo para o grupo](docs/apresentacao/RESUMO_GRUPO.md)

A divisão é uma sugestão de apresentação, sem atribuir autoria individual do código. O roteiro inclui as ações na tela e os testes.

## Dados e escopo

O Supabase ainda contém registros acadêmicos e cadastros não conciliados com fontes oficiais. Eles não comprovam um catálogo operacional de ônibus. A [página oficial de horários do DER/PR](https://www.der.pr.gov.br/Pagina/Horarios-Vigentes) foi consultada como referência de identificação de linhas. A importação completa e rastreável continua pendente.

Não foram implementados neste recorte edição, exclusão, autenticação de usuários, GPS ou horários ao vivo. A autenticação ficará a cargo do responsável pelo projeto. Publicar o código no GitHub não hospeda a API.

## Organização e histórico

O código ativo fica em backend/ e frontend/. Os testes usam PostgreSQL local, com schemas temporários. A integração contínua atual está em .github/workflows/api.yml.

As pastas avaliacao_backend/, ia/, data/, database/ e os demais documentos anteriores foram preservados como histórico. Seus roteiros, massas e resultados não definem requisitos nem comprovam a implementação atual. A fonte de escopo é o [documento do professor](https://docs.google.com/document/d/1I6Eh3J15ieVGsnb_DJX6qNugWwOU5nu3qyLK-XR2RNw/edit), com [matriz de requisitos](docs/avaliacao_backend/MATRIZ.md). As demais entidades do DER não são exigidas na etapa atual.

O .env, a .venv e os dados do PostgreSQL local são privados, ignorados pelo Git e excluídos do pacote de código. O arquivo .env.example contém apenas a configuração pública do container de desenvolvimento local.
