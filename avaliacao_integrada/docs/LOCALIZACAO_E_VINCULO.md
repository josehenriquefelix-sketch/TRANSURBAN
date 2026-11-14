# Localização e vínculo do veículo

O passageiro pode usar **Minha localização** no mapa. O navegador pede permissão e atualiza o ponto e o círculo de precisão. A localização do passageiro permanece no navegador; não é enviada à API TRANSURBAN. **Parar localização**, sair da conta, ocultar a página ou sair da seção do mapa interrompe esse acompanhamento. Para retomar, use o botão novamente.

O motorista autorizado informa nome público, modelo e prefixo do ônibus, seleciona cidade, linha e sentido e autoriza o compartilhamento. **Iniciar trajeto** verifica primeiro o GPS, salva o perfil e cria a viagem vinculada ao usuário autenticado. Sem permissão ou sinal inicial adequado, a viagem não é criada. A API usa o veículo salvo, rejeita campos extras de proprietário/veículo e bloqueia edição do perfil durante uma viagem ativa. Uma atualização de página exige retomar explicitamente o GPS.

Durante a viagem, o dispositivo envia posições com intervalo mínimo de 10 segundos, enquanto a página e o GPS estiverem disponíveis. Passageiros consultam os veículos da linha a cada 10 segundos. A gestão consulta frota, alertas, autorizações e ocorrências a cada 15 segundos quando o mapa está visível. A fila de manifestações e os indicadores do motorista também atualizam a cada 15 segundos. Respostas e dados de veículo em edição são preservados na atualização em segundo plano. Relatos recebidos continuam privados até a análise da gestão; não viram alertas públicos automaticamente.

A precisão depende do aparelho e do ambiente. O mapa mostra a margem informada pelo GPS, sem garantir posição exata. Não há acesso autorizado ao GPS/ETA da operadora, itinerário de navegação curva a curva nem recarga financeira integrada. O botão de itinerário abre a fonte oficial da linha. O Waze abre navegação externa, sem assumir que sua rota genérica corresponde ao itinerário de ônibus autorizado.

## Conferência

- 35 testes Python: `python -m unittest discover -s tests -p "test_*.py"`.
- 11 testes de comportamento de localização/início: `node --test tests/localizacao.test.cjs` (Node é ferramenta opcional de desenvolvimento, não requisito de execução do site).
- GPS e início de viagem usam dispositivos e APIs simulados nesses 11 testes. Isso valida as transições de permissão, limpeza, margem de precisão e vínculo; não atesta um sensor físico ou a posição da frota da operadora.
- A reconferência da consulta pública Na Hora encontrou os mesmos 66 códigos e nomes do catálogo. Sarandi mantém 22 atendimentos metropolitanos/variantes de 12 documentos DER/PR. O catálogo municipal completo de Sarandi não foi confirmado; não é anunciado como completo.
