"use strict";
const numero = valor => new Intl.NumberFormat('pt-BR', {maximumFractionDigits:4}).format(valor);
const charts = [];
async function obter(url) {const response=await fetch(url); const data=await response.json(); if(!response.ok) throw new Error(data.detail || 'Falha ao consultar a base.'); return data;}
function desenhar(id, tipo, titulo, dados, campo, cor) {
    if(!window.Chart) return false;
    charts.push(new Chart(document.getElementById(id), {type:tipo,data:{labels:dados.map(x=>x.data),datasets:[{label:titulo,data:dados.map(x=>x[campo]),backgroundColor:cor,borderColor:cor,borderWidth:2,tension:.2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true}}}}));
    return true;
}
async function carregar() {
    const status=document.getElementById('dashboard-status'), botao=document.getElementById('atualizar');
    botao.disabled=true; status.textContent='Consultando a base…'; status.classList.remove('error');
    try {
        const [resumo, observacoes, atraso] = await Promise.all([obter('/ia/resumo'),obter('/ia/dashboard/observacoes-por-dia'),obter('/ia/dashboard/atraso-por-dia')]);
        document.getElementById('total-observacoes').textContent=numero(resumo.observacoes_validas);
        document.getElementById('total-atraso').textContent=numero(resumo.atraso_total_min_observacoes);
        document.getElementById('total-linhas').textContent=numero(resumo.linhas_distintas_cidade_codigo);
        const tbody=document.getElementById('linhas-diarias'); tbody.replaceChildren();
        const porData=new Map(atraso.map(x=>[x.data,x.atraso_total_min]));
        for(const dia of observacoes) {const tr=document.createElement('tr');for(const valor of [dia.data,numero(dia.observacoes),numero(porData.get(dia.data) ?? 0)]) {const td=document.createElement('td');td.textContent=valor;tr.append(td);}tbody.append(tr);}
        document.getElementById('periodo-base').textContent=`Período da base: ${resumo.periodo_inicio || 'sem dados'} a ${resumo.periodo_fim || 'sem dados'}. Fonte: ${resumo.fonte}.`;
        for(const chart of charts.splice(0)) chart.destroy();
        const grafico=desenhar('grafico-observacoes','bar','Observações',observacoes,'observacoes','#176752');
        desenhar('grafico-atraso','line','Minutos',atraso,'atraso_total_min','#b78a32');
        status.textContent=grafico ? 'Indicadores, gráficos e tabela atualizados.' : 'Os números estão disponíveis. Não foi possível carregar a biblioteca dos gráficos.';
    } catch(error) {status.textContent=error.message;status.classList.add('error');}
    finally {botao.disabled=false;}
}
document.getElementById('atualizar').addEventListener('click',carregar);
carregar();
