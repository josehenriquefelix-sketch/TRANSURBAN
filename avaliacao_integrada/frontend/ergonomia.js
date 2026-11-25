"use strict";
// Menu utilizável por toque e teclado, compartilhado entre os três painéis.
(() => {
    const sidebar = document.getElementById("sidebar");
    const toggle = document.getElementById("menuButton") || document.getElementById("driverMenu") || document.getElementById("managementMenu");
    if (sidebar && toggle) {
        const backdrop = document.createElement("button");
        backdrop.type = "button";
        backdrop.className = "menu-backdrop";
        backdrop.setAttribute("aria-label", "Fechar menu de navegação");
        backdrop.hidden = true;
        document.body.append(backdrop);
        toggle.setAttribute("aria-controls", sidebar.id);
        const synchronize = () => {
            const open = sidebar.classList.contains("open");
            toggle.setAttribute("aria-expanded", String(open));
            backdrop.hidden = !open;
            backdrop.classList.toggle("is-open", open);
        };
        const close = () => { sidebar.classList.remove("open"); synchronize(); };
        new MutationObserver(synchronize).observe(sidebar, {attributes:true, attributeFilter:["class"]});
        backdrop.addEventListener("click", close);
        sidebar.querySelectorAll("nav a").forEach(link => link.addEventListener("click", close));
        document.addEventListener("keydown", event => {
            if (event.key === "Escape" && sidebar.classList.contains("open")) {close(); toggle.focus();}
        });
        synchronize();
    }
    // CPF e e-mail não recebem correção automática nem iniciais maiúsculas.
    for (const id of ["loginId","driverLoginId","managementEmail"]) {
        const field = document.getElementById(id);
        if (field) {field.autocapitalize="none"; field.spellcheck=false; field.setAttribute("autocorrect","off");}
    }
    if (document.body.dataset.area === "motorista") {
        const sections = [document.getElementById("motorista"),document.getElementById("suporte")];
        const navigate = () => {
            const page = location.hash === "#suporte" ? "suporte" : "motorista";
            sections.forEach(section => {if (section) section.hidden=section.id!==page;});
            document.querySelectorAll("#sidebar nav a").forEach(link => {
                const active=link.hash === "#"+page;
                link.classList.toggle("active",active);
                if (active) link.setAttribute("aria-current","page"); else link.removeAttribute("aria-current");
            });
            requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
        };
        window.addEventListener("hashchange",navigate);
        navigate();
    }
    // Indica a página ativa também para leitores de tela.
    const links = [...document.querySelectorAll("#sidebar nav a,.bottom-nav a")];
    const updateCurrent = () => links.forEach(link => {
        if (link.classList.contains("active")) link.setAttribute("aria-current", "page");
        else link.removeAttribute("aria-current");
    });
    links.forEach(link => new MutationObserver(updateCurrent).observe(link, {attributes:true, attributeFilter:["class"]}));
    updateCurrent();
    window.addEventListener("hashchange", () => requestAnimationFrame(() => {
        const title = [...document.querySelectorAll("main h1")].find(element => element.getClientRects().length);
        if (title) {title.tabIndex = -1; title.focus({preventScroll:true});}
    }));
})();
