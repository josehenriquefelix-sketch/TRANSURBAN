"use strict";
async function carregarEsquema(){
    const status=document.getElementById('schema-status'),button=document.getElementById('schema-refresh');button.disabled=true;status.textContent='Conferindo a estrutura…';
    try{
        let r=await fetch('/gestao/estoque/esquema');
        if(r.status===401){const refresh=await fetch('/auth/refresh',{method:'POST'});if(refresh.ok)r=await fetch('/gestao/estoque/esquema');}
        const dados=await r.json();if(!r.ok)throw new Error(dados.detail || 'Não foi possível consultar a estrutura.');
        const area=document.getElementById('schema-tables');area.replaceChildren();
        for(const tabela of dados.tabelas){
            const card=document.createElement('section');card.className='card';const title=document.createElement('h2');title.textContent=tabela.nome;
            const key=document.createElement('p');key.textContent='Chave primária: '+(tabela.chave_primaria.join(' + ') || 'não informada pela Data API');
            const lista=document.createElement('ul');for(const campo of tabela.campos){const li=document.createElement('li');li.textContent=`${campo.nome} · ${campo.tipo}${campo.pk?' · PK':''}${campo.fk?' · FK → '+campo.fk:''}`;lista.append(li);}card.append(title,key,lista);area.append(card);
        }
        status.textContent=dados.quantidade+' tabelas conferidas. '+dados.limite;
    }catch(error){status.textContent=error.message+' Entre com a conta administrativa na central de gestão.';}
    finally{button.disabled=false;}
}
document.getElementById('schema-refresh').addEventListener('click',carregarEsquema);carregarEsquema();
