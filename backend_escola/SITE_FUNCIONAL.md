# Site TRANSURBAN — demonstração funcional

O site desta entrega é servido pela própria API Python em **http://127.0.0.1:8000/app/**. Não precisa de Node, npm ou do antigo frontend-app. A avaliação da API continua em **/docs**. Este sistema é um protótipo acadêmico independente, sem vínculo com a operadora.

## Preparar em casa (Windows)

Abra a pasta `backend_escola` no VS Code. Com Python **3.12** e internet, execute no terminal:

```powershell
py -3.12 iniciar_apresentacao.py --preparar
py -3.12 iniciar_apresentacao.py --testar
py -3.12 iniciar_apresentacao.py
```

Ou use `PREPARAR-WINDOWS.cmd` e depois `APRESENTAR-WINDOWS.cmd`. Após `Application startup complete`, abra `/app/` no navegador desse notebook. Deixe o terminal aberto. Ctrl+C encerra.

## Preparar no Linux da escola

Copie a pasta do projeto, incluindo `backend_escola/web`, dados e documentação. Ambientes virtuais do Windows não funcionam no Linux: prepare novamente no computador da escola, com antecedência e internet.

```bash
cd backend_escola
python3 iniciar_apresentacao.py --preparar
python3 iniciar_apresentacao.py --testar
python3 iniciar_apresentacao.py
```

O comando requer Python 3.12. O inicializador utiliza `apresentacao_local.db` **local**, preserva o `.env` e não conecta ao Supabase. Contas, avaliações e carteira desta instalação ficam nesse banco; não aparecem automaticamente em outro notebook. Código/ZIP não inclui seus dados privados.

## Ensaio no telão, sem slides

1. Use Chrome normal para criar uma conta de **motorista**. Use uma janela **anônima** separada para criar uma conta de **passageiro**. Abas normais compartilham a mesma sessão. Não use senhas pessoais no ensaio.
2. No motorista: Planejar percurso → clique em 2 a 8 pontos, nomeie-os e calcule nas vias. Se o serviço estiver indisponível, salve somente os pontos. O sistema não inventará uma linha de ônibus.
3. Volte ao painel, escolha linha, informe prefixo e sentido de demonstração e inicie a viagem.
4. GPS é opcional: marque consentimento, autorize o navegador e compartilhe. No notebook a localização pode ser imprecisa; acima de 100 m de incerteza o servidor rejeita. Nunca simule um veículo operacional como se fosse real. Dados com mais de 90 segundos deixam de aparecer.
5. No passageiro: encontre a viagem, veja o mapa e registre embarque. Selecione os pontos informados pelo motorista quando disponíveis. Relate vazio, médio, cheio ou superlotado. Confirme desembarque e avalie de 1 a 5 estrelas com descrição.
6. No motorista: abra Avaliações. A descrição e a média aparecem sem divulgar o nome do passageiro.
7. No passageiro: Meu passe → simule recarga PIX, débito ou crédito em até 12 parcelas; simule crédito de VT e mostre o extrato. **Nenhum dinheiro é cobrado ou depositado.**
8. Encerre a viagem no motorista. Mostre `/docs` para relacionar a interface à API e aos testes DS/IA.

Fala sugerida: “Agora mostramos um protótipo funcional da experiência do passageiro e do motorista. As contas e registros são salvos neste computador. O mapa usa dados geográficos reais; as viagens são declaradas por nós. Pagamentos e vale-transporte são demonstrações, sem movimentação de dinheiro.”

## O que funciona e quais são os limites

| Recurso | Comportamento desta entrega |
|---|---|
| Login passageiro/motorista | Cadastro, autenticação, sessão e autorização por perfil; senha com hash PBKDF2 e sal aleatório. Perfil de motorista autodeclarado, sem validação profissional. |
| Mapa | Leaflet local e imagens reais OpenStreetMap; imagens exigem internet. |
| Percurso | OSRM calcula vias entre pontos escolhidos, perfil automóvel. Não equivale a itinerário oficial de ônibus, não é Waze, não tem trânsito nem navegação profissional. |
| Catálogo | 84 linhas recebidas de fonte secundária. Nomes/códigos não garantem horários, pontos ou itinerários atuais da operadora. |
| GPS | Geolocalização voluntária do navegador, compartilhada somente durante a viagem; expira em 90 s. Não conectado ao GPS da frota. |
| Embarque/desembarque | Registros autodeclarados; não validam bilhete e não cobram passagem. Alerta opcional de proximidade usa distância em linha reta ao ponto escolhido, só com a página aberta. |
| Lotação | Relatos dos usuários e motorista; sem sensores nem garantia de ocupação física. |
| Avaliação | Uma por embarque encerrado, 1–5 estrelas e texto; salva no banco, consultável pelo motorista. |
| Clima | Open-Meteo, com horário/fonte e chance de chuva; sem conexão informa indisponibilidade. Previsão não é certeza de chuva. |
| PIX/cartões/12x | Carteira de demonstração, centavos inteiros, proteção contra repetição do mesmo crédito. Sem dados de cartão, QR de cobrança ou gateway. |
| Vale-transporte | Lançamento de teste feito pelo usuário, claramente identificado; não comprova depósito de empresa. |
| Tarifa Maringá 2026 | Nenhum valor é inventado. Sem fonte oficial confirmada, não calculamos quantidade real de passagens. |
| Supabase | Este inicializador usa SQLite. As novas tabelas web não são migradas automaticamente para PostgreSQL; requer migração e revisão próprias. |

Mapa, clima e OSRM dependem de internet e disponibilidade de terceiros. Consultas externas usam timeout e apresentam erro explícito. Não se mantém desenho aproximado, clima inventado ou veículo fictício como substituto silencioso.

## Arquivos e responsabilidade

- `main.py`: FastAPI, ciclo de vida, rotas DS/IA, site estático `/app`, cabeçalhos e tratamento de erro.
- `database.py`: conexão SQLAlchemy, sessões e chave estrangeira no SQLite.
- `models.py` / `schemas.py`: entidades e validações da avaliação DS.
- `models_web.py`: contas, sessões, percursos, viagens, embarques, avaliações, lotação e lançamentos da carteira.
- `web_api.py`: regras, autorização e integrações fixas Open-Meteo/OSRM. Rotas iniciam com `/web-api/`.
- `web/index.html`, `styles.css`, `app.js`: interface responsiva, chamadas JSON à API e mapa.
- `web/vendor/leaflet`: biblioteca de mapa incluída com licença; não precisa baixar código por CDN.
- `data/site`: catálogo e estado explícito das fontes de tarifa/itinerário.
- `dados_publicos.py`: análise IA histórica de Curitiba, separada dos cadastros e viagens do site.
- `test_web.py`: testes de permissões, GPS, carteira, avaliações, persistência e falha dos serviços; fixtures externas somente em testes.

O cookie de sessão é HttpOnly e SameSite=Strict; respostas privadas não devem ser armazenadas em cache. Escritas exigem origem igual à API e JSON. Descrições são exibidas como texto, não HTML executável. Não há recuperação de senha, verificação de e-mail, administração de frota nem implantação pública pronta para produção.

## Projetor e transporte

Ensaie no mesmo notebook que irá ao auditório. Para espelhar a tela, use HDMI ou saída USB-C com suporte a vídeo e adaptador compatível; USB comum sozinho não transmite imagem. No Windows use Win+P → Duplicar. Se usar o computador do auditório, prepare o ambiente lá antes. Um pendrive transporta arquivos, não instala Python nem dependências automaticamente.

GPS funciona em `localhost`/`127.0.0.1` no próprio notebook. Acesso por outro aparelho em uma rede requer HTTPS para geolocalização e configuração de implantação; este pacote não abre o servidor publicamente.

## Verificação desta entrega

Em Linux/Python 3.12: **41 testes aprovados**, com um aviso de depreciação de biblioteca de testes. Chromium: fluxo de duas contas aprovado, sem erros JavaScript, incluindo tentativa de descrição com HTML, saldo persistido e largura de 390 px. O GPS foi emulado somente no teste automatizado; não é evidência de GPS do notebook.

Open-Meteo e OSRM responderam a consultas reais neste ambiente. O carregamento de imagem do mapa também foi verificado em Chromium via proxy; o navegador de QA precisou de exceção ao certificado do proxy (a aplicação não desativa TLS). Há evidências em `evidencias/site-20261019/`. Disponibilidade no auditório continua dependendo da rede. O portal Na Hora Maringá foi consultado e oferece pesquisa de linhas; o site fornece um link externo para a consulta original. O widget externo não foi incorporado como se fosse uma integração própria.

Para repetir o ensaio automatizado de interface (desenvolvedor, opcional): `verificar_site.cjs` requer Node, Playwright e Chromium em `/usr/bin/chromium`, além da API em execução. Execute `node verificar_site.cjs`; `TRANSURBAN_TEST_URL` permite outra origem local e `EVIDENCIAS_SITE` outra pasta. O script cria contas e registros de teste: use banco isolado. Esta ferramenta não é necessária para abrir o site e não foi executada no Windows.
