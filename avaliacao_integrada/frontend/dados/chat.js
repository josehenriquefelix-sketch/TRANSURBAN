"use strict";
const form=document.getElementById('chat-form'), seletor=document.getElementById('chat-pergunta'), botao=document.getElementById('chat-enviar'), statusChat=document.getElementById('chat-status');
const labels={total_observacoes:'Observações',linhas_distintas:'Linhas distintas',atraso_total_min:'Minutos de atraso',data:'Data',observacoes:'Observações',cidade:'Cidade',atraso_medio_min:'Média em minutos',atraso_mediano_min:'Mediana em minutos',maior_atraso_min:'Maior atraso em minutos'};
function linha(item) {return Object.entries(item).map(([key,value])=>`${labels[key] || key}: ${typeof value==='number' ? new Intl.NumberFormat('pt-BR',{maximumFractionDigits:4}).format(value) : value}`).join(' · ');}
async function perguntas() {
    try {const response=await fetch('/chat/perguntas');if(!response.ok)throw new Error(); const dados=await response.json();seletor.replaceChildren(new Option('Selecione uma pergunta',''));for(const p of dados)seletor.add(new Option(p,p));seletor.disabled=botao.disabled=!dados.length;statusChat.textContent=dados.length?'':'Nenhuma pergunta cadastrada.';}
    catch {statusChat.textContent='Não foi possível carregar as perguntas. Confira o servidor e recarregue a página.';}
}
form.addEventListener('submit',async event=>{
    event.preventDefault();if(botao.disabled || !seletor.value)return;
    const pergunta=seletor.value;botao.disabled=true;seletor.disabled=true;statusChat.textContent='Calculando e consultando a explicação…';document.getElementById('chat-resposta').hidden=true;
    const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),40000);
    try {
        const response=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pergunta}),signal:controller.signal});
        const dados=await response.json();if(!response.ok)throw new Error(dados.detail || 'Não foi possível consultar os dados.');
        document.getElementById('chat-enunciado').textContent=pergunta;
        const lista=document.getElementById('chat-dados');lista.replaceChildren();
        const registros=dados.resultado===null ? [] : Array.isArray(dados.resultado) ? dados.resultado : [dados.resultado];
        for(const registro of registros) {const li=document.createElement('li');li.textContent=linha(registro);lista.append(li);}
        if(!registros.length){const li=document.createElement('li');li.textContent='Nenhum resultado disponível para esta consulta.';lista.append(li);}
        document.getElementById('chat-explicacao').textContent=dados.explicacao || 'Explicação por IA indisponível.';
        const aviso=document.getElementById('chat-aviso');aviso.textContent=dados.aviso || '';aviso.hidden=!dados.aviso;
        document.getElementById('chat-resposta').hidden=false;statusChat.textContent='Consulta concluída. O resultado calculado está abaixo.';
    } catch(error) {statusChat.textContent=error.name==='AbortError'?'A consulta demorou. Tente novamente.':error.message;}
    finally {clearTimeout(timeout);botao.disabled=false;seletor.disabled=false;}
});
perguntas();
