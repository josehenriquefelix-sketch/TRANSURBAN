const chatMessages=document.getElementById("chatMessages");
const userInput=document.getElementById("userInput");
const atrasoForm=document.getElementById("atrasoForm");

function escaparHtml(texto){const div=document.createElement("div");div.textContent=String(texto??"");return div.innerHTML;}
function formatarData(valor){if(!valor)return "—";const data=new Date(valor+"T00:00:00");return Number.isNaN(data.getTime())?escaparHtml(valor):data.toLocaleDateString("pt-BR");}
function minutos(valor){return valor===null||valor===undefined?"—":valor+" min";}

async function obterJson(url,opcoes={}){
  const resposta=await fetch(url,opcoes);
  const dados=await resposta.json().catch(()=>({}));
  if(!resposta.ok)throw new Error(dados.error||dados.message||("Erro HTTP "+resposta.status));
  return dados;
}

async function verificarBackend(){
  const status=document.getElementById("apiStatus");
  try{
    const dados=await obterJson("/api/health");
    status.classList.remove("offline");
    status.innerHTML='<span class="status-dot"></span>'+escaparHtml(dados.message);
  }catch(_){
    status.classList.add("offline");
    status.innerHTML='<span class="status-dot"></span>Backend ativo / banco pendente';
  }
}

async function carregarDadosBanco(){
  const mensagem=document.getElementById("databaseMessage");
  const tabela=document.getElementById("atrasosTable");
  mensagem.textContent="Consultando Supabase...";
  try{
    const [resumo,atrasos]=await Promise.all([
      obterJson("/api/atrasos/resumo"),
      obterJson("/api/atrasos?limit=10")
    ]);
    document.getElementById("metricTotal").textContent=resumo.total_registros??0;
    document.getElementById("metricMedia").textContent=minutos(resumo.atraso_medio);
    document.getElementById("metricMaior").textContent=minutos(resumo.maior_atraso);
    document.getElementById("metricMenor").textContent=minutos(resumo.menor_atraso);

    tabela.innerHTML=atrasos.length?atrasos.map(item=>`
      <tr>
        <td>${formatarData(item.data_registro)}</td>
        <td>${escaparHtml(item.codigo_linha)} — ${escaparHtml(item.linha)}</td>
        <td>${escaparHtml(item.trecho)}</td>
        <td><strong>${escaparHtml(item.minutos_atraso)} min</strong></td>
      </tr>`).join(""):'<tr><td colspan="4">Nenhum registro encontrado.</td></tr>';
    mensagem.textContent="Dados carregados pela API Flask.";
  }catch(erro){
    mensagem.textContent=erro.message;
    tabela.innerHTML='<tr><td colspan="4">'+escaparHtml(erro.message)+'</td></tr>';
  }
}

async function registrarAtraso(event){
  event.preventDefault();
  const mensagem=document.getElementById("formMessage");
  mensagem.textContent="Enviando...";
  const corpo={
    id_linha:Number(document.getElementById("idLinha").value),
    id_trecho:Number(document.getElementById("idTrecho").value),
    data_registro:document.getElementById("dataRegistro").value,
    minutos_atraso:Number(document.getElementById("minutosAtraso").value),
    observacao:document.getElementById("observacao").value.trim()
  };
  try{
    const dados=await obterJson("/api/atrasos",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(corpo)});
    mensagem.textContent="Sucesso: registro #"+dados.registro.id_atraso+" criado.";
    await carregarDadosBanco();
  }catch(erro){mensagem.textContent=erro.message;}
}

async function sendMessage(){
  const texto=userInput.value.trim();if(!texto)return;
  adicionarMensagem(texto,"user");userInput.value="";mostrarDigitando();
  try{
    const dados=await obterJson("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:texto})});
    removerDigitando();adicionarMensagem(formatarResposta(dados.answer),"bot");
  }catch(erro){
    removerDigitando();adicionarMensagem("Não foi possível consultar a IA agora.<br><br>"+escaparHtml(erro.message),"bot");
  }
}

function sendSuggestion(texto){userInput.value=texto;sendMessage();}
function formatarResposta(texto){return escaparHtml(texto).replace(/\n/g,"<br>");}
function adicionarMensagem(texto,tipo){
  const message=document.createElement("div");message.className="message "+tipo;
  const avatar=document.createElement("div");avatar.className="avatar";avatar.innerText=tipo==="bot"?"TU":"VOCÊ";
  const bubble=document.createElement("div");bubble.className="bubble";bubble.innerHTML=texto;
  message.appendChild(avatar);message.appendChild(bubble);chatMessages.appendChild(message);chatMessages.scrollTop=chatMessages.scrollHeight;
}
function mostrarDigitando(){removerDigitando();const typing=document.createElement("div");typing.id="typing";typing.className="message bot";typing.innerHTML='<div class="avatar">TU</div><div class="bubble">Digitando...</div>';chatMessages.appendChild(typing);}
function removerDigitando(){const typing=document.getElementById("typing");if(typing)typing.remove();}

userInput.addEventListener("keydown",event=>{if(event.key==="Enter"){event.preventDefault();sendMessage();}});
atrasoForm.addEventListener("submit",registrarAtraso);
document.getElementById("dataRegistro").value=new Date().toISOString().slice(0,10);
verificarBackend();
carregarDadosBanco();