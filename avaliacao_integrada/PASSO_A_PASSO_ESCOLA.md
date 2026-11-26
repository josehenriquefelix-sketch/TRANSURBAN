# TRANSURBAN na escola — comece por aqui

## 1. O que levar de casa

- Link do GitHub: `https://github.com/josehenriquefelix-sketch/TRANSURBAN.git`.
- Arquivo privado `backend/.env`, levado separadamente em um pendrive ou outro meio privado.
- E-mail e senha da conta autorizada, guardados em particular.
- Roteiro sem slides em `docs/ROTEIRO_TRANSURBAN_SEM_SLIDES.docx`; mostrar os sites e a API durante as falas.

O GitHub não contém o `.env` nem as senhas. Copiar as credenciais privadas é uma etapa necessária para usar o mesmo Supabase da equipe.

## 2. Conferir o computador da escola

Abra o VS Code e escolha **Terminal → Novo Terminal**. Rode:

```powershell
git --version
python --version
```

É necessário ter Git e Python 3.10 ou superior. O computador também precisa de internet para instalar dependências e acessar o Supabase. O VS Code sozinho não instala esses programas.

## 3. Baixar uma cópia pelo Git

No terminal, em uma pasta onde você possa gravar, cole:

```powershell
git clone https://github.com/josehenriquefelix-sketch/TRANSURBAN.git TRANSURBAN_ESCOLA
```

Aguarde terminar. Se aparecer que `TRANSURBAN_ESCOLA` já existe, preserve essa pasta e use outro nome vazio, por exemplo `TRANSURBAN_ESCOLA_2`. Não apague trabalhos antigos para atualizar.

No VS Code, escolha **Arquivo → Abrir Pasta** e selecione a pasta **avaliacao_integrada**, que está dentro da cópia que acabou de baixar.

## 4. Colocar a configuração privada

Copie o arquivo real `.env` levado de casa para a pasta **backend** da cópia da escola. O destino deve ficar assim:

```text
TRANSURBAN_ESCOLA/
  avaliacao_integrada/
    backend/
      .env
      .env.example
      main.py
```

O nome é `.env`, sem acrescentar `.txt`. O `.env.example` contém valores fictícios e serve de modelo. Não substitua a chave real por um exemplo. Não envie o `.env` para o GitHub e não o projete na apresentação.

Com a pasta `avaliacao_integrada` aberta no VS Code, abra **Terminal → Novo Terminal** e confira que o terminal está nessa pasta. Rode:

```powershell
git check-ignore backend/.env
```

O resultado deve mostrar `backend/.env`: isso confirma que o arquivo privado está ignorado pelo Git.

## 5. Iniciar site e API

No mesmo terminal:

```powershell
.\iniciar_local.cmd
```

Na primeira vez, o iniciador cria o ambiente e instala as dependências. Aguarde o servidor iniciar. Mantenha esse terminal aberto durante o uso.

O atalho **Ctrl+Shift+B** também inicia o projeto quando a pasta `avaliacao_integrada` está aberta no VS Code.

## 6. Abrir os endereços no navegador

| O que mostrar | Endereço no computador da escola |
|---|---|
| Escolher uma área | `http://127.0.0.1:8000/acessos.html` |
| Passageiro | `http://127.0.0.1:8000/` |
| Motorista | `http://127.0.0.1:8000/motorista/` |
| Gestão | `http://127.0.0.1:8000/gestao/` |
| API de DS — Swagger | `http://127.0.0.1:8000/docs` |
| API de Ciência de Dados | `http://127.0.0.1:8000/dados/docs` |
| Dashboard de estudo | `http://127.0.0.1:8000/dados/` |

Entre no Motorista e na Gestão pelo formulário principal, usando a conta já autorizada. Não é necessário solicitar vínculo novamente. Não existe uma senha universal nos arquivos públicos do site.

## 7. Fazer a última conferência

Abra um segundo terminal em `avaliacao_integrada` e execute:

```powershell
.\VERIFICAR_TRANSURBAN.cmd
```

Depois, confirme pessoalmente:

- [ ] Passageiro abre e consulta cidades e linhas.
- [ ] Motorista entra com a conta autorizada.
- [ ] Gestão entra e carrega os indicadores.
- [ ] A API abre em `/docs` e uma consulta GET responde.
- [ ] O Supabase está acessível pela internet.
- [ ] As senhas e o `.env` não estão sendo projetados.

## 8. Ver todas as tabelas

No computador, abra `ferramentas/estrutura_banco.html`. É uma visualização técnica local dos metadados conferidos, sem registros de pessoas. O arquivo `docs/BANCO_CONFERIDO.md` explica as PKs e FKs. Os scripts SQL estão em `database/`.

Para ver o banco atual e seus registros, entre no projeto da equipe pelo Supabase e abra **Table Editor**. Selecione o esquema `public` para as tabelas da aplicação. As contas e senhas são gerenciadas pelo Supabase Auth; não são uma tabela pública de senhas.

O banco continua no Supabase. A visualização local não substitui o banco nem executa migrações. Para usar o mesmo projeto já configurado, basta levar o `.env` correto; não é necessário recriar as tabelas a cada clone.

## 9. Apresentar sem slides

Abra os três painéis e a API no navegador. As falas curtas estão em `docs/ROTEIRO_TRANSURBAN_SEM_SLIDES.docx` e `docs/ROTEIRO_APRESENTACAO.md`.

Ordem: **José, Bruno, Kauan Celso, Ana Carolina e Gustavo**. Entrem nas contas antes de projetar a tela e mantenham o servidor aberto.

## 10. Se quiser mostrar no celular

Encerre a execução anterior da API com Ctrl+C no terminal que a iniciou. Abra `ABRIR_NO_CELULAR.cmd`. Conecte os aparelhos ao mesmo Wi-Fi e use, no celular, o endereço IP exibido pelo iniciador.

`127.0.0.1` no celular aponta para o próprio celular. Use o IP do computador. A rede da escola pode bloquear a comunicação entre os aparelhos. O modo HTTP permite telas e login por senha; GPS no celular exige HTTPS válido e permissão. Login Google também depende de um retorno autorizado para o endereço usado.

## Se aparecer um erro

| Mensagem ou situação | O que conferir |
|---|---|
| `git` não é reconhecido | Git instalado e disponível no terminal. Reinicie o VS Code depois de instalar. |
| Python não encontrado | Python 3.10+ instalado e disponível no PATH. |
| Pasta já existe ao clonar | Usar uma pasta nova, preservando a anterior. |
| Site não abre | Terminal da API ativo, endereço correto e porta 8000 disponível. |
| Porta ocupada / instância antiga | Encerrar a execução anterior do TRANSURBAN e iniciar a versão nova. |
| Supabase não configurado | Arquivo real `.env` dentro de `backend`, com o nome correto. |
| Falha ao instalar dependências | Internet, acesso ao PyPI e permissão de gravação na pasta. |
| Acesso profissional não autorizado | Conta correta e papel liberado no Supabase; usar a conta autorizada levada de casa. |
| Celular não conecta | Mesmo Wi-Fi, IP correto e permissão da rede do local. |

Se uma cópia antiga já estiver correta e sem alterações de código, você pode atualizá-la pela raiz com `git pull --ff-only`, preservando o `.env`. Se o Git informar conflito ou divergência, não use comandos de descarte: uma cópia nova em outra pasta mantém o trabalho anterior seguro.

## Limites da conferência

O projeto pode ser testado por clone e instalação novos neste computador. O funcionamento na escola também depende do Python, do Git, da internet, das permissões da máquina e da configuração privada. Avisos de aprovação por e-mail dependem do SMTP próprio; o recebimento de recuperação do Supabase foi relatado pelo usuário; telemetria oficial da operadora, pagamento e bilhetagem não estão integrados. Os testes de coordenadas sintéticas não comprovam GPS físico no aparelho.
