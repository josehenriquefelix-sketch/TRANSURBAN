# Modelo editável no brModelo 3

Abra `TRANSURBAN_Cidade_Linha.brM3` no brModelo 3. A extensão nativa desta versão é `.brM3`; não renomeie para `.brM`, usado por versões antigas. O arquivo XML é uma segunda forma de abrir o mesmo modelo.

O modelo lógico representa o recorte da avaliação:

- Cidade: `id_cidade` INTEGER PK e `nome` VARCHAR(100) obrigatório e único.
- Linha de ônibus: `id_linha` INTEGER PK, `id_cidade` INTEGER FK obrigatória, `codigo` VARCHAR(20) e `nome` VARCHAR(100).
- FK: `linha_onibus.id_cidade` referencia `cidade.id_cidade`.
- Unicidade: o par `id_cidade, codigo` não pode se repetir.
- Cardinalidade: uma cidade possui zero ou várias linhas; uma linha pertence exatamente a uma cidade.

O arquivo foi gerado usando as classes do brModelo oficial, salvo no formato nativo e desserializado novamente. Foram conferidas as duas tabelas e a referência da FK após reabertura. Não é uma captura manual feita no computador do estudante.

Ferramenta: https://github.com/chcandido/brModelo
Revisão utilizada: `0cbda0225d9fbbff54469e06a99c21fee4e680d5`.

Na nuvem, o JAR está em `/workspace/.setup/brModelo/brModelo.jar`. Em um computador com Java e ambiente gráfico, inicie com `java -jar brModelo.jar` e use Arquivo → Abrir. O DER completo do projeto permanece em `docs/DER.md` na raiz do repositório.

Este desenho não executa migrações no Supabase. Para criação em banco de teste novo, use o SQL revisado em `sql/02_criar_recorte_em_banco_novo.sql`; para banco existente, comece pela auditoria de leitura.
