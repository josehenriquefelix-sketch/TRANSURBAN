-- Fila privada: o pedido e sua notificação são gravados na mesma transação.
begin;
create table if not exists public.tu_email_acesso (
 id uuid primary key default gen_random_uuid(),
 pedido_id uuid not null references public.tu_pedido_acesso(id) on delete cascade,
 destinatario text not null,
 evento text not null check(evento in ('recebido','aprovado','recusado','revisar')),
 papel text not null check(papel in ('motorista','gestor')),
 estado text not null default 'pendente' check(estado in ('pendente','processando','enviado','falha')),
 tentativas integer not null default 0,
 criado_em timestamptz not null default now(),
 enviado_em timestamptz,
 proxima_tentativa timestamptz not null default now(),
 reservado_ate timestamptz,
 reserva uuid,
 erro text,
 unique(pedido_id,destinatario,evento)
);
alter table public.tu_email_acesso enable row level security;
revoke all on public.tu_email_acesso from anon,authenticated;
grant all on public.tu_email_acesso to service_role;

create or replace function public.tu_email_do_pedido() returns trigger
language plpgsql security definer set search_path='' as $$
declare email_conta text;
begin
 if tg_op='UPDATE' and new.status=old.status then return new; end if;
 select email into email_conta from public.tu_perfil where usuario_id=new.usuario_id;
 if email_conta is not null then
  insert into public.tu_email_acesso(pedido_id,destinatario,evento,papel)
  values(new.id,email_conta,case when new.status='pendente' then 'recebido' else new.status end,new.papel)
  on conflict(pedido_id,destinatario,evento) do nothing;
 end if;
 return new;
end; $$;
drop trigger if exists tu_email_pedido on public.tu_pedido_acesso;
create trigger tu_email_pedido after insert or update of status on public.tu_pedido_acesso
for each row execute function public.tu_email_do_pedido();
revoke all on function public.tu_email_do_pedido() from public,anon,authenticated;

create or replace function public.tu_reservar_email() returns jsonb
language plpgsql security definer set search_path='' as $$
declare email_fila public.tu_email_acesso;
begin
 select * into email_fila from public.tu_email_acesso
 where (estado='pendente' and proxima_tentativa<=now())
    or (estado='processando' and reservado_ate<now())
 order by criado_em for update skip locked limit 1;
 if not found then return null; end if;
 update public.tu_email_acesso set estado='processando',reserva=gen_random_uuid(),
 reservado_ate=now()+interval '5 minutes',tentativas=tentativas+1
 where id=email_fila.id returning * into email_fila;
 return to_jsonb(email_fila);
end; $$;
revoke all on function public.tu_reservar_email() from public,anon,authenticated;
grant execute on function public.tu_reservar_email() to service_role;
create index if not exists tu_email_pendentes on public.tu_email_acesso(estado,proxima_tentativa);
notify pgrst,'reload schema';
commit;
