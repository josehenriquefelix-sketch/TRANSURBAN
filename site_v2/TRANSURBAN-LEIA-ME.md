# TransUrban — versão 2

Consulta de linhas de Maringá e Sarandi, perfis de passageiro/motorista, viagens colaborativas, embarque, avaliação com descrição e lotação.

## Abrir agora

Abra `preview/index.html`. Esta é uma **prévia offline**: busca, filtros, detalhes, navegação e favoritos locais funcionam sem servidor. Contas, GPS compartilhado e avaliações não são simulados como recursos ativos nesta prévia.

## Executar o servidor para desenvolvimento

Requisitos: Node.js 22.13 ou superior e npm. Na pasta deste projeto:

```powershell
npm ci
npm run preview:local
```

Acesse `http://127.0.0.1:5174`. O aviso amarelo identifica o login de teste local. Há identidades de teste separadas para passageiro e motorista, selecionadas pelo fluxo de entrada. Não use credenciais reais nessa prévia. Os dados de desenvolvimento são gravados em `.local-dev/transurban.sqlite`, ignorado pelo Git. A prévia alternativa existe porque o runtime Cloudflare/workerd não conseguiu iniciar neste computador.

## Autenticação de produção

O servidor publicado usa exclusivamente o login do ChatGPT fornecido por Sites; não armazena senhas. O identificador de usuário é recebido do servidor da plataforma, não do corpo de uma solicitação. O usuário cria um perfil de passageiro ou motorista após entrar. O tipo de perfil não pode ser trocado por uma chamada comum. Motoristas são **autodeclarados, não verificados pela operadora**.

O arquivo `scripts/dev-node.mjs` é exclusivo de teste em loopback. Seu login de teste não faz parte do Worker de produção. Não o exponha por túnel ou em rede pública.

## Dados e pesquisa

- 84 linhas pesquisadas: 66 de Maringá e 18 de Sarandi.
- Fontes: [Maringá](https://onibus.online/pr/maringa/) e [Sarandi](https://onibus.online/pr/sarandi/), com links individuais e datas declaradas de atualização em `lib/catalog.json`.
- Consulta: 16/10/2026, conforme a data local do usuário.
- São fontes secundárias. A listagem não comprova a operação atual nem garante cobertura integral da rede.
- A lista histórica da Prefeitura de Maringá foi consultada, mas continha PDFs com datas antigas, inclusive de 2005. Esses horários não alimentam previsões.
- Os registros sintéticos da primeira versão não são apresentados como indicadores reais desta versão.

## Funcionalidades implementadas

- Busca por número, destino e texto dos sentidos; filtro por cidade; favoritos neste navegador.
- Login da plataforma e perfis persistentes no banco D1.
- Início/fim de viagem por motorista, prefixo do veículo e sentido.
- GPS voluntário, com consentimento na interface e atualização da última posição. Não é criado histórico de posições.
- Ocultação de posições com mais de 90 segundos, rejeição de GPS impreciso e remoção de coordenadas ao encerrar a viagem.
- Passageiro registra embarque em uma viagem com GPS recente.
- Uma avaliação por embarque/viagem, nota de 1 a 5, descrição de 3 a 500 caracteres, lotação `vazia`, `normal` ou `cheia`.
- Média de avaliações do motorista nas viagens vinculadas ao perfil; lotação da viagem com relatos dos últimos 15 minutos.
- Descrições não são publicadas nesta versão; ficam armazenadas com a avaliação.
- Exclusão dos dados da própria conta.
- Motor de ETA que exige posição recente, sentido e geometria validados, compatibilidade com o trajeto e velocidade válida. Não transforma distância em linha reta ou rota de automóvel em previsão de ônibus.

## O que ainda depende de integração externa

Não há API oficial da TCCC/Cidade Verde conectada. Nenhuma geometria foi validada e importada em `lib/routes.json`. Portanto **não há previsão operacional de chegada ao ponto ou ao terminal** nesta entrega. Os botões informam a indisponibilidade. O motor foi testado com geometrias sintéticas exclusivamente nos testes; essas geometrias não fazem parte do catálogo.

Para habilitar ETA de uma linha, adicionar em `lib/routes.json` um registro com `lineId`, `direction` (`terminal` ou `bairro`), `verified:true`, `points` em ordem de viagem (`{lat,lng}`), `terminal` (`{lat,lng}`) e procedência verificável. Itinerários circulares ou com laços precisam de segmentação específica antes de uso; o algoritmo atual de projeção pressupõe um percurso direcional sem ambiguidades de posição. É necessário validar com a operadora os itinerários e pontos antes de usar previsões para orientar passageiros.

O compartilhamento depende de GPS e página aberta; navegadores podem suspender a localização em segundo plano. Só uma futura versão de app poderá tratar rastreamento nativo em segundo plano.

## Validação realizada

```powershell
npm test
npx tsc --noEmit
npm run build
```

Os testes usam SQLite em memória e as migrações geradas, e verificam autenticação, origem de solicitações, papéis, propriedade de viagens, consentimento de GPS, precisão, expiração, embarque, avaliação, duplicatas e exclusão. O teste HTTP exercita a mesma API pelo servidor de prévia local.

Compilação de produção e TypeScript passaram. A inspeção visual em navegador não foi concluída: o navegador conectado não acessou o loopback do ambiente e bloqueou a abertura de arquivos locais por política. Não houve teste real com dois dispositivos em circulação.

## Hospedagem e banco

O projeto Sites existente foi preservado em `.openai/hosting.json`, agora com binding D1 `DB` e sem configuração de site estático. As migrações estão em `drizzle/` e também são copiadas para a saída de compilação. Para o fluxo normal de desenvolvimento com Cloudflare, aplique as migrações locais conforme a documentação do starter antes de `npm run dev`.

A publicação **não foi concluída**: o envio de origem foi rejeitado automaticamente porque a sessão não permite a aprovação adicional exigida. Nenhum link de produção desta versão foi confirmado. O diretório `dist/` contém a compilação gerada, mas não indica que o site esteja no ar.

## Estrutura

- `app/dashboard.tsx`: interface responsiva e fluxos.
- `app/api/[...action]/route.ts`: ponte entre autenticação Sites e API.
- `lib/api.mjs`: regras de servidor e autorização.
- `lib/transit.mjs`: validação e projeção do ETA.
- `lib/catalog.json`: catálogo pesquisado, fontes e datas.
- `db/` e `drizzle/`: esquema e migrações.
- `scripts/dev-node.mjs`: prévia local de QA, com identidade de teste.
- `scripts/export-preview.mjs`: geração da prévia offline.
- `tests/`: testes de comportamento, permissão e HTTP.

Uma adaptação limitada em `scripts/windows-fs-compat.mjs` usa a implementação padrão de resolução de caminhos quando a variante nativa do Windows retorna EPERM para arquivos normalmente acessíveis. Ela só afeta os scripts locais de compilação/prévia.
