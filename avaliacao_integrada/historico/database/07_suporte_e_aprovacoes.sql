-- Suporte privado, alertas operacionais confirmados e aprovação de vínculos.
begin;
create table if not exists public.tu_chamado (
 id uuid primary key default gen_random_uuid(),
 numero bigint generated always as identity unique,
 usuario_id uuid not null references auth.users(id) on delete restrict,
 perfil text not null check(perfil in ('passageiro','motorista')),
 cidade text not null check(cidade in ('Maringá','Sarandi')),
 linha_id text,
 competencia text not null check(competencia in ('maringa','sarandi','metropolitano')),
 categoria text not null,
 assunto text not null check(length(assunto) between 5 and 120),
 mensagem text not null check(length(mensagem) between 10 and 2000),
 latitude double precision check(latitude between -90 and 90),
 longitude double precision check(longitude between -180 and 180),
 status text not null default 'recebido' check(status in ('recebido','em_analise','respondido','encerrado')),
 resposta text not null default '',
 criado_em timestamptz not null default now(),
 atualizado_em timestamptz not null default now(),
 check((latitude is null)=(longitude is null))
);
create table if not exists public.tu_alerta_operacional (
 id uuid primary key default gen_random_uuid(),
 autor_id uuid not null references auth.users(id) on delete restrict,
 cidade text not null check(cidade in ('Maringá','Sarandi')),
 competencia text not null check(competencia in ('maringa','sarandi','metropolitano')),
 linha_id text,
 nivel text not null check(nivel in ('vermelho','amarelo','verde')),
 titulo text not null check(length(titulo) between 5 and 120),
 orientacao text not null check(length(orientacao) between 10 and 1000),
 latitude double precision not null check(latitude between -90 and 90),
 longitude double precision not null check(longitude between -180 and 180),
 ativo boolean not null default true,
 criado_em timestamptz not null default now(),
 expira_em timestamptz not null,
 check(expira_em>criado_em)
);
create table if not exists public.tu_pedido_acesso (
 id uuid primary key default gen_random_uuid(),
 usuario_id uuid not null references auth.users(id) on delete cascade,
 papel text not null check(papel in ('motorista','gestor')),
 justificativa text not null check(length(justificativa) between 10 and 1000),
 status text not null default 'pendente' check(status in ('pendente','aprovado','recusado')),
 decisao text not null default '',
 escopo text check(escopo in ('maringa','sarandi','metropolitano','todos')),
 revisor_id uuid references auth.users(id),
 criado_em timestamptz not null default now(),
 decidido_em timestamptz,
 unique(usuario_id,papel)
);
create table if not exists public.tu_suporte_evento (
 id bigint generated always as identity primary key,
 chamado_id uuid not null references public.tu_chamado(id) on delete restrict,
 autor_id uuid not null references auth.users(id) on delete restrict,
 status text not null,
 resposta text not null,
 criado_em timestamptz not null default now()
);
create or replace function public.tu_decidir_acesso(p_pedido uuid,p_revisor uuid,p_aprovar boolean,p_escopo text,p_decisao text)
returns jsonb language plpgsql security definer set search_path='' as $$
declare registro public.tu_pedido_acesso;
begin
 select * into registro from public.tu_pedido_acesso where id=p_pedido for update;
 if not found or registro.status<>'pendente' then raise exception 'Solicitação indisponível'; end if;
 if p_escopo not in ('maringa','sarandi','metropolitano','todos') then raise exception 'Escopo inválido'; end if;
 if length(trim(p_decisao))<10 then raise exception 'Informe a justificativa da decisão'; end if;
 if registro.usuario_id=p_revisor then raise exception 'Não é permitido aprovar o próprio vínculo'; end if;
 if p_aprovar then
  insert into public.tu_acesso(usuario_id,papel,escopo,ativo) values(registro.usuario_id,registro.papel,p_escopo,true)
  on conflict(usuario_id,papel) do update set escopo=excluded.escopo,ativo=true;
 end if;
 update public.tu_pedido_acesso set status=case when p_aprovar then 'aprovado' else 'recusado' end,
 escopo=p_escopo,decisao=p_decisao,revisor_id=p_revisor,decidido_em=now() where id=p_pedido returning * into registro;
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
 update public.tu_chamado set status=p_status,resposta=p_resposta,atualizado_em=now() where id=p_chamado returning * into registro;
 insert into public.tu_suporte_evento(chamado_id,autor_id,status,resposta) values(p_chamado,p_autor,p_status,p_resposta);
 return to_jsonb(registro);
end; $$;
alter table public.tu_chamado enable row level security;
alter table public.tu_alerta_operacional enable row level security;
alter table public.tu_pedido_acesso enable row level security;
alter table public.tu_suporte_evento enable row level security;
revoke all on public.tu_chamado,public.tu_alerta_operacional,public.tu_pedido_acesso,public.tu_suporte_evento from anon,authenticated;
grant all on public.tu_chamado,public.tu_alerta_operacional,public.tu_pedido_acesso,public.tu_suporte_evento to service_role;
grant usage,select on sequence public.tu_chamado_numero_seq,public.tu_suporte_evento_id_seq to service_role;
revoke all on function public.tu_decidir_acesso(uuid,uuid,boolean,text,text) from public,anon,authenticated;
revoke all on function public.tu_responder_chamado(uuid,uuid,text,text) from public,anon,authenticated;
grant execute on function public.tu_decidir_acesso(uuid,uuid,boolean,text,text) to service_role;
grant execute on function public.tu_responder_chamado(uuid,uuid,text,text) to service_role;
-- Mantém o e-mail de busca por CPF sincronizado com alterações no Auth.
create or replace function public.tu_sincronizar_email() returns trigger language plpgsql security definer set search_path='' as $$
begin
 update public.tu_perfil set email=new.email where usuario_id=new.id;
 return new;
end; $$;
drop trigger if exists tu_email_atualizado on auth.users;
create trigger tu_email_atualizado after update of email on auth.users for each row execute function public.tu_sincronizar_email();
revoke all on function public.tu_sincronizar_email() from public,anon,authenticated;
create index if not exists tu_chamado_escopo on public.tu_chamado(competencia,criado_em desc);
create index if not exists tu_alerta_vigencia on public.tu_alerta_operacional(ativo,expira_em);
notify pgrst,'reload schema';
commit;
