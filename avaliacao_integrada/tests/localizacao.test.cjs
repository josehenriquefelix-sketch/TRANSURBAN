const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function element() {
    return {textContent:'Minha localização',value:'',checked:false,hidden:false,disabled:false,valid:true,listeners:{},attrs:{},classList:{toggle(){}},
        addEventListener(type,fn){this.listeners[type]=fn;},setAttribute(key,val){this.attrs[key]=val;},
        querySelector(){return this.button||(this.button=element());}, querySelectorAll(){return [];}, reportValidity(){return this.valid;},
        getClientRects(){return [{}];}};
}
function locationHarness() {
    const button=element(), status=element(), docEvents={}, winEvents={}, layers=[], cleared=[];
    let success, failure, opts, calls=0, visible=true;
    const map={views:[],getContainer:()=>({getClientRects:()=>visible?[{}]:[]}),setView(...args){this.views.push(args);},getBounds:()=>({contains:()=>true})};
    const L={};
    for(const method of ['circle','circleMarker']) L[method]=(coords,options)=>{
        const obj={coords,options,removed:false,addTo(){return this;},setLatLng(value){this.coords=value;return this;},setRadius(value){this.options.radius=value;return this;},bindPopup(){return this;},remove(){this.removed=true;}};
        layers.push(obj);return obj;
    };
    const context={console,Date,Number,Map,L,document:{hidden:false,getElementById:id=>id==='b'?button:status,createElement:element,addEventListener:(type,fn)=>docEvents[type]=fn},
        navigator:{geolocation:{watchPosition(ok,err,options){calls++;success=ok;failure=err;opts=options;return calls;},clearWatch:id=>cleared.push(id)}},window:{addEventListener:(type,fn)=>winEvents[type]=fn},fetch:()=>{throw Error('A localização do visitante não pode ser enviada à API.');}};
    vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/localizacao.js'),'utf8'),context);
    const control=context.window.TransurbanLocation.attach(map,{buttonId:'b',statusId:'s'});
    return {context,button,status,layers,cleared,map,control,docEvents,winEvents,get calls(){return calls;},get options(){return opts;},position(lat=-23.4,lon=-51.9,accuracy=12){success({coords:{latitude:lat,longitude:lon,accuracy},timestamp:Date.now()});},error(code){failure({code});},hideMap(){visible=false;}};
}
test('localização só começa após a ação do usuário e pede alta precisão',()=>{const h=locationHarness();assert.equal(h.calls,0);h.button.listeners.click();assert.equal(h.calls,1);assert.equal(h.options.enableHighAccuracy,true);});
test('posição e círculo exibem a precisão informada e atualizam sem criar marcadores repetidos',()=>{const h=locationHarness();h.button.listeners.click();h.position();h.position(-23.41,-51.91,35);assert.equal(h.layers.length,2);assert.deepEqual([...h.layers[0].coords],[-23.41,-51.91]);assert.equal(h.layers[1].options.radius,35);assert.match(h.status.textContent,/35 m/);});
test('parar limpa watch e marcadores; resposta atrasada não reativa a localização',()=>{const h=locationHarness();h.button.listeners.click();h.position();h.button.listeners.click();h.position();assert.equal(h.control.active,false);assert.equal(h.cleared.length,1);assert.ok(h.layers.every(l=>l.removed));assert.equal(h.layers.length,2);});
test('permissão negada não deixa o rastreamento ativo',()=>{const h=locationHarness();h.button.listeners.click();h.error(1);assert.equal(h.control.active,false);assert.match(h.status.textContent,/não autorizada/);});
test('coordenada não finita não vira ponto no mapa',()=>{const h=locationHarness();h.button.listeners.click();h.position(NaN,-51,10);assert.equal(h.layers.length,0);assert.match(h.status.textContent,/não forneceu uma posição válida/);});
test('segundo plano interrompe localização e não reinicia silenciosamente',()=>{const h=locationHarness();h.button.listeners.click();h.context.document.hidden=true;h.docEvents.visibilitychange();h.context.document.hidden=false;h.docEvents.visibilitychange();assert.equal(h.control.active,false);assert.equal(h.calls,1);});
test('sair do mapa ou da conta interrompe a localização',()=>{for(const event of ['hashchange','transurban:logout']){const h=locationHarness();h.button.listeners.click();h.hideMap();h.winEvents[event]();assert.equal(h.control.active,false);}});
test('registrar o mesmo controle não duplica os observadores',()=>{const h=locationHarness();const again=h.context.window.TransurbanLocation.attach(h.map,{buttonId:'b',statusId:'s'});assert.equal(again,h.control);h.button.listeners.click();assert.equal(h.calls,1);});

function driverHarness({valid=true,denied=false}={}) {
    const elements={}, order=[];
    const get=id=>elements[id]||(elements[id]=element());
    const context={console,Intl,Date,Number,JSON,Promise,AbortController,Event,setTimeout:()=>0,clearTimeout(){},requestAnimationFrame(){},fetch:()=>new Promise(()=>{}),confirm:()=>true,location:{reload(){}},window:{addEventListener(){},dispatchEvent(){}},document:{getElementById:get,addEventListener(){}},
        navigator:{geolocation:{getCurrentPosition(ok,err){order.push('gps');denied?err({code:1}):ok({coords:{latitude:-23.4,longitude:-51.9,accuracy:12}});}}}};
    vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/motorista.js'),'utf8'),context);
    vm.runInContext('state.driver={viagem:null}; driverPanel=async()=>{}; startGps=()=>{};',context);
    context.api=async(url,options)=>{order.push(url);const payload=JSON.parse(options.body);if(url.endsWith('/perfil')){assert.equal(payload.prefixo,'TESTE-1');assert.equal(payload.modelo,'Veículo de teste');return payload;}assert.equal(payload.linha_id,'maringa-460');assert.equal(payload.sentido,'Ida');return {id:'teste'};};
    get('locationConsent').checked=true;get('driverProfileForm').valid=valid;get('driverName').value='Teste';get('busModel').value='Veículo de teste';get('busPrefix').value='TESTE-1';get('driverLine').value='maringa-460';get('driverDirection').value='Ida';
    return {order,elements,get,submit:()=>get('tripForm').listeners.submit({preventDefault(){}})};
}
test('início valida GPS, salva ônibus e só então cria viagem da linha escolhida',async()=>{const h=driverHarness();await h.submit();assert.deepEqual(h.order,['gps','/mobilidade/motorista/perfil','/mobilidade/motorista/viagens']);assert.match(h.get('tripStatus').textContent,/Viagem iniciada/);});
test('GPS negado impede criar viagem ou salvar dados',async()=>{const h=driverHarness({denied:true});await h.submit();assert.deepEqual(h.order,['gps']);assert.match(h.get('tripStatus').textContent,/não foi iniciada/);});
test('dados incompletos do ônibus impedem pedir GPS ou iniciar viagem',async()=>{const h=driverHarness({valid:false});await h.submit();assert.deepEqual(h.order,[]);assert.match(h.get('tripStatus').textContent,/Preencha/);});
