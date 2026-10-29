# TRANSURBAN — API

> **Aplicação integrada DS + IA:** abra [`avaliacao_integrada/README.md`](avaliacao_integrada/README.md). No Windows, execute `avaliacao_integrada/iniciar_local.cmd` para iniciar um único serviço e abrir o painel. Configure `avaliacao_integrada/backend/.env` em cada computador; esse arquivo privado não é enviado ao GitHub.

Backend da avaliação, seguindo o caderno do estudante e o DER do TRANSURBAN.

Cidade é a primeira tabela, com `id_cidade` como PK. Linha de ônibus é a segunda, com `id_linha` como PK e `id_cidade` como FK. O banco armazena o identificador da cidade; a API apresenta o nome da cidade nas consultas de linhas.

## Executar no Windows

Abra `TRANSURBAN.code-workspace` no VS Code e execute na pasta `backend`:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Configure o arquivo local `.env` com a conexão PostgreSQL/Supabase:

```dotenv
DATABASE_URL=postgresql://USUARIO:SENHA@HOST:PORTA/BANCO
DATABASE_SCHEMA=transurban_caderno
```

Nesta máquina, a conexão já está configurada no `.env`. Esse arquivo e a `.venv` ficam fora do Git.

```bat
python -m uvicorn main:app --port 8091
```

Esta revisão utiliza a porta 8091. Para desenvolvimento, a opção `--reload` pode ser acrescentada ao comando.

Acesse a documentação em http://127.0.0.1:8091/docs. A execução anterior na porta 8090 não contém as últimas correções de documentação.

## Demonstração na ordem do caderno

1. Execute `GET /` para conferir a API.
2. Execute `POST /cidades` com `{"nome":"Marialva"}`, cidade real confirmada no [IBGE](https://www.ibge.gov.br/cidades-e-estados/pr/marialva.html). Na revisão de 20/10, ela ainda não estava cadastrada. Paiçandu e sua linha já foram cadastradas no ensaio.
3. Observe o `id_cidade` gerado e execute `GET /cidades`.
4. Execute `POST /linhas` usando o identificador retornado no passo 2:

```json
{
  "nome": "Maringá - Marialva",
  "codigo": "001.0224-400",
  "id_cidade": 1
}
```

Substitua `1` pelo identificador realmente retornado antes de executar. Essa linha consta no [documento oficial do DER-PR](https://www.der.pr.gov.br/sites/der/arquivos_restritos/files/documento/2026-02/Maringa_Marialva_REG0007_Linha0010224400_150226.pdf). Se repetir um cadastro já existente, a API responderá 409 com `Registro já cadastrado`.

5. Execute `GET /linhas`. A resposta apresenta `cidade` com o nome, além de `id_linha`, `nome` e `codigo`.
6. Faça outro `POST /linhas` com um `id_cidade` inexistente. A resposta esperada é HTTP 404 com `{"detail":"Cidade não encontrada"}`.
7. Encerre o servidor com `Ctrl+C` e execute `deactivate`.

## Arquivos

| Arquivo | Função |
|---|---|
| `backend/database.py` | Carrega `.env`, cria o engine, as sessões e a Base |
| `backend/models.py` | Mapeia as tabelas, PKs, FK e o relacionamento |
| `backend/schemas.py` | Define os dados de entrada e saída |
| `backend/main.py` | Cria a aplicação e as rotas POST e GET |
| `backend/requirements.txt` | Registra as dependências instaladas |
| `docs/DER.md` | DER do projeto autoral |
| `docs/dicionario_dados.md` | Campos, tipos e regras do projeto |

O recorte desta avaliação utiliza Cidade e Linha de Ônibus. Os demais relacionamentos do DER servem de contexto para o projeto e para o desafio de compreensão do caderno.

Os dados iniciais e suas fontes oficiais estão em [docs/FONTES.md](docs/FONTES.md). O schema `transurban_caderno` já foi criado no Supabase desta máquina. Em outro banco, crie esse schema antes de iniciar ou deixe `DATABASE_SCHEMA` vazio para utilizar o schema padrão.

Os [roteiros de apresentação](docs/ROTEIROS_APRESENTACAO.md) incluem falas, demonstração e perguntas frequentes. O [relatório de revisão](docs/REVISAO_FINAL.md) registra os testes e os ajustes feitos.

Foram feitos dois ajustes de integração às regras do TRANSURBAN: seleção explícita do schema no mapeamento SQLAlchemy, pois a conexão do Supabase não aplicou o parâmetro da URL; e tratamento de duplicidades e limites de texto definidos no dicionário. As rotas e o percurso PK → FK seguem o caderno.
