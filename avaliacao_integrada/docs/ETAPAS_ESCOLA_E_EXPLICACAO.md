# Evolução do TRANSURBAN para as atividades de DS e IA

## Ordem de estudo

1. **Cadastros e PK:** `cidade` e seus campos, modelos Pydantic e rotas GET, POST, PUT e DELETE.
2. **Relacionamento e FK:** `linha_onibus.id_cidade` aponta para `cidade.id_cidade`. A interface mostra um nome e a API grava o código.
3. **CSV e totalizações:** cada linha da base autoral é uma observação de atraso em um trecho. Não contar observações como viagens ou passageiros.
4. **Consultas por dia:** contar observações e somar seus minutos de atraso, usando `analise_dashboard.py`.
5. **Dashboard:** HTML organiza, o CSS compartilhado apresenta e JavaScript busca os mesmos JSONs que alimentam os gráficos Chart.js e a tabela acessível.
6. **Chave composta e conclusão da operação:** cada item é identificado pelo par ordem/material. O fechamento confere disponibilidade, calcula o total e altera tudo junto.
7. **Chat:** uma pergunta cadastrada escolhe uma função Python. O resultado é calculado antes de chamar o Ollama. Sem chave ou sem nuvem, o JSON ainda contém `resultado` e um `aviso`.

## Adaptação do exemplo da Mercearia

| Exemplo do guia | TRANSURBAN | Regra preservada |
|---|---|---|
| Cliente | Unidade/oficina | Nome para escolher; código para vincular; limite disponível |
| Produto | Material da manutenção | Preço, categoria e estoque |
| Venda | Ordem de fornecimento | Unidade, data, itens e estado |
| Item de venda | Item da ordem | PK composta por ordem e material; duas FKs |
| Venda fiada | Fornecimento a prazo | Desconta o total do limite da unidade |

O registro de dinheiro, Pix ou cartão é apenas uma informação do exercício. Não é cobrança real e não integra a bilhetagem. O módulo não modifica carteira ou passe dos passageiros.

O guia mais recente apresenta PostgreSQL com SQLAlchemy. Este projeto preserva a conexão Supabase por HTTPS das etapas anteriores; as operações que precisam de transação foram levadas a funções PostgreSQL chamadas pela API. É uma adaptação da persistência: não há SQLAlchemy em execução. O banco continua responsável pela chave composta, bloqueios e rollback. A orientação de preservar a conexão existente foi mantida, sem adicionar uma segunda senha de banco nem misturar duas implementações de gravação.

## Entenda o fechamento

1. Bloquear a ordem e verificar se está aberta.
2. Bloquear a unidade e os materiais em ordem de código.
3. Calcular o total pelos preços copiados nos itens.
4. Conferir estoque e, para pagamento a prazo, limite.
5. Gravar estoque, limite, total, pagamento e estado na mesma transação.

Se houver erro, a transação é desfeita. A API devolve 409. A ordem finalizada fica apenas para consulta e não pode ser finalizada outra vez.

## O que cada arquivo faz

- `backend/main.py`: inicialização, roteadores, CORS e arquivos da interface.
- `backend/database.py`: cliente Supabase, com segredo apenas no backend.
- `backend/controller/materiais.py`: validação HTTP e chamadas ao banco.
- `database/09_materiais_e_ordens.sql`: tabelas, chave composta e transações.
- `backend/analise.py`: leitura e validação do CSV e totalizações originais.
- `backend/analise_dashboard.py`: séries por dia.
- `backend/chat_dados.py`: perguntas permitidas e funções que as respondem.
- `backend/ollama_cloud.py`: envia somente pergunta cadastrada e agregados.
- `backend/controller/chat.py`: GET de perguntas e POST de consulta.
- `frontend/dados/`: dashboard, tabela e chat em HTML e JavaScript.
- `frontend/mobilidade.css`: estilos compartilhados, com os novos estilos limitados à sua área.
- `backend/notificacoes.py`: entrega a fila de notificações por SMTP quando configurado.
- `database/08_notificacoes_acesso.sql`: fila privada criada junto aos eventos de aprovação.

## Esboço proposto para revisão da equipe

Dashboard: título e identificação da fonte → três indicadores → dois gráficos → tabela diária → botão do chat.

Chat: escolher pergunta → consultar → resultado numérico → explicação, quando disponível → aviso de indisponibilidade.

Materiais: cadastrar unidade → cadastrar material → escolher unidade pelo nome → incluir itens → salvar ordem → selecionar pagamento → finalizar → conferir estoque e limite.

O esboço é uma proposta implementada. A equipe precisa revisar junta, combinar responsáveis e explicar os cálculos. Não há registro de que todos já fizeram essa validação coletiva.

## Conferência do material consultado

Foram lidos os enunciados e guias acessíveis na turma **CEEP2026 – Projeto – Líderes**, inclusive as etapas de 15/11, os materiais de frontend, o guia de itens/finalização e o de Ollama Cloud. A turma **CEEP Projeto 2026: DS-IA-Meca** também foi solicitada; o controle do Chrome foi interrompido antes de confirmar a leitura de todos os seus anexos. Não se afirma que as duas turmas sejam idênticas.

Há divergência de anexos na turma lida: DS–Frontend de 15/11 descreve uma venda, mas anexa guias de chat; o dashboard de 08/11 anexa materiais de compras. A implementação separa os requisitos de cada enunciado e reaproveita os guias correspondentes, em vez de trocar o significado das telas.

Referências: [guia de itens e finalização](https://docs.google.com/document/d/11TR0Ciyahppvi0tBwqLroWgCOBi3FKscmsxZFraxrqU/edit), [guia de chat com Ollama](https://docs.google.com/document/d/1hjuMvi7iV3cgogNI1s23MJ8GQefDKCcD2798HsTizDE/edit). Os documentos completos do professor não foram copiados ao repositório.
