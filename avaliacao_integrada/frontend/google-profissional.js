"use strict";
// Mesmo OAuth do passageiro; o papel solicitado não concede autorização.
(() => {
    const messages={google_sessao_invalida:'A confirmação do Google expirou ou foi interrompida. Tente entrar com Google novamente.',google_indisponivel:'Não foi possível concluir o acesso Google. Tente novamente ou entre com e-mail/CPF e senha.'};
    const error=new URLSearchParams(location.search).get('erro');
    for(const button of document.querySelectorAll('[data-google-role]')){
        const status=document.getElementById(button.dataset.googleStatus);
        if(error && messages[error])status.textContent=messages[error];
        button.addEventListener('click',async()=>{
            button.disabled=true;status.textContent='Abrindo acesso seguro com Google…';
            try{
                const config=await api('/auth/configuracao',{},false);
                if(!config.google)throw Error('Google indisponível no momento. Entre com e-mail ou CPF e senha.');
                location.assign('/auth/google?tipo_acesso='+encodeURIComponent(button.dataset.googleRole));
            }catch(e){status.textContent=e.message;button.disabled=false;}
        });
    }
})();
