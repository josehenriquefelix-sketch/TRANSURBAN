# Códigos para testar o backend seguindo o roteiro

`testar_backend_roteiro.py` executa requisições HTTP reais à API já aberta. Não inicia ou encerra o servidor e não acessa o frontend. O script usa somente a biblioteca padrão do Python.

## Terminal 1: iniciar a API

Na pasta que contém `main.py`, após a preparação:

Linux:
```bash
python3 iniciar_apresentacao.py
```

Windows:
```powershell
py -3.12 iniciar_apresentacao.py
```

Aguarde Application startup complete e mantenha esse terminal aberto. O inicializador usa banco SQLite local e preserva `.env`.

## Terminal 2: testes separados

Abra outro terminal na mesma pasta. Se baixou o script separadamente, coloque-o nessa pasta.

Linux:
```bash
python3 testar_backend_roteiro.py --ds
python3 testar_backend_roteiro.py --ia
```

Windows:
```powershell
py -3.12 testar_backend_roteiro.py --ds
py -3.12 testar_backend_roteiro.py --ia
```

Execute um de cada vez. Para ambos em sequência, use `--tudo`. Se iniciou a API com `--port 8002`, acrescente `--porta 8002` aos comandos do script.

Opcional: salve a execução em arquivo novo com `--salvar evidencia-ds-nova.json` ou `--salvar evidencia-ia-nova.json`. Não sobrescreve arquivo existente.

## DS

O teste exige que `/health` informe `sqlite_local`, para não gravar demonstrações em Supabase. Cria uma cidade Sarandi e uma linha de demonstração, usa o ID realmente devolvido, consulta os registros e confere o nome da cidade na linha. Em seguida, escolhe um ID de cidade comprovadamente ausente, espera 404 e confere que a tentativa não foi salva. Envia nome somente com espaços, espera 422 e confere a lista de cidades.

O teste cria registros de exemplo no banco local e não apaga dados. Repetir pode criar outra cidade com o mesmo nome: o modelo SQLite atual não tem restrição UNIQUE nesse campo. O código da linha ganha um sufixo para identificar a execução. Os cadastros criados permanecem para serem mostrados no Swagger.

Persistência é um teste manual separado: anote o id_linha impresso, encerre a API com Ctrl+C, inicie novamente com a mesma configuração e consulte GET /linhas no Swagger. O script não afirma que reiniciou o servidor.

## IA

Consulta fonte, qualidade, resumo e agrupamentos por linha e serviço com `limite=5`. Confere integridade, contagens e cálculos do snapshot: 71.086 registros, 309 códigos, média 230,0518 e mediana 162. Verifica que atraso médio e viagens realizadas estão indisponíveis (`null`). Confere os totais completos separadamente dos grupos exibidos.

A fonte é programação pública comunitária histórica de Curitiba, não medições de atraso de Maringá/Sarandi. A etapa IA somente lê os dados. Um `OK` do script corresponde à resposta recebida naquela execução; se houver `FALHA`, não anuncie sucesso.

## Para o público ver

O script ajuda a conferir o roteiro. No telão, vocês podem continuar usando `http://127.0.0.1:8000/docs`, executando as mesmas operações em Try it out → Execute e explicando os resultados reais. 404 e 422 são esperados nos dois testes de erro, não falhas inesperadas.
