-- OPCIONAL, após auditoria aprovada e em banco autorizado para escrita.
-- Acrescenta somente as cidades ainda ausentes; não altera IDs nem registros.
-- Não inventa linhas, trajetos, horários ou dados de GPS.
BEGIN;
LOCK TABLE public.cidade IN SHARE ROW EXCLUSIVE MODE;

INSERT INTO public.cidade(nome)
SELECT 'Maringá'
WHERE NOT EXISTS (
    SELECT 1 FROM public.cidade WHERE lower(btrim(nome)) = lower('Maringá')
);

INSERT INTO public.cidade(nome)
SELECT 'Sarandi'
WHERE NOT EXISTS (
    SELECT 1 FROM public.cidade WHERE lower(btrim(nome)) = lower('Sarandi')
);

COMMIT;

SELECT id_cidade, nome FROM public.cidade ORDER BY id_cidade;
