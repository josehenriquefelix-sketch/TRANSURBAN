# Atualização de 17/10/2026

- Acrescentados índices de unicidade no banco para impedir duas viagens ativas do mesmo motorista, embarques duplicados na mesma viagem e dois embarques ativos do mesmo passageiro.
- Solicitações concorrentes de início de viagem não encerram silenciosamente uma viagem recém-criada por outra solicitação.
- Conflitos de gravação retornam HTTP 409 com uma orientação de atualização, em vez de erro genérico.
- A última posição de GPS vencida é apagada no próximo acesso autenticado. Viagens abertas há oito horas são encerradas automaticamente nesse acesso.
- Corrigida a execução dos lotes SQLite na prévia local para que as operações de uma transação não sejam intercaladas com outra transação.
- Acrescentados testes de concorrência e de remoção de coordenadas vencidas: seis testes aprovados no total.

O acesso à pasta de histórico Git foi solicitado e concedido. Mesmo assim, a ferramenta rejeitou o envio de origem à hospedagem por exigir uma aprovação adicional indisponível nesta sessão. A versão permanece sem publicação confirmada. Não houve tentativa de contornar esse bloqueio.

Continuam pendentes a inspeção visual em navegador, os testes com dispositivos em circulação e a obtenção/validação dos itinerários geográficos necessários ao ETA.
