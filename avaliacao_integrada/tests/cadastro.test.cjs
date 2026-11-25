const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../frontend/cadastro.js'),'utf8');
function harness({authenticated=false,requestError=false}={}){
    const element=()=>({hidden:false,value:'',textContent:'',disabled:false,listeners:{},addEventListener(n,f){this.listeners[n]=f;},focus(){},setAttribute(){},removeAttribute(){}});
    const submit=element(),feedback=element(),next=element(),back=element(),choice=element(),opener=element(),identifier=element();
    const fields=Object.fromEntries(Object.entries({nome:'Pessoa fictícia',cpf:'52998224725',email:'teste@example.invalid',senha:'Teste123!',confirmacao:'Teste123!',justificativa:'Cadastro de teste simulado.'}).map(([k,v])=>[k,{...element(),value:v}]));
    const login={...element(),querySelector:()=>element()};
    const request={...element(),querySelector:()=>identifier};
    const form={...element(),elements:fields,dataset:{papel:'motorista',loginId:'login'},reset(){for(const f of Object.values(fields))f.value='';},querySelector:s=>({'[role=status]':feedback,'[type=submit]':submit,'[data-request-next]':next,'[data-back-login]':back,'input':fields.nome})[s]};
    const calls=[];
    const context={window:{},document:{querySelectorAll:s=>s==='.professionalSignupForm'?[form]:[],getElementById:()=>login,querySelector:s=>({'[data-registration-choice]':choice,'.professional-request':request,'[data-open-signup]':opener})[s]},api:async(route,opts,retry)=>{calls.push({route,body:JSON.parse(opts.body),retry});if(route==='/auth/cadastro')return {autenticado:authenticated,mensagem:'Conta recebida.'};if(requestError)throw Error('Falha de conexão.');return {mensagem:'Vínculo pendente de análise.'};}};
    vm.createContext(context);vm.runInContext(source,context);
    return {context,calls,fields,form,submit,feedback,next,send:()=>form.listeners.submit({preventDefault(){}})};
}
test('CPF exige os dois dígitos verificadores e rejeita repetições',()=>{
    const {validarCpf}=harness().context.window.TransurbanCadastro;
    assert.equal(validarCpf('529.982.247-25'),true);
    for(const cpf of ['11111111111','52998224724','123','abcdefghijk'])assert.equal(validarCpf(cpf),false);
});
test('senha exige comprimento e todas as classes de caracteres',()=>{
    const {validarSenha}=harness().context.window.TransurbanCadastro;
    assert.equal(validarSenha('Teste123!'),true);
    for(const pass of ['Teste12','teste123!','TESTE123!','Testeabc!','Teste1234','A1!a'.repeat(20)])assert.equal(validarSenha(pass),false);
});
test('cadastro pendente de confirmação envia só identidade e não concede papel',async()=>{
    const h=harness();await h.send();
    assert.equal(h.calls.length,1);assert.equal(h.calls[0].route,'/auth/cadastro');
    assert.deepEqual(Object.keys(h.calls[0].body).sort(),['cpf','email','nome','senha']);
    assert.equal(h.calls[0].retry,false);assert.equal(h.next.hidden,false);
    assert.match(h.feedback.textContent,/confirmar seu e-mail/);assert.equal(h.fields.senha.value,'');
});
test('sessão confirmada cria pedido de vínculo, sem aprovação automática',async()=>{
    const h=harness({authenticated:true});await h.send();
    assert.equal(h.calls.length,2);assert.equal(h.calls[1].route,'/atendimento/pedidos-acesso');
    assert.equal(h.calls[1].body.papel,'motorista');assert.equal(h.calls[1].body.justificativa,'Cadastro de teste simulado.');
    assert.match(h.feedback.textContent,/pendente/);
});
test('falha do pedido após cadastro impede cadastro duplicado',async()=>{
    const h=harness({authenticated:true,requestError:true});await h.send();await h.send();
    assert.equal(h.calls.length,2);assert.equal(h.submit.disabled,true);assert.equal(h.next.hidden,false);
    assert.match(h.feedback.textContent,/não é necessário repetir/);
});
test('CPF inválido e confirmação diferente não são enviados',async()=>{
    const h=harness();h.fields.cpf.value='00000000000';await h.send();assert.equal(h.calls.length,0);
    h.fields.cpf.value='52998224725';h.fields.confirmacao.value='Outra123!';await h.send();assert.equal(h.calls.length,0);
});
