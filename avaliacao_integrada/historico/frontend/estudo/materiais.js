"use strict";
const el=id=>document.getElementById(id), base='/gestao/estoque';
let units=[],materials=[],orders=[],items=[],current=null,busy=false;
let renewal=null;
const moeda=value=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(Number(value));
async function api(path,options={},retry=true) {const response=await fetch(path,{...options,headers:{'Content-Type':'application/json',...options.headers},credentials:'same-origin'});if(response.status===401 && retry && !path.startsWith('/auth/')){if(!renewal)renewal=api('/auth/refresh',{method:'POST'},false).then(()=>true).catch(()=>false).finally(()=>{renewal=null;});if(await renewal)return api(path,options,false);}if(response.status===204)return null;const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Confira os campos informados.');return data;}
async function acao(work) {if(busy)return;busy=true;el('stock-status').textContent='Aguarde…';try{await work();el('stock-status').textContent='Operação concluída.';}catch(error){el('stock-status').textContent=error.message;}finally{busy=false;}}
function opcoes(id,rows,placeholder,label=x=>x.nome) {const select=el(id),old=select.value;select.replaceChildren(new Option(placeholder,''));for(const row of rows)select.add(new Option(label(row),row.id));select.value=rows.some(x=>String(x.id)===old)?old:'';}
async function catalogos() {
    [units,materials,orders]=await Promise.all([api(base+'/unidades'),api(base+'/materiais'),api(base+'/ordens')]);
    opcoes('unit-edit',units,'Nova unidade');opcoes('order-unit',units,'Selecione a unidade',x=>`${x.nome} · limite ${moeda(x.limite)}`);
    opcoes('material-edit',materials,'Novo material');opcoes('item-material',materials,'Selecione o material',x=>`${x.nome} · ${moeda(x.valor_unitario)} · estoque ${x.estoque}`);
    opcoes('order-select',orders,'Nova ordem',x=>`#${x.id} · ${x.unidade?.nome || 'Unidade '+x.unidade_id} · ${x.status}`);
}
function desenharItens() {
    const tbody=el('order-items');tbody.replaceChildren();
    for(const item of items) {
        const tr=document.createElement('tr'),nome=item.material?.nome || materials.find(x=>x.id===item.material_id)?.nome || item.material_id;
        for(const text of [nome,moeda(item.valor_venda),String(item.quantidade),moeda(Number(item.valor_venda)*item.quantidade)]) {const td=document.createElement('td');td.textContent=text;tr.append(td);}
        const actions=document.createElement('td');
        if(!current || current.status==='ABERTA') {
            const quantidade=document.createElement('input');quantidade.type='number';quantidade.min='1';quantidade.step='1';quantidade.value=item.quantidade;quantidade.setAttribute('aria-label','Nova quantidade de '+nome);
            const salvar=document.createElement('button');salvar.type='button';salvar.textContent='Alterar quantidade';salvar.onclick=()=>acao(async()=>{
                const valor=Number(quantidade.value);if(!Number.isInteger(valor)||valor<1)throw new Error('Use quantidade inteira e positiva.');
                if(current)await api(`${base}/ordens/${current.id}/itens/${item.material_id}`,{method:'PUT',body:JSON.stringify({quantidade:valor})});else item.quantidade=valor;
                await atualizarOrdem();
            });
            const excluir=document.createElement('button');excluir.type='button';excluir.textContent='Remover';excluir.onclick=()=>acao(async()=>{
                if(current)await api(`${base}/ordens/${current.id}/itens/${item.material_id}`,{method:'DELETE'});else items=items.filter(x=>x!==item);
                await atualizarOrdem();
            });actions.append(quantidade,salvar,excluir);
        }
        tr.append(actions);tbody.append(tr);
    }
    const total=items.reduce((s,x)=>s+Number(x.valor_venda)*x.quantidade,0);
    el('order-total').textContent=current?.status==='FINALIZADA' ? 'Total gravado: '+moeda(current.valor_total) : 'Prévia: '+moeda(total)+' · total final calculado pelo banco';
    const finalizada=current?.status==='FINALIZADA';
    for(const id of ['order-unit','order-date','order-bus','order-save','item-material','item-quantity','item-add','payment'])el(id).disabled=!!finalizada;
    el('order-finish').disabled=!current || finalizada;el('order-delete').disabled=!current || finalizada;
    el('order-state').textContent=current?`Ordem #${current.id} · ${current.status}`:'Nova ordem: adicione pelo menos um material.';
}
async function atualizarOrdem() {if(current){current=await api(`${base}/ordens/${current.id}`);items=await api(`${base}/ordens/${current.id}/itens`);}desenharItens();}
function novaOrdem() {current=null;items=[];el('order-form').reset();el('order-select').value='';const hoje=new Date();el('order-date').value=[hoje.getFullYear(),String(hoje.getMonth()+1).padStart(2,'0'),String(hoje.getDate()).padStart(2,'0')].join('-');desenharItens();}
el('unit-edit').onchange=()=>{const u=units.find(x=>String(x.id)===el('unit-edit').value);el('unit-name').value=u?.nome || '';el('unit-limit').value=u?.limite ?? '';};
el('unit-form').onsubmit=e=>{e.preventDefault();acao(async()=>{const id=el('unit-edit').value;await api(base+'/unidades'+(id?'/'+id:''),{method:id?'PUT':'POST',body:JSON.stringify({nome:el('unit-name').value,limite:el('unit-limit').value})});el('unit-form').reset();await catalogos();});};
el('unit-delete').onclick=()=>acao(async()=>{const id=el('unit-edit').value;if(!id)throw new Error('Selecione a unidade.');if(!confirm('Excluir esta unidade? Unidades vinculadas a ordens serão preservadas.'))return;await api(base+'/unidades/'+id,{method:'DELETE'});el('unit-form').reset();await catalogos();});
el('material-edit').onchange=()=>{const m=materials.find(x=>String(x.id)===el('material-edit').value);el('material-name').value=m?.nome || '';el('material-price').value=m?.valor_unitario ?? '';el('material-stock').value=m?.estoque ?? '';el('material-category').value=m?.categoria || 'pecas';};
el('material-form').onsubmit=e=>{e.preventDefault();acao(async()=>{const id=el('material-edit').value;await api(base+'/materiais'+(id?'/'+id:''),{method:id?'PUT':'POST',body:JSON.stringify({nome:el('material-name').value,categoria:el('material-category').value,valor_unitario:el('material-price').value,estoque:Number(el('material-stock').value)})});el('material-form').reset();await catalogos();});};
el('material-delete').onclick=()=>acao(async()=>{const id=el('material-edit').value;if(!id)throw new Error('Selecione o material.');if(!confirm('Excluir o material? Materiais vinculados a itens serão preservados.'))return;await api(base+'/materiais/'+id,{method:'DELETE'});el('material-form').reset();await catalogos();});
el('order-new').onclick=novaOrdem;
el('order-select').onchange=()=>acao(async()=>{const id=el('order-select').value;if(!id){novaOrdem();return;}current=await api(base+'/ordens/'+id);el('order-unit').value=current.unidade_id;el('order-date').value=current.data_ordem;el('order-bus').value=current.prefixo;await atualizarOrdem();});
el('item-form').onsubmit=e=>{e.preventDefault();acao(async()=>{
    const material=materials.find(x=>String(x.id)===el('item-material').value),quantidade=Number(el('item-quantity').value);
    if(!material || !Number.isInteger(quantidade)||quantidade<1)throw new Error('Selecione material e quantidade válida.');
    if(quantidade>material.estoque)throw new Error('Estoque insuficiente.');
    if(items.some(x=>x.material_id===material.id))throw new Error('Material já incluído. Altere a quantidade do item.');
    if(current)await api(`${base}/ordens/${current.id}/itens`,{method:'POST',body:JSON.stringify({material_id:material.id,quantidade})});
    else items.push({material_id:material.id,quantidade,valor_venda:material.valor_unitario});
    await atualizarOrdem();el('item-form').reset();
});};
el('order-form').onsubmit=e=>{e.preventDefault();acao(async()=>{
    const dados={unidade_id:Number(el('order-unit').value),data_ordem:el('order-date').value,prefixo:el('order-bus').value};
    if(!current && !items.length)throw new Error('Inclua pelo menos um item antes de salvar.');
    if(!current)dados.itens=items.map(x=>({material_id:x.material_id,quantidade:x.quantidade}));
    current=await api(base+'/ordens'+(current?'/'+current.id:''),{method:current?'PUT':'POST',body:JSON.stringify(dados)});await catalogos();el('order-select').value=current.id;await atualizarOrdem();
});};
el('order-delete').onclick=()=>acao(async()=>{if(!current)throw new Error('Selecione uma ordem.');if(!confirm('Excluir a ordem aberta e seus itens? O estoque não será alterado.'))return;await api(base+'/ordens/'+current.id,{method:'DELETE'});await catalogos();novaOrdem();});
el('finish-form').onsubmit=e=>{e.preventDefault();acao(async()=>{if(!current)throw new Error('Salve a ordem antes de finalizar.');current=await api(`${base}/ordens/${current.id}/finalizar`,{method:'POST',body:JSON.stringify({forma_pagamento:el('payment').value})});await catalogos();el('order-select').value=current.id;await atualizarOrdem();});};
el('mail-refresh').onclick=()=>acao(async()=>{const data=await api('/atendimento/gestao/notificacoes');el('mail-status').textContent=data.smtp_configurado?'SMTP configurado. Consulte os estados abaixo.':'SMTP ainda não configurado. As notificações ficam pendentes; não foram enviadas.';el('mail-list').replaceChildren();for(const row of data.notificacoes){const li=document.createElement('li');li.textContent=`${row.evento} · ${row.estado} · tentativas: ${row.tentativas}`;el('mail-list').append(li);}});
(async()=>{try{const user=await api('/auth/me');if(!user.administrador)throw new Error('Este módulo exige a conta administrativa da equipe.');await catalogos();el('stock-content').hidden=false;el('stock-status').textContent='Escolha um cadastro ou prepare uma nova ordem.';novaOrdem();}catch(error){el('stock-status').textContent=error.message;el('stock-login').hidden=false;}})();
