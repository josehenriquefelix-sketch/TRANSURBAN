-- Adaptação do guia: unidade/oficina -> cliente; material -> produto;
-- ordem de fornecimento -> venda; item -> par (ordem, material).
-- Não processa pagamentos e não altera o passe do cidadão.
begin;
create table if not exists public.tu_unidade (
 id bigint generated always as identity primary key,
 nome text not null check(length(trim(nome)) between 2 and 100),
 limite numeric(12,2) not null check(limite>=0)
);
create table if not exists public.tu_material (
 id bigint generated always as identity primary key,
 nome text not null check(length(trim(nome)) between 2 and 100),
 categoria text not null check(categoria in ('pecas','limpeza','acessibilidade','seguranca','outros')),
 valor_unitario numeric(12,2) not null check(valor_unitario>0),
 estoque integer not null check(estoque>=0)
);
create table if not exists public.tu_ordem_material (
 id bigint generated always as identity primary key,
 unidade_id bigint not null references public.tu_unidade(id) on delete restrict,
 data_ordem date not null,
 prefixo text not null default '' check(length(prefixo)<=30),
 status text not null default 'ABERTA' check(status in ('ABERTA','FINALIZADA')),
 forma_pagamento text check(forma_pagamento in ('dinheiro','pix','cartao','fiado')),
 valor_total numeric(20,2),
 criada_por uuid not null references auth.users(id) on delete restrict,
 criada_em timestamptz not null default now(),
 check((status='ABERTA' and forma_pagamento is null and valor_total is null)
    or (status='FINALIZADA' and forma_pagamento is not null and valor_total is not null and valor_total>0))
);
create table if not exists public.tu_item_material (
 ordem_id bigint not null references public.tu_ordem_material(id) on delete cascade,
 material_id bigint not null references public.tu_material(id) on delete restrict,
 valor_venda numeric(12,2) not null check(valor_venda>0),
 quantidade integer not null check(quantidade>0),
 primary key(ordem_id,material_id)
);

-- Função auxiliar chamada apenas dentro das transações da API.
create or replace function public.tu_incluir_material(p_ordem bigint,p_material bigint,p_quantidade integer)
returns void language plpgsql security definer set search_path='' as $$
declare material public.tu_material;
begin
 if p_quantidade is null or p_quantidade<=0 then raise exception 'Quantidade deve ser positiva'; end if;
 select * into material from public.tu_material where id=p_material for update;
 if not found then raise exception 'Material não encontrado' using errcode='P0002'; end if;
 if p_quantidade>material.estoque then raise exception 'Estoque insuficiente'; end if;
 insert into public.tu_item_material(ordem_id,material_id,valor_venda,quantidade)
 values(p_ordem,p_material,material.valor_unitario,p_quantidade);
end; $$;

create or replace function public.tu_abrir_ordem_material(p_unidade bigint,p_data date,p_prefixo text,p_itens jsonb,p_autor uuid)
returns jsonb language plpgsql security definer set search_path='' as $$
declare ordem public.tu_ordem_material; item jsonb;
begin
 if not exists(select 1 from public.tu_unidade where id=p_unidade) then raise exception 'Unidade não encontrada' using errcode='P0002'; end if;
 if p_itens is null or jsonb_typeof(p_itens)<>'array' or jsonb_array_length(p_itens)=0 then raise exception 'Inclua pelo menos um material'; end if;
 insert into public.tu_ordem_material(unidade_id,data_ordem,prefixo,criada_por)
 values(p_unidade,p_data,p_prefixo,p_autor) returning * into ordem;
 -- Ordenar os materiais evita inversão de bloqueios em operações simultâneas.
 for item in select value from jsonb_array_elements(p_itens) order by (value->>'material_id')::bigint loop
  perform public.tu_incluir_material(ordem.id,(item->>'material_id')::bigint,(item->>'quantidade')::integer);
 end loop;
 return to_jsonb(ordem);
end; $$;

create or replace function public.tu_editar_item_material(p_ordem bigint,p_material bigint,p_quantidade integer,p_acao text)
returns jsonb language plpgsql security definer set search_path='' as $$
declare ordem public.tu_ordem_material; item public.tu_item_material; saldo integer;
begin
 select * into ordem from public.tu_ordem_material where id=p_ordem for update;
 if not found then raise exception 'Ordem não encontrada' using errcode='P0002'; end if;
 if ordem.status<>'ABERTA' then raise exception 'Uma ordem finalizada é somente para consulta'; end if;
 if p_acao='incluir' then
  perform public.tu_incluir_material(p_ordem,p_material,p_quantidade);
 else
  select * into item from public.tu_item_material where ordem_id=p_ordem and material_id=p_material;
  if not found then raise exception 'Item não encontrado' using errcode='P0002'; end if;
  if p_acao='excluir' then
   if (select count(*) from public.tu_item_material where ordem_id=p_ordem)<=1 then raise exception 'A ordem deve manter pelo menos um item'; end if;
   delete from public.tu_item_material where ordem_id=p_ordem and material_id=p_material;
   return jsonb_build_object('mensagem','Item excluído');
  elsif p_acao='atualizar' then
   if p_quantidade is null or p_quantidade<=0 then raise exception 'Quantidade deve ser positiva'; end if;
   select estoque into saldo from public.tu_material where id=p_material for update;
   if p_quantidade>saldo then raise exception 'Estoque insuficiente'; end if;
   update public.tu_item_material set quantidade=p_quantidade where ordem_id=p_ordem and material_id=p_material;
  else raise exception 'Operação inválida'; end if;
 end if;
 select * into item from public.tu_item_material where ordem_id=p_ordem and material_id=p_material;
 return to_jsonb(item);
end; $$;

create or replace function public.tu_finalizar_ordem_material(p_ordem bigint,p_pagamento text)
returns jsonb language plpgsql security definer set search_path='' as $$
declare ordem public.tu_ordem_material; item public.tu_item_material; saldo integer; credito numeric; total numeric;
begin
 select * into ordem from public.tu_ordem_material where id=p_ordem for update;
 if not found then raise exception 'Ordem não encontrada' using errcode='P0002'; end if;
 if ordem.status<>'ABERTA' then raise exception 'A ordem já foi finalizada; nenhuma segunda baixa foi feita'; end if;
 if p_pagamento is null or p_pagamento not in ('dinheiro','pix','cartao','fiado') then raise exception 'Forma de pagamento inválida'; end if;
 select limite into credito from public.tu_unidade where id=ordem.unidade_id for update;
 select sum(valor_venda*quantidade) into total from public.tu_item_material where ordem_id=p_ordem;
 if total is null or total<=0 then raise exception 'A ordem precisa de itens'; end if;
 for item in select * from public.tu_item_material where ordem_id=p_ordem order by material_id loop
  select estoque into saldo from public.tu_material where id=item.material_id for update;
  if saldo<item.quantidade then raise exception 'Estoque insuficiente para finalizar'; end if;
 end loop;
 if p_pagamento='fiado' and credito<total then raise exception 'Limite da unidade insuficiente'; end if;
 for item in select * from public.tu_item_material where ordem_id=p_ordem order by material_id loop
  update public.tu_material set estoque=estoque-item.quantidade where id=item.material_id;
 end loop;
 if p_pagamento='fiado' then update public.tu_unidade set limite=limite-total where id=ordem.unidade_id; end if;
 update public.tu_ordem_material set status='FINALIZADA',forma_pagamento=p_pagamento,valor_total=total
 where id=p_ordem returning * into ordem;
 return to_jsonb(ordem);
end; $$;

create or replace function public.tu_alterar_ordem_material(p_ordem bigint,p_unidade bigint,p_data date,p_prefixo text,p_excluir boolean)
returns jsonb language plpgsql security definer set search_path='' as $$
declare ordem public.tu_ordem_material;
begin
 select * into ordem from public.tu_ordem_material where id=p_ordem for update;
 if not found then raise exception 'Ordem não encontrada' using errcode='P0002'; end if;
 if ordem.status<>'ABERTA' then raise exception 'Ordem finalizada é somente para consulta'; end if;
 if p_excluir then
  delete from public.tu_ordem_material where id=p_ordem;
  return jsonb_build_object('mensagem','Ordem aberta excluída; estoque preservado');
 end if;
 if not exists(select 1 from public.tu_unidade where id=p_unidade) then raise exception 'Unidade não encontrada' using errcode='P0002'; end if;
 update public.tu_ordem_material set unidade_id=p_unidade,data_ordem=p_data,prefixo=p_prefixo where id=p_ordem returning * into ordem;
 return to_jsonb(ordem);
end; $$;

alter table public.tu_unidade enable row level security;
alter table public.tu_material enable row level security;
alter table public.tu_ordem_material enable row level security;
alter table public.tu_item_material enable row level security;
revoke all on public.tu_unidade,public.tu_material,public.tu_ordem_material,public.tu_item_material from anon,authenticated;
grant all on public.tu_unidade,public.tu_material,public.tu_ordem_material,public.tu_item_material to service_role;
grant usage,select on sequence public.tu_unidade_id_seq,public.tu_material_id_seq,public.tu_ordem_material_id_seq to service_role;
revoke all on function public.tu_incluir_material(bigint,bigint,integer) from public,anon,authenticated;
revoke all on function public.tu_abrir_ordem_material(bigint,date,text,jsonb,uuid) from public,anon,authenticated;
revoke all on function public.tu_editar_item_material(bigint,bigint,integer,text) from public,anon,authenticated;
revoke all on function public.tu_finalizar_ordem_material(bigint,text) from public,anon,authenticated;
revoke all on function public.tu_alterar_ordem_material(bigint,bigint,date,text,boolean) from public,anon,authenticated;
grant execute on function public.tu_abrir_ordem_material(bigint,date,text,jsonb,uuid),public.tu_editar_item_material(bigint,bigint,integer,text),public.tu_finalizar_ordem_material(bigint,text),public.tu_alterar_ordem_material(bigint,bigint,date,text,boolean) to service_role;
create index if not exists tu_itens_por_material on public.tu_item_material(material_id);
create index if not exists tu_ordens_por_unidade on public.tu_ordem_material(unidade_id);
notify pgrst,'reload schema';
commit;
