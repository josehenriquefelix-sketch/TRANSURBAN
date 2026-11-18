# Abrir no computador e no celular

## No computador da escola

1. Instale Python 3.10 ou superior, Git e VS Code, se ainda não estiverem instalados.
2. No VS Code, pressione Ctrl+Shift+P e escolha **Git: Clone**.
3. Cole `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`.
4. Abra o arquivo `TRANSURBAN.code-workspace` da raiz do repositório.
5. Copie seu arquivo privado `.env` para `avaliacao_integrada/backend/.env`. Não publique esse arquivo. Não copie a pasta `.venv`: o iniciador cria outra para esse computador.
6. Pressione Ctrl+Shift+B. A primeira abertura instala as dependências.
7. Abra `http://127.0.0.1:8000/acessos.html` para escolher passageiro, motorista ou gestão.

Se já existe uma cópia, preserve o `.env` e as alterações da equipe antes de usar Git Pull. Não apague a pasta para atualizar.

## Entrar sem complicação

- Passageiro: conta pessoal por e-mail/CPF e senha, ou Google quando configurado para o endereço usado.
- Motorista e gestão: a mesma forma de entrada, mas a conta precisa ter o papel autorizado no banco.
- A conta privada do responsável já foi testada nos dois painéis. As credenciais estão no arquivo privado do computador de casa; não estão no GitHub.
- Não peça vínculo outra vez para uma conta já autorizada. Use o formulário principal de entrada.
- Uma conta de passageiro não ganha acesso profissional apenas escolhendo outro painel.
- Envio de confirmação e notificações depende do SMTP. Sem configuração, a fila no banco não significa que o Gmail recebeu a mensagem.

## Mostrar no celular, na mesma rede

1. Encerre a execução anterior da API com Ctrl+C na janela que a iniciou, ou pelo botão Parar do depurador do VS Code.
2. Abra `avaliacao_integrada/ABRIR_NO_CELULAR.cmd`. No VS Code também existe a tarefa **TRANSURBAN: computador e celular**.
3. Conecte celular e computador ao mesmo Wi-Fi. Mantenha a janela da API aberta.
4. O iniciador mostra um endereço como `http://192.168.1.10:8000/acessos.html`. Digite o endereço exibido no navegador do celular. O número real depende da rede.
5. No computador, continue usando `http://127.0.0.1:8000/acessos.html`.

No celular, `127.0.0.1` aponta para o próprio celular. Use o IP do computador. O modo de rede disponibiliza a API aos dispositivos que alcançam o computador; use uma rede confiável e feche o servidor ao terminar. Não encaminhe portas do roteador para a internet.

O Windows pode solicitar autorização de rede para o Python. Não desative o firewall. Se o acesso for bloqueado, consulte o responsável pela rede da escola; algumas redes isolam os aparelhos e impedem essa comunicação.

## Limite importante do GPS no celular

Navegadores normalmente bloqueiam localização em endereços HTTP de rede, como `http://192.168...`. Esse modo permite mostrar as telas e entrar por senha. Para GPS no celular é necessário HTTPS válido, permissão do usuário e uma rede que permita o acesso. Isso não exige Render, mas exige configurar um endereço/certificado confiável para o ambiente escolhido.

Não desative a segurança do navegador nem ignore avisos de certificado. No computador, localhost é tratado como contexto confiável pelos navegadores compatíveis. A precisão é a informada pelo aparelho; o sistema mostra essa margem e não promete posição sem erro.

Login Google no celular também depende de uma URL de retorno autorizada no Supabase/Google. Para a demonstração pela rede HTTP, use a conta de e-mail/CPF e senha.

## Conferir antes de apresentar

- Abra os três painéis e entre nas contas que vocês vão usar.
- Abra `/docs` para a API de DS e `/dados/docs` para a API de Ciência de Dados.
- Na gestão, o administrador pode abrir o banco e conferir as tabelas.
- Execute `VERIFICAR_TRANSURBAN.cmd`.
- Teste o celular na rede do local antes de começar. O acesso físico desse aparelho precisa ser confirmado no local.
- Não apresente dados de exercício como passageiros reais, nem horários documentais como GPS de uma operadora.

## Render

O iniciador, o VS Code e o login usam o endereço local configurado em `APP_URL`. Não há dependência de Render para executar o projeto. Em 18/11/2026, o serviço antigo `transurban-mobilidade` foi suspenso no painel do Render. O painel confirmou “Suspended by you”. Ele não foi apagado. Para esta entrega, use a execução local.
