"use strict";
// O navegador consulta o vínculo; só a API administrativa pode concedê-lo.
(() => {
    async function executar(dados, request) {
        if(!dados.sessao)await request('/auth/login', {method:'POST',body:JSON.stringify({identificador:dados.identificador,senha:dados.senha,tipo_acesso:'passageiro'})},false);
        const user=await request('/auth/me',{},false);
        if(user.papeis?.includes(dados.papel))return 'Seu acesso já está autorizado. Entre pelo formulário principal acima, com a mesma conta.';
        const pedidos=await request('/atendimento/meus-pedidos',{},false);
        const pedido=pedidos.find(p=>p.papel===dados.papel);
        if(pedido?.status==='pendente')return 'Seu pedido está pendente de análise pelo responsável. Não precisa enviar novamente. Consulte aqui depois da aprovação; o aviso por e-mail não é necessário para liberar o acesso.';
        if(pedido?.status==='recusado')return 'Seu pedido não foi aprovado. Decisão: '+(pedido.decisao||'Procure o responsável para esclarecimentos.');
        if(pedido?.status==='aprovado')return 'Existe uma aprovação anterior, mas seu vínculo não está ativo. Procure o responsável para conferir a autorização.';
        if(dados.consultar)return 'Ainda não existe pedido para esta área. Preencha seu vínculo profissional e clique em Enviar pedido de autorização.';
        const result=await request('/atendimento/pedidos-acesso',{method:'POST',body:JSON.stringify({papel:dados.papel,justificativa:dados.justificativa})},false);
        return result.mensagem+' Você pode acompanhar a decisão pelo botão Consultar minha autorização.';
    }
    window.TransurbanAutorizacao={executar};
    document.querySelectorAll('.requestAccessForm').forEach(form=>{
        let connected=false;
        const target=form.querySelector('.requestStatus');
        const submit=form.querySelector('[type=submit]');
        const consult=document.createElement('button');consult.type='button';consult.className='btn quiet wide';consult.textContent='Consultar minha autorização';submit.after(consult);
        target.setAttribute('aria-live','polite');
        async function send(consultar){
            if(submit.disabled)return;
            if(!connected && (!form.elements.identificador.reportValidity() || !form.elements.senha.reportValidity()))return;
            if(!consultar && !form.reportValidity())return;
            submit.disabled=consult.disabled=true;target.textContent='Conferindo sua conta e o vínculo…';
            try {
                target.textContent=await executar({identificador:form.elements.identificador.value,senha:form.elements.senha.value,papel:form.dataset.papel,justificativa:form.elements.justificativa.value,consultar,sessao:connected},api);
            }catch(error){target.textContent=error.message;}
            finally{form.elements.senha.value='';submit.disabled=consult.disabled=false;}
        }
        form.onsubmit=e=>{e.preventDefault();send(false);};
        consult.addEventListener('click',()=>send(true));
        api('/auth/me',{},false).then(user=>{
            if(user.papeis?.includes(form.dataset.papel))return;
            connected=true;
            const loginId=form.dataset.papel==='motorista'?'driverLoginForm':'managementLoginForm';
            const login=document.getElementById(loginId);if(login)login.hidden=true;
            const choice=document.querySelector('[data-registration-choice]');if(choice)choice.hidden=true;
            for(const name of ['identificador','senha']){
                const input=form.elements[name];input.required=false;input.disabled=true;input.hidden=true;input.value='';
                form.querySelector(`label[for="${input.id}"]`)?.setAttribute('hidden','');
            }
            target.textContent='Sua conta está conectada. Informe seu vínculo para solicitar autorização ou consulte um pedido já enviado. Não é necessário digitar a senha do Google aqui.';
            const details=form.closest('details');if(details){details.open=true;const intro=details.querySelector('p');if(intro)intro.textContent='Sua conta já está conectada. Solicite ou consulte o vínculo profissional abaixo. Somente o responsável pode aprovar o acesso.';const help=details.querySelector('p.subtle');if(help)help.textContent='Após a aprovação, atualize esta página para abrir o painel com a mesma conta.';}
            const change=document.createElement('button');change.type='button';change.className='btn quiet wide';change.textContent='Sair desta conta';
            change.addEventListener('click',async()=>{change.disabled=true;try{await api('/auth/logout',{method:'POST'},false);location.reload();}catch(error){target.textContent=error.message;change.disabled=false;}});
            form.append(change);
        }).catch(()=>{});
    });
})();
