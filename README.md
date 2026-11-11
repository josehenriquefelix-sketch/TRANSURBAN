# Portal TRANSURBAN — atualização de novembro de 2026

O portal completo fica em [avaliacao_integrada](avaliacao_integrada). Inclui login, início, dashboard com fontes oficiais, consulta de cidades e linhas, trajetos e horários, avaliações e passe demonstrativo.

Para abrir no Windows, clone este repositório pelo VS Code, configure o arquivo privado `avaliacao_integrada/backend/.env` usando o `.env.example` e execute `INICIAR_TRANSURBAN.cmd` na raiz. O iniciador prepara o ambiente e abre o site em `http://127.0.0.1:8000/`.

A API de DS fica em `/docs`. A API de Ciência de Dados fica em `/dados/docs`. O projeto Supabase da equipe já recebeu a migração do portal. Cada computador precisa de Python e de sua configuração privada do `.env`.

Consulte as [instruções do portal](avaliacao_integrada/README.md) e o [roteiro da apresentação](avaliacao_integrada/docs/PORTAL_E_APRESENTACAO.md). Horários, avaliações de teste e recargas do módulo de apresentação usam dados de demonstração. O dashboard identifica os documentos oficiais por fonte e data.

---

# TRANSURBAN — API

## Abrir o projeto de apresentação no VS Code (Windows)

1. No VS Code, pressione **Ctrl + Shift + P**, escolha **Git: Clone** e cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`.
2. Escolha uma pasta e abra o repositório clonado.
3. No VS Code, abra **Terminal → New Terminal** e execute:

   `.\avaliacao_integrada\iniciar_local.cmd`

4. Na primeira execução, configure `avaliacao_integrada/backend/.env` com a Project URL e a chave secreta do projeto Supabase. Salve e feche o Bloco de Notas.
5. O site abre sozinho. Clique em **Ver API (Swagger)** para abrir a API. Mantenha a janela do servidor aberta.

Requisitos: Git for Windows, Python 3.10 ou superior e internet na primeira instalação. Para um repositório já clonado, use **Source Control → … → Pull** antes de apresentar. O arquivo `.env` é local e não está no GitHub.

- [Guia rápido para o computador do auditório](avaliacao_integrada/GUIA_RAPIDO_AUDITORIO.md)
- [Instruções completas da integração DS + IA e da FK](avaliacao_integrada/README.md)
- [Adaptação da atividade de chave estrangeira ao TRANSURBAN](avaliacao_integrada/docs/RELACIONAMENTO_FK_CIDADE_LINHA.md)


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
