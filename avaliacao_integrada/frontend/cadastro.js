"use strict";
// Cadastro de identidade não concede papel profissional; a API mantém a autorização.
(() => {
    function validarCpf(value) {
        const cpf=String(value||'').replace(/[.\-\s]/g,'');
        if (!/^\d{11}$/.test(cpf) || /^(\d)\1{10}$/.test(cpf)) return false;
        for (const size of [9,10]) {
            let sum=0;
            for(let i=0;i<size;i++) sum+=Number(cpf[i])*(size+1-i);
            const digit=(sum*10)%11;
            if(Number(cpf[size])!==(digit===10?0:digit)) return false;
        }
        return true;
    }
    const validarSenha=value => value.length>=8 && value.length<=72 && /\p{Lu}/u.test(value) && /\p{Ll}/u.test(value) && /\d/.test(value) && /[^\p{L}\p{N}\s]/u.test(value);
    window.TransurbanCadastro={validarCpf,validarSenha};
    document.querySelectorAll('[data-cpf],#signupCpf').forEach(input => {
        const validate=()=>input.setCustomValidity(input.value && !validarCpf(input.value)?'Informe um CPF válido, com os 11 dígitos.':'');
        input.addEventListener('input',validate);input.addEventListener('blur',validate);
    });
    document.querySelectorAll('.professionalSignupForm').forEach(form => {
        const login=document.getElementById(form.dataset.loginId);
        const choice=document.querySelector('[data-registration-choice]');
        const request=document.querySelector('.professional-request');
        const feedback=form.querySelector('[role=status]');
        const submit=form.querySelector('[type=submit]');
        const next=form.querySelector('[data-request-next]');
        const show=visible=>{
            form.hidden=!visible;login.hidden=visible;
            if(choice)choice.hidden=visible;if(request)request.hidden=visible;
            if(visible){const title=form.querySelector('h2');if(title){title.tabIndex=-1;title.focus();}else form.querySelector('input').focus();}
            else {form.elements.senha.value='';form.elements.confirmacao.value='';login.querySelector('input').focus();}
        };
        document.querySelector('[data-open-signup]')?.addEventListener('click',()=>show(true));
        form.querySelector('[data-back-login]').addEventListener('click',()=>show(false));
        next.addEventListener('click',()=>{show(false);if(request){request.open=true;request.querySelector('input').focus();}});
        form.addEventListener('submit',async event=>{
            event.preventDefault();
            if(submit.disabled) return;
            feedback.textContent='';
            if(!validarCpf(form.elements.cpf.value)){feedback.textContent='Informe um CPF válido.';return;}
            if(!validarSenha(form.elements.senha.value)){feedback.textContent='Use no mínimo 8 caracteres, com maiúscula, minúscula, número e símbolo.';return;}
            if(form.elements.senha.value!==form.elements.confirmacao.value){feedback.textContent='As senhas precisam ser iguais.';return;}
            submit.disabled=true;form.setAttribute('aria-busy','true');
            const email=form.elements.email.value.trim();
            let received=false;
            try {
                const result=await api('/auth/cadastro',{method:'POST',body:JSON.stringify({
                    nome:form.elements.nome.value.trim(),cpf:form.elements.cpf.value,
                    email,senha:form.elements.senha.value
                })},false);
                received=true;
                const reason=form.elements.justificativa.value.trim();
                form.reset();
                const identifier=request?.querySelector('[name=identificador]');
                if(identifier)identifier.value=email;
                next.hidden=false;
                feedback.textContent=result.mensagem+' O acesso profissional só será liberado após a aprovação do responsável.';
                if(result.autenticado){
                    try {
                        const pedido=await api('/atendimento/pedidos-acesso',{method:'POST',body:JSON.stringify({papel:form.dataset.papel,justificativa:reason})},false);
                        feedback.textContent='Conta recebida. '+pedido.mensagem;
                    } catch(error) {
                        feedback.textContent='Conta recebida, mas o pedido de vínculo não foi enviado. '+error.message+' Use Continuar para solicitar autorização; não é necessário repetir o cadastro.';
                    }
                } else feedback.textContent+=' Após confirmar seu e-mail, use Continuar para solicitar autorização.';
                submit.textContent='Cadastro recebido';
            } catch(error){feedback.textContent=error.message;}
            finally {if(!received)submit.disabled=false;form.removeAttribute('aria-busy');}
        });
    });
})();
