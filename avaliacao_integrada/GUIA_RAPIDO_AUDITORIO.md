# Abrir na informática



1. No VS Code: **Ctrl+Shift+P → Git: Clone**.
2. Cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`, escolha uma pasta e abra a cópia.
3. Abra `avaliacao_integrada/TRANSURBAN.code-workspace` como workspace.
4. Pressione **Ctrl+Shift+B**. Na primeira vez, o iniciador prepara o ambiente e solicita a configuração privada em `avaliacao_integrada/backend/.env`.
5. Use os comandos da pasta `avaliacao_integrada/ACESSOS`: `ABRIR_PASSAGEIRO.cmd`, `ABRIR_MOTORISTA.cmd` e `ABRIR_GESTAO.cmd`.

Os atalhos iniciam ou reutilizam o servidor local. Mantenha a janela da API aberta. O `.env`, as senhas, as chaves e a `.venv` não vão para o GitHub.

| Portal | Link no computador que está rodando o projeto |
|---|---|
| Passageiro | http://127.0.0.1:8000/ |
| Motorista | http://127.0.0.1:8000/motorista/ |
| Gestão | http://127.0.0.1:8000/gestao/ |

Se o projeto já está clonado, use **Git Pull** e reinicie o servidor para carregar o backend novo. Preserve as configurações privadas e as alterações locais da equipe.



## Entrada e uso no celular

Abra `http://127.0.0.1:8000/acessos.html` para escolher uma área. A senha é da conta pessoal; o banco confere a autorização de motorista e gestão. As credenciais privadas não acompanham o GitHub.

Para computador e celular na mesma rede, encerre a execução anterior e abra `ABRIR_NO_CELULAR.cmd`. O iniciador informa o IP do computador. Esse modo permite telas e login por senha; GPS no celular exige HTTPS válido. Veja [o passo a passo](docs/COMPUTADOR_E_CELULAR.md).

A equipe tem um [roteiro curto de apresentação](docs/ROTEIRO_APRESENTACAO.md), com José, Bruno, Kauan Celso, Ana Carolina e Gustavo, e uma [conferência dos acessos e do banco](docs/VALIDACAO_ACESSO_20261118.json).


## Operação dos ônibus

A Gestão agora tem Visão geral, Ônibus em viagem e mapa, Ocorrências recebidas e Avaliações. O motorista usa sua conta autorizada, informa ônibus e linha / bairro e inicia. A viagem fica disponível automaticamente para gestão e passageiros; relatos privados são analisados antes de virar avisos públicos.

O banco real continua no Supabase. A consulta técnica local está em `ferramentas/estrutura_banco.html`. O exercício escolar de materiais fica isolado em `/estudo/materiais.html`, sem link nos três painéis.

Use o [roteiro sem slides](docs/ROTEIRO_TRANSURBAN_SEM_SLIDES.docx) e mostre os três painéis e a API no navegador.
