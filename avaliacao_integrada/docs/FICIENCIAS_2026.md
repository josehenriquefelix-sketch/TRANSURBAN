# TRANSURBAN na Ficiências 2026

O TRANSURBAN é um sistema de mobilidade destinado à população de Maringá e Sarandi. A participação no evento apresenta o propósito, a implementação e os resultados verificados, com clareza sobre os serviços disponíveis e as integrações pendentes.

## Preparar o computador do evento

1. Instale Git e Python 3.10 ou superior, com Python disponível no PATH.
2. Clone o repositório no VS Code ou use Pull para atualizar a cópia existente.
3. Configure `avaliacao_integrada/backend/.env` pelo exemplo. Utilize o mesmo projeto Supabase da equipe, já migrado. Configure também os e-mails autorizados em `ADMIN_EMAILS`.
4. Execute `INICIAR_TRANSURBAN.cmd`, na raiz do repositório. Aguarde a abertura do site e mantenha o servidor aberto.
5. Execute `VERIFICAR_TRANSURBAN.cmd`, na raiz. A checagem consulta tabelas e testa o site e a API sem criar ou excluir registros.
6. Confira o login e a navegação no próprio computador do evento. As credenciais privadas da conta da equipe ficam no `.env` local e precisam ser transferidas separadamente do GitHub.

O computador precisa de internet para o Supabase e para preparar dependências na primeira execução. O endereço local é `http://127.0.0.1:8000/`. A API de DS está em `/docs`; a documentação de Ciência de Dados está em `/dados/docs`.

## Versão atual — 12/11/2026

O portal foi atualizado com áreas de passageiro, motorista autorizado e central de gestão. Maringá possui 66 linhas municipais conferidas no Na Hora; Sarandi possui 22 atendimentos, incluindo variantes documentadas em 12 tabelas DER/PR. A seleção abre os horários automaticamente. O quadro oficial incorporado permite consultar os pontos e itinerários de Maringá. Consulte [operação e fontes](MOBILIDADE_OPERACAO.md) e [conferência do catálogo](CONFERENCIA_CATALOGO_20261112.json). Google, SMTP, adesão institucional, previsão por ponto e bilhetagem têm dependências externas identificadas.

## Percurso da demonstração

1. Apresente o problema de acesso à informação de transporte entre as duas cidades e a proposta do TRANSURBAN.
2. Mostre a página inicial, a identidade visual e a navegação.
3. Abra o dashboard público e indique as fontes e as datas dos documentos. Os indicadores desse painel descrevem os documentos citados.
4. Mostre a consulta de cidades e linhas. Explique que passageiros e motoristas não alteram esses cadastros.
5. Mostre o login e a separação entre acesso do público e acesso autorizado da equipe.
6. Explique como o navegador chama o FastAPI e como o backend acessa o Supabase por HTTPS. Abra o Swagger para mostrar as rotas.
7. Demonstre uma manifestação e sua resposta na central do escopo autorizado. Para o motorista, mostre perfil, veículo e controles de viagem. Use registros identificados como teste; não atribua avaliações ou posições sintéticas a profissionais reais. A recarga efetiva permanece pendente.
8. Mostre no Supabase os relacionamentos entre as tabelas. As senhas são gerenciadas pelo Supabase Auth; a chave secreta permanece no backend.

## Estado dos serviços

| Recurso | Estado |
| --- | --- |
| Interface pública, início e navegação | Implementados |
| Dashboard com documentos oficiais e referências | Implementado |
| Cadastro, login por e-mail/CPF e sessão | Implementados com Supabase Auth |
| Confirmação e recuperação por e-mail | Implementadas; recebimento em endereço real da equipe precisa ser validado |
| Cidades e linhas | Consulta e CRUD da equipe implementados |
| Chegada em tempo real | Depende de acesso aos dados da operação/GPS |
| Avaliações sobre veículos e motoristas reais | Dependem de cadastro operacional validado |
| Recarga efetiva de transporte | Depende de integração com bilhetagem e pagamento |
| Carteira e avaliações internas de desenvolvimento | Mecanismos testados com registros fictícios |
| Acesso público pela internet | Depende de hospedagem HTTPS e configuração de produção |

## Conferências registradas

Os 12 testes automatizados passaram. As 42 verificações de integração com Supabase estão registradas em `EVIDENCIAS_PORTAL_20261110.json`. Os testes pelo navegador estão em `EVIDENCIAS_INTERFACE_20261111.json`. Uma cópia baixada do GitHub foi testada, e a codificação do CSV publicado foi corrigida para UTF-8.

A validação final deve ser repetida no computador e na rede do evento. O verificador identifica configuração, dependências, tabelas e rotas disponíveis. Ele não garante a disponibilidade futura da internet ou dos serviços externos.
