# TRANSURBAN — levar para o outro notebook

Apresentação em 20/10/2026, sem slides: API no Swagger e explicação dos arquivos no VS Code.

## O que está pronto e o que está pendente

A API Python permite cadastrar e consultar cidades e linhas, relacionar as tabelas e rejeitar cidade inexistente e texto vazio. A parte de Ciência de Dados lê 180 observações sintéticas em CSV e fornece qualidade, resumo e agrupamentos em JSON. O painel da própria API é opcional; não é necessário para esta apresentação.

No Supabase, as capturas escolares confirmaram tabelas com PK, FK, IDs automáticos, restrições de unicidade e RLS ativo sem políticas. A alteração do nome da linha para 150 caracteres foi executada pelo usuário. A conexão Python com o pooler foi interrompida antes da autenticação durante a negociação inicial de TLS: causa ainda não determinada. Não afirmar que POST/GET foram comprovados no Supabase. Para o auditório, o inicializador deste pacote usa explicitamente SQLite local e não depende desse acesso.

## Transferir e preparar HOJE

1. Copie o ZIP para o outro notebook por pendrive ou download e EXTRAIA tudo. Não execute dentro do ZIP.
2. Instale Python **3.12**, se necessário. No Windows, marque a opção de adicionar Python ao PATH e instale o Python Launcher. Abra a pasta extraída no VS Code.
3. No terminal, entre em `backend_escola`. Os comandos abaixo partem dessa pasta. Não copie ambientes virtuais de outro computador.
4. Prepare com internet. Depois dessa preparação, a apresentação local não precisa da internet. Não deixe a instalação para o auditório.

### Windows (PowerShell)

```powershell
cd backend_escola
py -3.12 iniciar_apresentacao.py --preparar
py -3.12 iniciar_apresentacao.py --testar
py -3.12 iniciar_apresentacao.py --evidencias
py -3.12 iniciar_apresentacao.py
```

### Linux

```bash
cd backend_escola
python3.12 iniciar_apresentacao.py --preparar
python3.12 iniciar_apresentacao.py --testar
python3.12 iniciar_apresentacao.py --evidencias
python3.12 iniciar_apresentacao.py
```

Se `python3.12` não existir, confira `python3 --version`; use `python3` somente se indicar 3.12. Em Linux pode ser necessário instalar o pacote de venv correspondente com o responsável pelo notebook.

O teste automático deve terminar com 22 testes aprovados; o gerador confere 16 requisições HTTP em banco temporário e guarda os resultados em `backend_escola/evidencias/execucao-*`. Confirme os resultados NO NOVO NOTEBOOK. A validação na nuvem não comprova a instalação em outra máquina. Windows tem instruções fornecidas, mas não foi executado no ambiente Linux de preparação.

Depois de `Application startup complete`, abra no navegador DO MESMO NOTEBOOK:

- Swagger: `http://127.0.0.1:8000/docs`
- Saúde: `http://127.0.0.1:8000/health` → `status: ok`, `banco: sqlite_local`.
- Painel opcional: `http://127.0.0.1:8000/painel/`.

O inicializador usa `apresentacao_local.db`, preserva `.env` e substitui DATABASE_URL e CSV_PATH apenas no processo filho. O banco começa vazio no pacote. Nenhum login, GPS, pagamento ou modelo preditivo faz parte desta demonstração. Não é necessário executar npm nem abrir o site React.

## Amanhã no auditório

1. Conecte o carregador, teste o projetor e aumente o zoom do navegador para leitura da plateia.
2. Abra o terminal em `backend_escola`. Execute somente o último comando de iniciar, correspondente ao sistema. Não reinstale bibliotecas.
3. Confira `/health` e `/docs`, mantenha o terminal aberto e apresente pelo roteiro `apresentacoes/ROTEIRO_API_SEM_SLIDES_20_10.md`.
4. No VS Code, deixe abertos `database.py`, `models.py`, `schemas.py` e `main.py`. Não projete `.env` ou senhas.
5. Na demonstração, use sempre o ID devolvido pelo POST da cidade. Confirme por GET que o ID 999999 não existe antes do teste de erro. O banco do ensaio pode já conter registros; não pressuponha IDs 1 ou 2.
6. Ctrl+C encerra a API. Reinicie e faça GET para conferir persistência dos cadastros no mesmo arquivo local.

Se a porta 8000 estiver ocupada, acrescente `--port 8001` ao comando de iniciar e use esse número no navegador. Não encerre processos desconhecidos.

Se houver falha não resolvida na hora, mostre os JSONs de `backend_escola/evidencias/` e informe se foram gerados no notebook ou na validação na nuvem. Não apresente uma captura antiga como teste ao vivo.

## Quem fala

| Integrante | Explicação |
|---|---|
| Bruno | Abertura curta, pode ler; sem operar o computador |
| Kauan | Explicação curta de GET, pode ler; sem operar o computador |
| José Henrique | Arquivos, chaves, relacionamento e demonstração POST/GET |
| Gustavo | Erros 404 e 422 e confirmação de não inserção |
| Jullyany | CSV sintético, unidade de análise e qualidade |
| Camila | Média, mediana, total e agrupamentos |
| Ana Carolina | Evidências, GitHub e limitações |

As falas individuais estão em `apresentacoes/api-sem-slides/falas/`. O PDF nessa mesma pasta é um roteiro de leitura A4, não slides.

## Conferência dos resultados de IA

180 observações, soma de 1.362 minutos de atraso por observação, média 7,5667 minutos, mediana 8, máximo 12 em sete observações. Os dados não representam viagens completas, minutos perdidos por passageiros ou operação real. Rotas: `/ia/qualidade`, `/ia/resumo`, `/ia/agrupamentos/linha`, `/ia/agrupamentos/data`.

## Conteúdo e limites do pacote

O pacote inclui os arquivos versionados do projeto (API, CSV, testes, SQL, modelagem brModelo, documentação, site V2 e versões anteriores), sem `.git`, credenciais, bancos pessoais ou ambientes virtuais. Os slides históricos foram excluídos. Para amanhã, o caminho recomendado é apenas `backend_escola` e o roteiro sem slides. O arquivo `.brM3` fica em `avaliacao_backend/modelagem/`; abra-o em versão compatível do brModelo.

O frontend React/Vite chamado `frontend-app`, visto no computador da escola, não estava no checkout fornecido e não integra este ZIP. `site_v2` é outra versão; não afirmar que é esse frontend ou que está integrado automaticamente com a API escolar.

Não copiar senhas ou `.env` para GitHub/Classroom. A senha antes compartilhada no chat deve permanecer substituída por uma nova senha privada. A entrega no Classroom não foi realizada por este pacote.

GitHub: https://github.com/josehenriquefelix-sketch/TRANSURBAN/tree/entrega/escola-apresentacao-2026-10-20

As alterações estão na branch indicada; isso não significa merge na main ou hospedagem pública.
