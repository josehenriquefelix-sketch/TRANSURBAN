# Chaves do TRANSURBAN

Estas chaves foram conferidas nos arquivos SQL das entregas Módulo 6 e Sprint 7. **Não foram confirmadas na instância atual do Supabase**, cujo painel não pôde ser aberto nesta sessão. O script `sql/01_auditar_supabase.sql` mostra o estado real do banco, inclusive outras tabelas.

| Tabela acadêmica | Chave primária (PK) | Chaves estrangeiras (FK) e destino |
|---|---|---|
| cidade | id_cidade | Nenhuma |
| linha_onibus | id_linha | id_cidade → cidade.id_cidade |
| trecho | id_trecho | id_cidade_origem → cidade.id_cidade; id_cidade_destino → cidade.id_cidade |
| linha_trecho | (id_linha, id_trecho), juntas | id_linha → linha_onibus.id_linha; id_trecho → trecho.id_trecho |
| faixa_exclusiva | id_faixa | id_trecho → trecho.id_trecho |
| registro_atraso | id_atraso | id_linha → linha_onibus.id_linha; id_trecho → trecho.id_trecho |

As seis tabelas têm PK. Cinco têm FK; cidade é a única sem FK neste modelo. Há oito restrições FK. `linha_trecho` tem uma PK composta por duas colunas: cada coluna também é FK. Um mesmo id_linha pode aparecer várias vezes com trechos diferentes, mas o par não pode repetir. PK não aceita nulo nem duplicação da chave completa. A FK exige que o registro apontado exista quando o campo está preenchido; neste modelo as FKs são obrigatórias por NOT NULL.

`relationship()` facilita navegar nos objetos Python; não substitui a FK no banco. Nome parecido ou prefixo `id_` também não comprova que uma coluna é chave. `UNIQUE(id_cidade,codigo)` é uma regra de unicidade da linha, não sua PK. RLS controla acesso às linhas; PK/FK controlam identidade e integridade.

**PK/FK não são chaves de API.** Chaves publishable/anon/secret/service_role são credenciais de acesso ao serviço. Não as cole no trabalho como exemplo de chave primária. O backend usa conexão PostgreSQL e senha do banco via `.env`.

## Divergências nos arquivos anteriores

- Módulo 6: IDs `INTEGER PRIMARY KEY`, sem DEFAULT; o backend antigo aceitava IDs manuais. Sprint 7: IDs `SERIAL`. Este backend espera geração pelo banco e rejeita IDs enviados no cadastro.
- Módulo 6: faixa_exclusiva tinha `tipo` e `status`. Sprint 7: `nome` e `km`. As chaves são as mesmas, mas as colunas não são idênticas. Este trabalho não escreve nessa tabela nem tenta reconciliar automaticamente esses esquemas.
- O app mobile V3 possui um esquema de evolução próprio. Sua existência no ZIP não comprova que tenha sido aplicado ao Supabase. Não misture esse DDL com o acadêmico sem uma migração planejada.

## Como apresentar ao professor

“No nosso projeto, a cidade é a entidade independente. A linha de ônibus tem sua própria PK e uma FK para cidade. Ao cadastrar a linha, verificamos se a cidade existe. O banco guarda o ID, e a consulta usa o relacionamento para exibir o nome da cidade. O campo FK não é substituído pelo nome: o nome é acrescentado à resposta JSON.”

Desafio de compreensão: registro_atraso depende de linha_onibus e trecho. Sua PK é id_atraso; suas FKs são id_linha e id_trecho. Uma resposta útil mostraria código/nome da linha e nome do trecho, além dos minutos. A existência isolada das duas FKs não garante que o trecho pertença à linha; essa regra exige validar a associação linha_trecho (como fazia o backend Sprint 7).

Referências consultadas em 05/10/2026:
- https://supabase.com/docs/guides/database/tables
- https://supabase.com/docs/guides/database/joins-and-nesting
- https://docs.sqlalchemy.org/en/20/orm/session_basics.html
