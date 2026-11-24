-- Evolução reversível: 12 tabelas ativas. Não exclui registros antigos.
-- Execute uma única vez no SQL Editor; toda a operação é transacional.
begin;
create schema if not exists transurban_arquivo_20261124;
revoke all on schema transurban_arquivo_20261124 from public, anon, authenticated, service_role;

alter table public.tu_manifestacao add column if not exists historico jsonb not null default '[]';
alter table public.tu_chamado add column if not exists historico jsonb not null default '[]';
alter table public.tu_pedido_acesso add column if not exists notificacoes jsonb not null default '[]';

do $$ begin
 if to_regclass('public.tu_manifestacao_evento') is not null then
  update public.tu_manifestacao m set historico=(select coalesce(jsonb_agg(to_jsonb(e) order by e.criado_em,e.id),'[]') from public.tu_manifestacao_evento e where e.manifestacao_id=m.id) where historico='[]';
 end if;
 if to_regclass('public.tu_suporte_evento') is not null then
  update public.tu_chamado c set historico=(select coalesce(jsonb_agg(to_jsonb(e) order by e.criado_em,e.id),'[]') from public.tu_suporte_evento e where e.chamado_id=c.id) where historico='[]';
 end if;
 if to_regclass('public.tu_email_acesso') is not null then
  update public.tu_pedido_acesso p set notificacoes=(select coalesce(jsonb_agg(to_jsonb(e) order by e.criado_em,e.id),'[]') from public.tu_email_acesso e where e.pedido_id=p.id) where notificacoes='[]';
 end if;
end $$;

-- Cadastro real: sem criação de carteira ou saldo fictício.
create or replace function public.tu_criar_conta() returns trigger
language plpgsql security definer set search_path='' as $$
begin
 insert into public.tu_perfil(usuario_id,nome,email,cpf_hash)
 values(new.id,coalesce(new.raw_user_meta_data->>'nome',new.raw_user_meta_data->>'full_name','Passageiro'),new.email,new.raw_user_meta_data->>'cpf_hash');
 return new;
end; $$;

drop trigger if exists tu_nova_conta on auth.users;
create trigger tu_nova_conta after insert on auth.users for each row execute function public.tu_criar_conta();

create or replace function public.tu_responder_manifestacao(p_id uuid,p_autor uuid,p_status text,p_resposta text)
returns jsonb language plpgsql security definer set search_path='' as $$
declare registro public.tu_manifestacao;
begin
 select * into registro from public.tu_manifestacao where id=p_id for update;
 if not found or registro.status='encerrada' then raise exception 'Manifestação indisponível ou encerrada'; end if;
 if p_status not in ('em_analise','respondida','encerrada') then raise exception 'Status inválido'; end if;
 if p_status in ('respondida','encerrada') and length(trim(p_resposta))<10 then raise exception 'Resposta obrigatória'; end if;
 update public.tu_manifestacao set status=p_status,resposta=p_resposta,atualizada_em=now(),
 historico=historico||jsonb_build_array(jsonb_build_object('autor_id',p_autor,'status',p_status,'resposta',p_resposta,'criado_em',now()))
 where id=p_id returning * into registro;
 return to_jsonb(registro);
end; $$;
create or replace function public.tu_responder_chamado(p_chamado uuid,p_autor uuid,p_status text,p_resposta text)
returns jsonb language plpgsql security definer set search_path='' as $$
declare registro public.tu_chamado;
begin
 select * into registro from public.tu_chamado where id=p_chamado for update;
 if not found or registro.status='encerrado' then raise exception 'Chamado indisponível ou encerrado'; end if;
 if p_status not in ('em_analise','respondido','encerrado') then raise exception 'Status inválido'; end if;
 if length(trim(p_resposta))<10 then raise exception 'Resposta obrigatória'; end if;
 update public.tu_chamado set status=p_status,resposta=p_resposta,atualizado_em=now(),
 historico=historico||jsonb_build_array(jsonb_build_object('autor_id',p_autor,'status',p_status,'resposta',p_resposta,'criado_em',now()))
 where id=p_chamado returning * into registro;
 return to_jsonb(registro);
end; $$;

-- A fila passa a pertencer ao pedido. Reservas mantêm envio concorrente seguro.
create or replace function public.tu_email_do_pedido() returns trigger
language plpgsql security definer set search_path='' as $$
declare email_conta text; evento text;
begin
 if tg_op='UPDATE' and new.status=old.status then return new; end if;
 select email into email_conta from public.tu_perfil where usuario_id=new.usuario_id;
 evento:=case when new.status='pendente' then 'recebido' else new.status end;
 if email_conta is not null and not exists(select 1 from jsonb_array_elements(new.notificacoes) e where e->>'destinatario'=email_conta and e->>'evento'=evento) then
  new.notificacoes:=new.notificacoes||jsonb_build_array(jsonb_build_object('id',gen_random_uuid(),'pedido_id',new.id,'destinatario',email_conta,'evento',evento,'papel',new.papel,'estado','pendente','tentativas',0,'criado_em',now(),'proxima_tentativa',now()));
 end if;
 return new;
end; $$;
drop trigger if exists tu_email_pedido on public.tu_pedido_acesso;
create trigger tu_email_pedido before insert or update of status on public.tu_pedido_acesso for each row execute function public.tu_email_do_pedido();

create or replace function public.tu_enfileirar_revisores(p_pedido uuid,p_emails text[]) returns boolean
language plpgsql security definer set search_path='' as $$
declare pedido public.tu_pedido_acesso; email_revisor text;
begin
 select * into pedido from public.tu_pedido_acesso where id=p_pedido for update;
 if not found then raise exception 'Pedido inexistente'; end if;
 foreach email_revisor in array p_emails loop
  if not exists(select 1 from jsonb_array_elements(pedido.notificacoes) e where e->>'destinatario'=email_revisor and e->>'evento'='revisar') then
   pedido.notificacoes:=pedido.notificacoes||jsonb_build_array(jsonb_build_object('id',gen_random_uuid(),'pedido_id',pedido.id,'destinatario',email_revisor,'evento','revisar','papel',pedido.papel,'estado','pendente','tentativas',0,'criado_em',now(),'proxima_tentativa',now()));
  end if;
 end loop;
 update public.tu_pedido_acesso set notificacoes=pedido.notificacoes where id=p_pedido;
 return true;
end; $$;
create or replace function public.tu_reservar_email() returns jsonb
language plpgsql security definer set search_path='' as $$
declare pedido public.tu_pedido_acesso; item jsonb; indice integer;
begin
 select * into pedido from public.tu_pedido_acesso p where exists(
 select 1 from jsonb_array_elements(p.notificacoes) e where (e->>'estado'='pendente' and (e->>'proxima_tentativa')::timestamptz<=now()) or (e->>'estado'='processando' and (e->>'reservado_ate')::timestamptz<now()))
 order by criado_em for update skip locked limit 1;
 if not found then return null; end if;
 select e.value,e.ordinality::integer-1 into item,indice from jsonb_array_elements(pedido.notificacoes) with ordinality e
 where (e.value->>'estado'='pendente' and (e.value->>'proxima_tentativa')::timestamptz<=now()) or (e.value->>'estado'='processando' and (e.value->>'reservado_ate')::timestamptz<now()) order by e.ordinality limit 1;
 item:=item||jsonb_build_object('estado','processando','reserva',gen_random_uuid(),'reservado_ate',now()+interval '5 minutes','tentativas',coalesce((item->>'tentativas')::integer,0)+1);
 update public.tu_pedido_acesso set notificacoes=jsonb_set(notificacoes,array[indice::text],item) where id=pedido.id;
 return item;
end; $$;
create or replace function public.tu_concluir_email(p_pedido uuid,p_id uuid,p_reserva uuid,p_dados jsonb) returns boolean
language plpgsql security definer set search_path='' as $$
declare pedido public.tu_pedido_acesso; indice integer; item jsonb;
begin
 select * into pedido from public.tu_pedido_acesso where id=p_pedido for update;
 if not found then return false; end if;
 select e.value,e.ordinality::integer-1 into item,indice from jsonb_array_elements(pedido.notificacoes) with ordinality e where e.value->>'id'=p_id::text and e.value->>'reserva'=p_reserva::text;
 if not found then return false; end if;
 if p_dados->>'estado' not in ('pendente','enviado','falha') then raise exception 'Estado inválido'; end if;
 update public.tu_pedido_acesso set notificacoes=jsonb_set(notificacoes,array[indice::text],item||p_dados) where id=p_pedido;
 return true;
end; $$;
create or replace function public.tu_listar_emails() returns jsonb
language sql security definer set search_path='' as $$
 select coalesce(jsonb_agg(x.item),'[]') from (select e.value-'destinatario'-'reserva' as item from public.tu_pedido_acesso p cross join lateral jsonb_array_elements(p.notificacoes) e order by e.value->>'criado_em' desc limit 100) x;
$$;

-- Histórico fora da API. Nenhum DROP TABLE e nenhum CASCADE.
do $$ declare nome text; begin
 foreach nome in array array['faixa_exclusiva','linha_trecho','registro_atraso','trecho','tu_avaliacao','tu_carteira','tu_recarga','tu_trajeto','tu_horario','tu_manifestacao_evento','tu_suporte_evento','tu_email_acesso','tu_unidade','tu_material','tu_ordem_material','tu_item_material'] loop
  if to_regclass('public.'||nome) is not null then execute format('alter table public.%I set schema transurban_arquivo_20261124',nome); end if;
 end loop;
 if (select count(*) from information_schema.tables where table_schema='public' and table_type='BASE TABLE')<>12 then raise exception 'Conferência falhou: public precisa conter exatamente 12 tabelas. Operação cancelada.'; end if;
end $$;

revoke all on function public.tu_criar_conta(),public.tu_email_do_pedido(),public.tu_responder_manifestacao(uuid,uuid,text,text),public.tu_responder_chamado(uuid,uuid,text,text),public.tu_reservar_email(),public.tu_enfileirar_revisores(uuid,text[]),public.tu_concluir_email(uuid,uuid,uuid,jsonb),public.tu_listar_emails() from public,anon,authenticated;
grant execute on function public.tu_responder_manifestacao(uuid,uuid,text,text),public.tu_responder_chamado(uuid,uuid,text,text),public.tu_reservar_email(),public.tu_enfileirar_revisores(uuid,text[]),public.tu_concluir_email(uuid,uuid,uuid,jsonb),public.tu_listar_emails() to service_role;
notify pgrst,'reload schema';
commit;
select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE' order by table_name;
