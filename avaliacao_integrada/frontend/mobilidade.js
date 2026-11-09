"use strict";
const el = id => document.getElementById(id);
const api = location.port === "5500" ? "http://127.0.0.1:8092" : location.origin;
const codigo = id => el(id).value.trim().toUpperCase();
const query = linha => "?linha=" + encodeURIComponent(linha);
const msg = (id, texto) => { el(id).textContent = texto; };
async function req(path, {method="GET", body, token}={}) {
  const headers = {};
  if (body) headers["Content-Type"]="application/json";
  if (token) headers.Authorization="Bearer "+token;
  const r=await fetch(api+"/mobilidade"+path,{method,headers,body:body?JSON.stringify(body):undefined,cache:"no-store",signal:AbortSignal.timeout(10000)});
  if(r.status===204)return null;
  const d=await r.json();
  if(!r.ok)throw Error(typeof d.detail==="string"?d.detail:"Confira o código da linha, do ônibus e os dados informados.");
  return d;
}
const inicial = (new URLSearchParams(location.search).get("linha") || "001").trim().toUpperCase();
let linha=/^[A-Z0-9-]{1,20}$/.test(inicial) ? inicial : "001", map, markers, rota, primeira=true, watch=null, sessao=null, fila=Promise.resolve(), atualizando=false;
el("linhaMapa").value=linha;
el("linhaAval").value=linha;
if(window.L){
  map=L.map("mapa").setView([-23.425,-51.906],12);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
  markers=L.layerGroup().addTo(map);
}
function listar(id,itens){
  el(id).replaceChildren(...itens.map(t=>{const l=document.createElement("li");l.textContent=t;return l;}));
}
async function posicoes(){
  if(atualizando||el("passageiroArea").hidden)return;
  atualizando=true;
  const atual=linha;
  try{
    const itens=await req("/onibus"+query(atual));
    if(atual!==linha)return;
    markers?.clearLayers();
    listar("veiculos",itens.map(x=>x.veiculo+" · "+x.latitude.toFixed(5)+", "+x.longitude.toFixed(5)+" · precisão informada "+Math.round(x.precisao)+" m"));
    for(const x of itens){
      const titulo=document.createElement("span");titulo.textContent=x.veiculo+" · linha "+x.linha;
      if(map)L.circleMarker([x.latitude,x.longitude],{radius:9}).addTo(markers).bindTooltip(titulo);
    }
    if(map&&primeira&&itens.length&&!rota){map.setView([itens[0].latitude,itens[0].longitude],15);primeira=false;}
    msg("mapaStatus",(itens.length?itens.length+" ônibus com GPS recente.":"Nenhum ônibus transmitindo GPS recente nesta linha.")+(!map?" Mapa indisponível; consulte a lista de posições.":""));
  }catch(e){if(atual===linha){markers?.clearLayers();listar("veiculos",[]);msg("mapaStatus","Não foi possível atualizar o GPS. "+e.message);}}
  finally{atualizando=false;}
}
async function carregarTrajeto(atual){
  if(rota){rota.remove();rota=null;}
  msg("trajetoStatus","Buscando trajeto cadastrado…");
  try{
    const d=await req("/trajeto"+query(atual));
    if(atual!==linha)return;
    if(d.pontos.length>1&&map){rota=L.polyline(d.pontos,{color:"#1263a0",weight:5}).addTo(map);map.fitBounds(rota.getBounds(),{padding:[22,22],maxZoom:16});}
    msg("trajetoStatus",d.pontos.length>1?"Trajeto cadastrado da linha "+atual+".":"Ainda não há trajeto cadastrado para esta linha.");
  }catch(e){if(atual===linha)msg("trajetoStatus",e.message);}
}
async function carregarAval(atual){
  try{
    const a=await req("/avaliacoes"+query(atual));
    if(atual===linha)listar("avaliacoes",a.length?a.map(x=>x.veiculo+" · "+x.nota+"/5 · "+x.lotacao+" — "+x.descricao):["Nenhuma avaliação nesta linha."]);
  }catch(e){if(atual===linha)listar("avaliacoes",[e.message]);}
}
el("buscar").addEventListener("submit",e=>{
  e.preventDefault();linha=codigo("linhaMapa");el("linhaAval").value=linha;primeira=true;
  markers?.clearLayers();listar("veiculos",[]);listar("avaliacoes",[]);
  void posicoes();void carregarTrajeto(linha);void carregarAval(linha);
});
el("avaliar").addEventListener("submit",async e=>{
  e.preventDefault();const b=e.submitter;b.disabled=true;
  try{
    await req("/avaliacoes",{method:"POST",body:{linha:codigo("linhaAval"),veiculo:codigo("veiculoAval"),nota:Number(el("nota").value),lotacao:el("lotacao").value,descricao:el("descricao").value}});
    msg("avalStatus","Avaliação registrada.");el("descricao").value="";void carregarAval(linha);
  }catch(e){msg("avalStatus",e.message);}finally{b.disabled=false;}
});
for(const perfil of ["motorista","passageiro"])el(perfil).addEventListener("click",()=>{
  for(const p of ["motorista","passageiro"]){el(p+"Area").hidden=p!==perfil;el(p).setAttribute("aria-pressed",String(p===perfil));}
  if(perfil==="passageiro"){map?.invalidateSize();void posicoes();}
});
el("transmitir").addEventListener("submit",e=>{
  e.preventDefault();
  if(sessao)return;
  if(!window.isSecureContext||!navigator.geolocation){msg("gpsStatus","Abra o painel por HTTPS ou localhost para usar o GPS.");return;}
  const dados={veiculo:codigo("veiculoMotorista"),linha:codigo("linhaMotorista"),token:el("token").value};
  if(!/^[A-Z0-9-]{1,20}$/.test(dados.veiculo)||!/^[A-Z0-9-]{1,20}$/.test(dados.linha)){msg("gpsStatus","Use letras, números ou hífen nos códigos.");return;}
  sessao=dados;el("iniciar").disabled=true;el("parar").disabled=false;let ultimo=0,pendente=false;
  msg("gpsStatus","Aguardando autorização e sinal do GPS…");
  watch=navigator.geolocation.watchPosition(p=>{
    if(sessao!==dados||pendente||Date.now()-ultimo<4000)return;
    ultimo=Date.now();pendente=true;
    fila=req("/gps",{method:"PUT",token:dados.token,body:{veiculo:dados.veiculo,linha:dados.linha,latitude:p.coords.latitude,longitude:p.coords.longitude,precisao:p.coords.accuracy,gps_em:p.timestamp/1000}})
      .then(()=>{if(sessao===dados)msg("gpsStatus","Posição enviada às "+new Date().toLocaleTimeString("pt-BR"));})
      .catch(err=>{if(sessao===dados)msg("gpsStatus",err.message);})
      .finally(()=>{pendente=false;});
  },err=>{if(sessao===dados)msg("gpsStatus","GPS indisponível: "+err.message);},{enableHighAccuracy:true,maximumAge:0,timeout:15000});
});
el("parar").addEventListener("click",async ()=>{
  const atual=sessao;if(!atual)return;
  sessao=null;navigator.geolocation.clearWatch(watch);el("parar").disabled=true;
  try{await fila;await req("/gps/"+encodeURIComponent(atual.veiculo),{method:"DELETE",token:atual.token});msg("gpsStatus","Transmissão encerrada.");}
  catch{msg("gpsStatus","Transmissão local parada. Se o servidor estiver indisponível, a última posição expira em até 35 segundos.");}
  finally{el("token").value="";el("iniciar").disabled=false;}
});
void posicoes();void carregarTrajeto(linha);void carregarAval(linha);
setInterval(posicoes,5000);
