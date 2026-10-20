# Apresentação de 20/10/2026

O diretório `presentation/` contém um cenário acadêmico separado do sistema de produção. Perfis, ônibus, posições e tempos são fictícios. Nenhuma API real, autenticação ou geolocalização é usada nesse cenário.

Para gerar o HTML offline:

```powershell
npm run presentation:export
```

O resultado fica em `presentation-export/01-ABRIR-APRESENTACAO.html`. Esse arquivo funciona sozinho, com JavaScript, CSS e ícone embutidos e sem dependências de rede obrigatórias. Links das fontes são opcionais e precisam de internet.

O modelo de demonstração está em `presentation/model.mjs`. Os testes verificam troca de papel, embarque, avaliação única, lotação, avanço de posição, cálculo de exemplo e reinício. O cenário não é importado pelas rotas de produção.

O pacote preparado para a aula inclui ainda roteiro, perguntas prováveis e análise descritiva dos 180 registros acadêmicos sintéticos originais. Não se deve apresentar essa análise ou a estimativa didática como um modelo de IA treinado ou como telemetria da frota.

Dez testes passaram após a inclusão da apresentação. A conferência visual em navegador real continua pendente; é necessário ensaiar no computador da sala antes de apresentar.
