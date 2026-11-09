# TransUrban — Mobilidade

Abra /mobilidade.html pelo mesmo servidor que serve /docs. O painel anterior continua em /.

- Passageiro: consulte o código da linha, veja os ônibus com posição recente e envie nota, lotação e descrição da viagem.
- Motorista: configure TRANSURBAN_MOTORISTA_TOKEN em backend/.env (um segredo aleatório de pelo menos 24 caracteres). No celular, abra o painel por HTTPS, informe linha e veículo e autorize o GPS. Encerre o compartilhamento ao terminar. Use somente um dispositivo por veículo.
- Trajetos: aponte TRANSURBAN_TRAJETOS_JSON para um arquivo local com chaves de códigos de linha e valores em listas de pares [latitude, longitude], em ordem de percurso. Use coordenadas verificadas da operadora. Sem arquivo, o mapa informa que não há trajeto cadastrado.
- A página consulta posições a cada 5 segundos e o servidor descarta leituras com mais de 35 segundos. O navegador pode suspender a transmissão em segundo plano. A posição é do dispositivo autorizado; não representa integração oficial com a frota.
- A chave de motorista é compartilhada no piloto; use somente com operadores de confiança. Para produção, cadastre condutores e veículos individualmente e adote autenticação e moderação antes de abrir avaliações ao público.
- Avaliações e última posição usam um SQLite próprio no servidor. O Supabase continua responsável pelos cadastros existentes. Use um servidor com volume persistente e defina TRANSURBAN_MOB_DB caso queira escolher a localização do arquivo.
- A demonstração do GPS em dois aparelhos exige que ambos acessem a mesma instância por HTTPS. 127.0.0.1 no computador da escola não abre a API no celular.
