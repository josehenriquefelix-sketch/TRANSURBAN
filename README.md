# TRANSURBAN

Site de mobilidade entre **Maringá e Sarandi**, com áreas de passageiro, motorista e gestão. Projeto escolar independente: HTML, CSS e JavaScript; API Python/FastAPI; PostgreSQL no Supabase por HTTPS. Executado localmente pelo VS Code, sem Render.

**Comece pelo [passo a passo para o computador da escola](avaliacao_integrada/PASSO_A_PASSO_ESCOLA.md).**

## Baixar e abrir

No terminal do VS Code, em uma pasta onde possa gravar:

```powershell
git clone https://github.com/josehenriquefelix-sketch/TRANSURBAN.git
cd TRANSURBAN
```

Abra `TRANSURBAN.code-workspace`. Copie o `.env` privado da equipe para `avaliacao_integrada/backend/.env`; ele é levado separadamente e não está no GitHub. Pressione **Ctrl+Shift+B** ou execute:

```powershell
.\INICIAR_TRANSURBAN.cmd
```

É necessário ter Python 3.10 ou superior, Git, VS Code e internet para acessar o Supabase. Esta rodada foi testada com Python 3.13 no Windows. Na primeira abertura, aguarde a instalação das dependências. Mantenha o servidor aberto.

| O que abrir | Endereço no computador que iniciou o servidor |
|---|---|
| Passageiro | http://127.0.0.1:8000/ |
| Motorista | http://127.0.0.1:8000/motorista/ |
| Gestão | http://127.0.0.1:8000/gestao/ |
| API de DS / Swagger | http://127.0.0.1:8000/docs |
| Ciência de Dados | http://127.0.0.1:8000/dados/ |
| API de Ciência de Dados | http://127.0.0.1:8000/dados/docs |
| Slides da equipe | http://127.0.0.1:8000/equipe/apresentacao |
| Banner em PDF | http://127.0.0.1:8000/equipe/banner.pdf |

Motorista e gestão exigem conta autorizada. As senhas e chaves não são publicadas. A gestão fica em um painel separado e a API confere as permissões.

## Versão de 24/11/2026

- **12 tabelas ativas**, com PK e RLS; [modelo e relações](avaliacao_integrada/docs/BANCO_CONFERIDO.md).
- Duas cidades e 88 entradas documentadas no catálogo: 66 linhas municipais de Maringá e 22 serviços/variantes metropolitanos de Sarandi. A cobertura municipal completa de Sarandi não foi confirmada.
- Histórico de respostas e fila privada incorporados aos registros. Dados anteriores preservados em schema de arquivo privado, fora da API.
- Horários e saldos fictícios retirados da API. A recarga integrada depende de autorização da bilhetagem; o site orienta aos canais oficiais.
- Painéis com paletas próprias, menu por toque/teclado e campos adaptados para celular.

[Leia a revisão e suas fontes](avaliacao_integrada/docs/REVISAO_20261124.md), os [resultados dos testes reais](avaliacao_integrada/docs/VALIDACAO_ENTREGA_20261124.json) e as [instruções do banco](avaliacao_integrada/database/README.md). Para usar o mesmo Supabase na escola, **não recrie as tabelas**.

## Apresentação e banner

- [Falas: José → Bruno → Cauã → Ana Carolina → Gustavo](avaliacao_integrada/docs/ROTEIRO_APRESENTACAO.md).
- [Slides HTML para abrir no navegador](avaliacao_integrada/docs/APRESENTACAO_TRANSURBAN.html): baixe o projeto e abra o arquivo; a página do GitHub mostra seu código.
- [Banner editável no Canva](https://www.canva.com/design/DAHaDq9Tc8I/oFhhzQ4O4VNY-gSqSoUNbg/edit).
- [PDF do banner revisado](avaliacao_integrada/docs/BANNER_TRANSURBAN_20261124.pdf), exportado e conferido visualmente. Mantém A4 do arquivo original; o tamanho exigido pela escola precisa ser confirmado.

## Testar e usar no celular

Execute `VERIFICAR_TRANSURBAN.cmd`. Os comandos de teste estão no [README técnico](avaliacao_integrada/README.md).

Para telas e login no celular, use `avaliacao_integrada/ABRIR_NO_CELULAR.cmd` e o endereço da rede que ele informa. O aparelho deve estar na mesma rede. GPS no celular exige contexto seguro HTTPS e permissão; um endereço HTTP da rede local não garante geolocalização. Veja [computador e celular](avaliacao_integrada/docs/COMPUTADOR_E_CELULAR.md).

SMTP e Ollama continuam sem credenciais fornecidas. Não há confirmação de entrega no Gmail, GPS físico ou integração oficial de telemetria. Os números do CSV são sintéticos, identificados e separados do catálogo público. Os arquivos em `historico/` registram etapas anteriores e não descrevem o modelo ativo atual.
