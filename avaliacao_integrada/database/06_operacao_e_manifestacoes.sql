-- TRANSURBAN: acesso autorizado, favoritos, viagens, posições e atendimento.
begin;
create table if not exists public.tu_acesso (
 usuario_id uuid not null references auth.users(id) on delete cascade,
 papel text not null check(papel in ('motorista','gestor')),
 escopo text not null default 'metropolitano' check(escopo in ('maringa','sarandi','metropolitano','todos')),
 ativo boolean not null default true,
 primary key(usuario_id,papel)
);
create table if not exists public.tu_motorista (
 usuario_id uuid primary key references auth.users(id) on delete cascade,
 nome_publico text not null check(length(nome_publico) between 2 and 100),
 ano_nascimento integer check(ano_nascimento between 1920 and 2100),
 bio text not null default '' check(length(bio)<=240),
 exibir_perfil boolean not null default false,
 modelo text not null check(length(modelo) between 2 and 100),
 prefixo text not null check(length(prefixo) between 1 and 30),
 atualizado_em timestamptz not null default now()
);
create table if not exists public.tu_favorito (
 usuario_id uuid not null references auth.users(id) on delete cascade,
 linha_id text not null,
 criado_em timestamptz not null default now(),
 primary key(usuario_id,linha_id)
);
create table if not exists public.tu_viagem_operacional (
 id uuid primary key default gen_random_uuid(),
 motorista_id uuid not null references public.tu_motorista(usuario_id) on delete restrict,
 linha_id text not null,
 sentido text not null,
 prefixo text not null,
 modelo text not null,
 status text not null default 'ativa' check(status in ('ativa','encerrada')),
 iniciada_em timestamptz not null default now(),
 encerrada_em timestamptz,
 check((status='ativa' and encerrada_em is null) or (status='encerrada' and encerrada_em is not null))
);
create unique index if not exists tu_motorista_uma_viagem on public.tu_viagem_operacional(motorista_id) where status='ativa';
create unique index if not exists tu_prefixo_uma_viagem on public.tu_viagem_operacional(prefixo) where status='ativa';
create table if not exists public.tu_posicao_atual (
 viagem_id uuid primary key references public.tu_viagem_operacional(id) on delete cascade,
 latitude double precision not null check(latitude between -90 and 90),
 longitude double precision not null check(longitude between -180 and 180),
 precisao_m double precision not null check(precisao_m between 0 and 1000),
 direcao double precision check(direcao between 0 and 360),
 registrada_em timestamptz not null default now()
);
create table if not exists public.tu_manifestacao (
 id uuid primary key default gen_random_uuid(),
 numero bigint generated always as identity unique,
 usuario_id uuid not null references auth.users(id) on delete restrict,
 viagem_id uuid references public.tu_viagem_operacional(id) on delete restrict,
 motorista_id uuid references public.tu_motorista(usuario_id) on delete restrict,
 linha_id text not null,
 cidade text not null,
 competencia text not null check(competencia in ('maringa','sarandi','metropolitano')),
 tipo text not null check(tipo in ('elogio','reclamacao','sugestao')),
 categoria text not null,
 nota_onibus integer check(nota_onibus between 1 and 5),
 nota_motorista integer check(nota_motorista between 1 and 5),
 relato text not null check(length(relato) between 10 and 2000),
 status text not null default 'recebida' check(status in ('recebida','em_analise','respondida','encerrada')),
 resposta text not null default '',
 criada_em timestamptz not null default now(),
 atualizada_em timestamptz not null default now()
);
create table if not exists public.tu_manifestacao_evento (
 id bigint generated always as identity primary key,
 manifestacao_id uuid not null references public.tu_manifestacao(id) on delete restrict,
 autor_id uuid not null references auth.users(id) on delete restrict,
 status text not null,
 resposta text not null,
 criado_em timestamptz not null default now()
);
create index if not exists tu_manifestacao_competencia on public.tu_manifestacao(competencia,criada_em desc);
create index if not exists tu_manifestacao_motorista on public.tu_manifestacao(motorista_id);
create or replace function public.tu_registrar_posicao(p_viagem uuid,p_motorista uuid,p_lat double precision,p_lon double precision,p_precisao double precision,p_direcao double precision)
returns boolean language plpgsql security definer set search_path='' as $$
begin
 perform 1 from public.tu_viagem_operacional where id=p_viagem and motorista_id=p_motorista and status='ativa' for update;
 if not found then raise exception 'Viagem não ativa'; end if;
 insert into public.tu_posicao_atual(viagem_id,latitude,longitude,precisao_m,direcao)
 values(p_viagem,p_lat,p_lon,p_precisao,p_direcao)
 on conflict(viagem_id) do update set latitude=excluded.latitude,longitude=excluded.longitude,precisao_m=excluded.precisao_m,direcao=excluded.direcao,registrada_em=now();
 return true;
end; $$;
create or replace function public.tu_responder_manifestacao(p_id uuid,p_autor uuid,p_status text,p_resposta text)
returns jsonb language plpgsql security definer set search_path='' as $$
declare registro public.tu_manifestacao;
begin
 select * into registro from public.tu_manifestacao where id=p_id for update;
 if not found then raise exception 'Manifestação inexistente'; end if;
 if p_status not in ('em_analise','respondida','encerrada') then raise exception 'Status inválido'; end if;
 if registro.status='encerrada' then raise exception 'Atendimento encerrado'; end if;
 if p_status in ('respondida','encerrada') and length(trim(p_resposta))<10 then raise exception 'Resposta obrigatória'; end if;
 update public.tu_manifestacao set status=p_status,resposta=p_resposta,atualizada_em=now() where id=p_id returning * into registro;
 insert into public.tu_manifestacao_evento(manifestacao_id,autor_id,status,resposta) values(p_id,p_autor,p_status,p_resposta);
 return to_jsonb(registro);
end; $$;
revoke all on function public.tu_registrar_posicao(uuid,uuid,double precision,double precision,double precision,double precision) from public,anon,authenticated;
revoke all on function public.tu_responder_manifestacao(uuid,uuid,text,text) from public,anon,authenticated;
grant execute on function public.tu_registrar_posicao(uuid,uuid,double precision,double precision,double precision,double precision) to service_role;
grant execute on function public.tu_responder_manifestacao(uuid,uuid,text,text) to service_role;
alter table public.tu_acesso enable row level security;
alter table public.tu_motorista enable row level security;
alter table public.tu_favorito enable row level security;
alter table public.tu_viagem_operacional enable row level security;
alter table public.tu_posicao_atual enable row level security;
alter table public.tu_manifestacao enable row level security;
alter table public.tu_manifestacao_evento enable row level security;
revoke all on public.tu_acesso,public.tu_motorista,public.tu_favorito,public.tu_viagem_operacional,public.tu_posicao_atual,public.tu_manifestacao,public.tu_manifestacao_evento from anon,authenticated;
grant all on public.tu_acesso,public.tu_motorista,public.tu_favorito,public.tu_viagem_operacional,public.tu_posicao_atual,public.tu_manifestacao,public.tu_manifestacao_evento to service_role;
grant usage,select on sequence public.tu_manifestacao_numero_seq,public.tu_manifestacao_evento_id_seq to service_role;
notify pgrst,'reload schema';
commit;
