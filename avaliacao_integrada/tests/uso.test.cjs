const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const busca={window:{},document:{getElementById:()=>null}};
vm.createContext(busca);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/busca-linhas.js'),'utf8'),busca);
const encontrar=busca.window.TransurbanBusca.encontrar;
const linhas=[{value:'',text:'Selecione'},{value:'olimpico',text:'460 · Jd. Olímpico'},{value:'ouro',text:'461 · Jd. Ouro Cola'},{value:'a',text:'222 · Praça São Vicente / Higienópolis'}];
test('busca por bairro reconhece acentos e diferenças de maiúsculas',()=>{
    assert.equal(encontrar(linhas,'  OLIMPICO ').value,'olimpico');
    assert.equal(encontrar(linhas,'higienopolis').value,'a');
});
test('código exato escolhe a linha correta entre códigos parecidos',()=>{
    assert.equal(encontrar([...linhas,{value:'variante',text:'460A · Outra linha'}],'460').value,'olimpico');
});
test('consulta ambígua não escolhe um ônibus pela pessoa',()=>{
    assert.equal(encontrar(linhas,'Jd.'),null);
    assert.equal(encontrar([{value:'a',text:'001 · Centro'},{value:'b',text:'001 · Centro'}],'001 · Centro'),null);
});
test('consulta vazia ou inexistente não seleciona a opção inicial',()=>{
    assert.equal(encontrar(linhas,''),null);
    assert.equal(encontrar(linhas,'bairro não cadastrado'),null);
});

function conexaoHarness({area='motorista',message='Serviço indisponível',authorized=true,online=true}={}){
    function el(){return {hidden:false,disabled:false,textContent:'',attrs:{},listeners:{},children:[],setAttribute(k,v){this.attrs[k]=v;},removeAttribute(k){delete this.attrs[k];},append(...nodes){this.children.push(...nodes);},after(node){this.next=node;},addEventListener(k,fn){this.listeners[k]=fn;}};}
    const form=el(),feedback=el(),shell=el(),body=el(),events={};
    feedback.textContent=message;shell.hidden=true;
    const ids=area==='motorista'?{driverLoginForm:form,driverLoginStatus:feedback,driverShell:shell}:{managementLoginForm:form,managementStatus:feedback,managementShell:shell};
    let retries=0;
    const retry=async()=>{retries++;shell.hidden=!authorized;if(!authorized) feedback.textContent='Esta conta não possui autorização de gestão.';};
    const context={document:{body,getElementById:id=>ids[id]||null,createElement:el},navigator:{onLine:online},window:{addEventListener:(name,fn)=>events[name]=fn},MutationObserver:class{observe(){}},driverAccount:retry,openManagement:retry,fetch:()=>{throw Error('Reconexão não pode enviar um formulário.');}};
    vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/conexao.js'),'utf8'),context);
    return {form,feedback,shell,button:feedback.next,banner:body.children[0],events,retries:()=>retries};
}
test('credenciais inválidas não exibem o botão de reconexão',()=>{
    const h=conexaoHarness({message:'E-mail/CPF ou senha inválidos.'});assert.equal(h.button.hidden,true);
});
test('reconexão verifica a sessão existente e libera os controles ao terminar',async()=>{
    const h=conexaoHarness();assert.equal(h.button.hidden,false);await h.button.listeners.click();
    assert.equal(h.retries(),1);assert.equal(h.shell.hidden,false);assert.equal(h.feedback.textContent,'');assert.equal(h.button.disabled,false);assert.equal(h.form.attrs['aria-busy'],undefined);
});
test('gestão sem autorização mantém a recusa e o painel oculto',async()=>{
    const h=conexaoHarness({area:'gestao',authorized:false});await h.button.listeners.click();
    assert.equal(h.shell.hidden,true);assert.match(h.feedback.textContent,/não possui autorização/);
});
test('aviso de rede acompanha perda e retorno de conexão',()=>{
    const h=conexaoHarness({online:false});assert.equal(h.banner.hidden,false);h.events.online();assert.equal(h.banner.hidden,true);h.events.offline();assert.equal(h.banner.hidden,false);
});

test('consulta pública fica disponível enquanto a sessão ainda é verificada',async()=>{
    const source=fs.readFileSync(path.join(__dirname,'../frontend/mobilidade.js'),'utf8');
    const initSource=source.slice(source.indexOf('async function init()'),source.indexOf('init().catch'));
    const state={ready:false,user:null},navigations=[];
    let releaseSession;
    const pendingSession=new Promise(resolve=>{releaseSession=resolve;});
    const context={URLSearchParams,location:{hash:'',search:''},history:{replaceState(){}},window:{addEventListener(){},TransurbanRecovery:{entrada:()=>'/#login'}},processRecoveryLink:()=>false,recoveryArea:'passageiro',state,
        $:()=>({value:'Maringá',textContent:''}),accountUI(){},navigate:async()=>{navigations.push(state.ready);},
        api:async()=>({linhas:[]}),fillLines(){},account:()=>pendingSession,loadFavorites:async()=>{},toast(){},status(){}};
    vm.createContext(context);vm.runInContext(initSource,context);
    const initialization=context.init();
    for(let i=0;i<8;i++) await Promise.resolve();
    assert.equal(state.ready,true);
    assert.ok(navigations.includes(true),'A navegação pública precisa abrir sem esperar a sessão.');
    releaseSession();await initialization;
});
