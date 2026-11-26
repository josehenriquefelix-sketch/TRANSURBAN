"use strict";
// O token fica só na memória da página, nunca em localStorage/sessionStorage.
(() => {
    const areas=['passageiro','motorista','gestor'];
    function read(url){
        const query=new URLSearchParams(url.search||'');
        const raw=String(url.hash||'').replace(/^#/,'');
        const fragment=new URLSearchParams(raw.replace(/^nova-senha[#&?]/,'').replace(/#/g,'&'));
        const area=areas.includes(query.get('area'))?query.get('area'):'passageiro';
        const active=url.pathname==='/recuperar-senha'||query.get('recuperacao')==='1'||fragment.get('type')==='recovery'||raw.startsWith('nova-senha');
        const failed=Boolean(fragment.get('error')||fragment.get('error_description')||query.get('error'));
        return {active:active||failed,area,token:active&&!failed?fragment.get('access_token')||'':'',failed,code:query.has('code')};
    }
    function entrada(area){return area==='motorista'?'/motorista/':area==='gestor'?'/gestao/':'/#login';}
    window.TransurbanRecovery={read,entrada};
})();
