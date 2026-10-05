# Critérios da avaliação e evidências

| Critério | Implementação / evidência | Estado |
|---|---|---|
| Ambiente virtual e dependências | README, requirements.txt, requirements.lock.txt | Instalação testada neste ambiente; recriar venv no computador de apresentação |
| Separação de responsabilidades | backend/database.py, models.py, schemas.py, main.py | Implementado |
| Tabela simples com PK | cidade.id_cidade; POST e GET /cidades | HTTP 201/200 observados localmente |
| Segunda tabela com FK | linha_onibus.id_linha e id_cidade | Implementado e testado |
| Nome compreensível na consulta | cidade no JSON de /linhas | Verificado: Maringá |
| Registro referenciado inexistente | POST /linhas com id_cidade=999999 | 404 observado; nenhum cadastro inserido |
| PostgreSQL/Supabase | .env.example, SQL de auditoria e recorte | Pendente de configuração e teste remoto |
| CSV autoral desnormalizado | data/atrasos_analise.csv | 180 observações; idêntico ao GitHub; sintético |
| Qualidade e validação | /ia/qualidade; bloqueio de indicadores inválidos | Testado, sem apagar a fonte |
| Script antes da API | python -m backend.analise | Executado; evidencias/analise_terminal.txt |
| Três respostas JSON adaptadas | /ia/resumo, /ia/agrupamentos/linha, /ia/agrupamentos/data | HTTP 200 observado |
| Cálculo manual e agrupamento completo | GUIA_APRESENTACAO.md; teste csv/statistics | Conferido: registro 1 e grupo Maringá/031 |
| Reconciliação | tests/test_analise.py | Todas as dimensões: 180 observações e 1362 min |
| Perguntas de negócio e dashboard futuro | docs/IA_E_DASHBOARD.md e GUIA_APRESENTACAO.md | Documentado |
| Respostas e evidências | evidencias/http/respostas_http.json, servidor.log, testes_completos.txt | Execução real local |
| Capturas de /docs | evidencias/capturas quando disponíveis | Conferir presença; se ausentes, capturar no computador |
| GitHub atualizado | versionamento/PUBLICACAO.json | Estado registrado após envio |
| Encerrar e retomar | Ctrl+C, deactivate, comandos no README | Procedimento documentado |
| Atuação individual | docs/EQUIPE_E_ENTREGA.md | A equipe registra a atuação efetiva na entrega |

O frontend está previsto para a próxima semana no caderno IA. GPS, recarga de passes e login do aplicativo completo continuam como evolução do produto. Esta entrega é o backend acadêmico e não comprova integração com veículos ou operadoras.
