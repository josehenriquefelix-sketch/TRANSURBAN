# Abrir o TRANSURBAN no VS Code do auditório (Windows)

## Antes de começar

- O computador precisa ter internet, Git for Windows e Python 3.10 ou superior.
- A chave do Supabase fica somente no arquivo local `backend/.env`. Ela não está no GitHub.

## Clonar pelo VS Code

1. Abra o VS Code e pressione `Ctrl + Shift + P`.
2. Digite `Git: Clone` e escolha essa opção.
3. Cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git` e pressione Enter.
4. Escolha uma pasta para salvar o repositório e clique em **Abrir**.
5. Se aparecer a pergunta de confiança, escolha **Sim, confio nos autores**.

Se o repositório já estiver neste computador, abra-o no VS Code e use **Source Control → … → Pull** para buscar as atualizações.

## Configurar o Supabase neste computador

1. Abra a pasta `avaliacao_integrada` no Explorador de Arquivos.
2. Dê dois cliques em `iniciar_local.cmd`.
3. Na primeira abertura, o iniciador cria `backend/.env` a partir do exemplo e abre o arquivo no Bloco de Notas.
4. Preencha `SUPABASE_URL` com a Project URL do projeto da equipe e `SUPABASE_KEY` com a chave secreta desse mesmo projeto. Não use a senha do banco nem coloque a chave no GitHub.
5. Salve com `Ctrl + S` e feche o Bloco de Notas. O iniciador prossegue.

O primeiro início cria o ambiente Python e instala as dependências; pode levar alguns minutos e precisa de internet. Não execute os scripts SQL de criação se as tabelas já existirem no projeto Supabase.

## Abrir e apresentar

- A tela abre em `http://127.0.0.1:8000/`.
- Na tela, clique em **Ver API (Swagger)** para abrir a documentação interativa. O endereço direto é `http://127.0.0.1:8000/docs`.
- Mantenha aberta a janela do servidor durante a apresentação.
- Para iniciar novamente depois da primeira configuração, dê dois cliques em `iniciar_local.cmd`.

## Se não abrir

- Se o Windows disser que Python não foi encontrado, instale Python 3.10 ou superior, marque **Add Python to PATH** e abra o iniciador novamente.
- Se a porta 8000 já estiver em uso, feche a janela antiga do TRANSURBAN com `Ctrl + C` e tente de novo.
- Se a tela abrir, mas o CRUD não carregar, confira a Project URL, a chave secreta e a conexão com a internet no `backend/.env`.
- Nunca compartilhe o `backend/.env`; cada computador precisa da própria cópia local.
