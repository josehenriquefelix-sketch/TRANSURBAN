-- Teste transacional: não envia e-mails e desfaz todas as alterações ao final.
-- Execute apenas com o SMTP parado. Não é uma migração de instalação.
begin;
do $$
declare conta uuid; pedido uuid; item jsonb; total integer;
begin
 select id into conta from auth.users where email is not null order by created_at limit 1;
 if conta is null then raise exception 'É necessária uma conta existente para validar FKs'; end if;
 insert into public.tu_pedido_acesso(usuario_id,papel,justificativa)
 values(conta,'motorista','TESTE TRANSACIONAL DESCARTÁVEL: nenhuma autorização concedida')
 on conflict(usuario_id,papel) do update set notificacoes=excluded.notificacoes
 returning id into pedido;
 -- No caminho ON CONFLICT, o UUID original é preservado.
 update public.tu_pedido_acesso set notificacoes=(select jsonb_agg(e||jsonb_build_object('pedido_id',pedido)) from jsonb_array_elements(notificacoes) e) where id=pedido;
 select jsonb_array_length(notificacoes) into total from public.tu_pedido_acesso where id=pedido;
 if total<>1 then raise exception 'Notificação do pedido não foi criada'; end if;
 perform public.tu_enfileirar_revisores(pedido,array['teste-descartavel@example.com']);
 perform public.tu_enfileirar_revisores(pedido,array['teste-descartavel@example.com']);
 select jsonb_array_length(notificacoes) into total from public.tu_pedido_acesso where id=pedido;
 if total<>2 then raise exception 'Enfileiramento duplicado'; end if;
 item:=public.tu_reservar_email();
 if item is null or item->>'estado'<>'processando' or item->>'reserva' is null then raise exception 'Reserva não criada'; end if;
 if public.tu_concluir_email((item->>'pedido_id')::uuid,(item->>'id')::uuid,gen_random_uuid(),'{"estado":"enviado"}') then raise exception 'Aceitou reserva inválida'; end if;
 if not public.tu_concluir_email((item->>'pedido_id')::uuid,(item->>'id')::uuid,(item->>'reserva')::uuid,'{"estado":"pendente","reserva":null,"reservado_ate":null}') then raise exception 'Conclusão recusada'; end if;
end $$;
rollback;
select 'OK: pedido, deduplicação, reserva e conclusão conferidos; alterações desfeitas; nenhum e-mail enviado' as resultado;
