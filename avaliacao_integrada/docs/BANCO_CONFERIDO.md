# Banco essencial — conferido em 24/11/2026

O esquema ativo `public` tem **12 tabelas**, todas com PK e RLS habilitada. As contas e senhas são gerenciadas no esquema interno `auth` do Supabase; essas tabelas internas não fazem parte das 12 tabelas do aplicativo.

| Tabela | Finalidade | PK | Relações públicas |
|---|---|---|---|
| `cidade` | As duas cidades atendidas: Maringá e Sarandi. | id_cidade | — |
| `linha_onibus` | Códigos e nomes do catálogo documentado, vinculados à cidade. | id_linha | id_cidade → cidade.id_cidade |
| `tu_acesso` | Permissão profissional de motorista ou gestor e sua área de atendimento. | usuario_id, papel | — |
| `tu_alerta_operacional` | Avisos confirmados pela gestão, com local e prazo de validade. | id | — |
| `tu_chamado` | Relatos privados, local opcional e histórico do atendimento. | id | — |
| `tu_favorito` | Linhas favoritas de cada usuário; chave composta evita repetição. | usuario_id, linha_id | — |
| `tu_manifestacao` | Notas, elogios, reclamações e histórico de respostas. | id | viagem_id → tu_viagem_operacional.id; motorista_id → tu_motorista.usuario_id |
| `tu_motorista` | Perfil do motorista autorizado e último ônibus informado. | usuario_id | — |
| `tu_pedido_acesso` | Solicitação de vínculo, decisão e notificações do pedido. | id | — |
| `tu_perfil` | Nome, e-mail e hash do CPF da conta. A senha é gerenciada pelo Supabase Auth. | usuario_id | — |
| `tu_posicao_atual` | Última posição compartilhada da viagem e precisão do aparelho. | viagem_id | viagem_id → tu_viagem_operacional.id |
| `tu_viagem_operacional` | Motorista, linha, ônibus, sentido e início/fim da viagem. | id | motorista_id → tu_motorista.usuario_id |

Os registros antigos foram preservados no schema privado `transurban_arquivo_20261124`, fora da Data API. Ele contém as 16 tabelas retiradas e duas cópias dos cadastros anteriores. Portanto, são 12 tabelas **ativas**, e o histórico não foi destruído. Não é uma redução para 12 objetos em toda a instalação do Supabase.

O cadastro ativo usa somente Maringá e Sarandi. O catálogo tem 66 linhas municipais de Maringá e 22 serviços/variantes metropolitanos que atendem Sarandi, com fonte registrada. Não se afirma cobertura municipal completa de Sarandi. A base CSV acadêmica continua sintética e separada.

Os históricos de atendimento ficam em `historico` no próprio registro; a fila de notificações fica em `notificacoes` no pedido. As funções PostgreSQL fazem atualizações atômicas e reservas de envio. Sem SMTP configurado, nada é marcado como enviado.

Para usar o mesmo projeto em outro computador, não recrie o banco. Clone o GitHub e configure o `.env` privado. Para um Supabase vazio: leia `database/README.md` antes de executar SQL.

A redução retirou os exercícios de estoque/pagamento e os horários/saldos fictícios da API principal. O código anterior está em `historico/`, para estudo. Essa decisão atende ao novo limite de 12 tabelas solicitado em 24/11; não equivale a cumprir um guia que exija estoque e ordens de material em funcionamento.
