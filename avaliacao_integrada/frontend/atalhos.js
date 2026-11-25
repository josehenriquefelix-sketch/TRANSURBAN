"use strict";
// Usa apenas links da navegação deste painel; nunca cria permissões ou atalhos administrativos.
(() => {
    const header = document.querySelector('.workspace>header');
    const sidebar = document.querySelector('#sidebar nav');
    if (!header || !sidebar || !HTMLDialogElement.prototype.showModal) return;
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'command-trigger';
    trigger.setAttribute('aria-label', 'Buscar uma função neste painel');
    trigger.setAttribute('aria-haspopup', 'dialog');
    trigger.append('Buscar no painel');
    const key = document.createElement('kbd'); key.textContent = 'Ctrl K'; trigger.append(key);
    const account = header.querySelector('.header-account');
    if (account) account.before(trigger); else header.append(trigger);
    const dialog = document.createElement('dialog');
    dialog.className = 'command-dialog';
    dialog.setAttribute('aria-labelledby','commandTitle');
    dialog.innerHTML = '<div class="command-head"><div><h2 id="commandTitle">O que você precisa fazer?</h2><button type="button" class="command-close" aria-label="Fechar busca">Fechar</button></div><input type="search" aria-label="Buscar função" placeholder="Ex.: horários, mapa, avaliações" autocomplete="off"></div><nav class="command-results" aria-label="Resultados da busca"></nav><p class="command-note">Navegue com Tab. Pressione Esc para fechar.</p>';
    document.body.append(dialog);
    const input = dialog.querySelector('input'), results = dialog.querySelector('nav');
    const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    function render() {
        const query = normalize(input.value.trim());
        const links = [...sidebar.querySelectorAll('a')].filter(link => !link.closest('[hidden]') && normalize(link.textContent).includes(query));
        results.replaceChildren(...links.map(link => {
            const result = document.createElement('a'); result.href = link.getAttribute('href');
            result.textContent = link.textContent.trim();
            const hint = document.createElement('small'); hint.textContent = 'Abrir página'; result.append(hint);
            result.addEventListener('click',() => dialog.close());
            return result;
        }));
        if (!links.length) {const p=document.createElement('p');p.className='command-empty';p.textContent='Nenhuma função encontrada. Tente outra palavra.';results.append(p);}
    }
    function open() {
        if (!header.getClientRects().length || dialog.open) return;
        input.value=''; render(); dialog.showModal(); input.focus();
    }
    trigger.addEventListener('click',open);
    input.addEventListener('input',render);
    dialog.querySelector('button').addEventListener('click',() => dialog.close());
    dialog.addEventListener('keydown',event => {if(event.key==='Escape'){event.preventDefault();dialog.close();}});
    dialog.addEventListener('click',event => {if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
    dialog.addEventListener('close',() => {if(header.getClientRects().length)trigger.focus();});
    document.addEventListener('keydown',event => {if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();open();}});
})();
