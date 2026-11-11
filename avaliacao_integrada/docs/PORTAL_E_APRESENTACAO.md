# TRANSURBAN — roteiro do portal

## O que demonstrar

1. Abra o site e apresente a proposta de mobilidade entre Maringá e Sarandi.
2. Entre na conta pelo e-mail ou CPF. As senhas são verificadas pelo Supabase Auth, e os cookies de sessão são HttpOnly.
3. Abra o dashboard. Os indicadores oficiais vêm da tabela do DER/PR da linha Maringá–Sarandi, com vigência informada em 15/03/2026. Abaixo aparecem registros públicos de 2023 e 2025, com atribuição e fonte. Os dados de atraso são do CSV sintético acadêmico.
4. Consulte cidades e linhas. A equipe pode cadastrar, consultar, editar e excluir após entrar com uma conta autorizada. Um passageiro consulta os registros e não pode alterá-los.
5. Em trajetos, escolha o sentido e uma data. A tela mostra paradas, embarque e chegada programados. Os horários desse módulo são sintéticos e estão identificados.
6. Envie uma avaliação com notas separadas para ônibus e motorista. Mostre o registro no histórico da conta e no Supabase. A combinação de conta, horário e dia aceita uma avaliação.
7. Abra o passe. Escolha um valor, aceite a indicação de demonstração, revise e confirme. Mostre o saldo e o histórico. Os valores são fictícios. O backend calcula em centavos e uma função PostgreSQL grava o movimento e o saldo na mesma transação, protegida contra repetição da operação.
8. Abra a documentação de DS pelo menu. A documentação das análises fica no botão de Ciência de Dados no dashboard.
9. Saia da conta e mostre que o passe e as avaliações exigem autenticação.

## Como explicar a comunicação

O HTML organiza as telas, o CSS define as cores, os tamanhos e a adaptação ao dispositivo, e o JavaScript navega entre as páginas e chama a API com `fetch`. O FastAPI valida os dados e consulta o Supabase por HTTPS. O PostgreSQL preserva as chaves, os relacionamentos e a transação da recarga demonstrativa. O pandas calcula as quatro totalizações do CSV acadêmico. A chave secreta fica no `.env` do backend.

## Documentos consultados

- DER/PR — tabela da linha 001.0254-410, Maringá–Sarandi (Jd. Independência), vigência informada de 15/03/2026. https://www.der.pr.gov.br/sites/der/arquivos_restritos/files/documento/2026-03/Maringa_Sarandi_JdIndependencia_L03_REG0511_Linha0010254410_150326.pdf
- Secretaria Municipal de Mobilidade Urbana de Maringá — Ofício 18/2023/SECSEMOB, de 10/03/2023, assinado em 13/03/2023. https://sapl.cmm.pr.gov.br/media/sapl/public/documentoacessorio/2023/24786/req_173.pdf
- Câmara Municipal de Sarandi — Indicação 223/2025. A indicação solicita atendimento de bairros, sem comprovar execução das linhas. https://sapl.sarandi.pr.leg.br/materia/9891/acompanhar-materia/

As fontes foram consultadas em 10/11/2026. Os textos citados são trechos dos documentos atribuídos às instituições. O site não apresenta depoimentos inventados de passageiros. Os números oficiais descrevem a linha e o documento referenciados, sem representar toda a rede ou uma medição ao vivo.

## Limites que devem ser apresentados

As recargas não compram passagens reais. O módulo não recebe posições de GPS dos ônibus nem previsões ao vivo. Os veículos, motoristas e horários da consulta são demonstrativos. A conta fictícia usa uma senha privada no `.env`, que precisa ser transferida separadamente do GitHub. O recebimento do e-mail de confirmação/recuperação depende do serviço de e-mail do Supabase e deve ser testado com o endereço real da equipe.
