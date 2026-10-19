# Validação do pacote para outro notebook

Executada na nuvem Linux em 19/10/2026, Python 3.12, usando ambiente virtual novo criado por iniciar_apresentacao.py --preparar. Não é comprovação de execução no notebook de destino nem no Supabase.

- iniciar_apresentacao.py --testar: 22 aprovados, nenhuma falha, um aviso de depreciação de httpx/Starlette.
- iniciar_apresentacao.py --evidencias: 16 requisições HTTP reais aprovadas; banco temporário descartável.
- Inicializador real, /health, /docs, CSV e POST/GET testados. Cadastros permaneceram após parar e reiniciar a API no mesmo arquivo SQLite. Banco de ensaio removido após teste, não incluído no pacote.
- DATABASE_URL e CSV_PATH incorretos herdados foram substituídos somente no processo filho, confirmando o modo de apresentação local. .env preservado.
- Caminho Windows documentado, mas não executado neste ambiente Linux.

O hash do ZIP para transporte é disponibilizado fora do ZIP. Os testes devem ser repetidos no notebook de destino antes do auditório.
