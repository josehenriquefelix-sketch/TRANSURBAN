"use strict";
// Reconectar nunca reenvia formulários ou concede permissões: a API valida a sessão.
(() => {
    const banner = document.createElement("div");
    banner.className = "network-message";
    banner.setAttribute("role", "status");
    banner.hidden = navigator.onLine !== false;
    banner.textContent = "Você está sem conexão com a rede. Confira a conexão antes de enviar ou atualizar informações.";
    document.body.append(banner);
    window.addEventListener("offline", () => {banner.hidden = false;});
    window.addEventListener("online", () => {banner.hidden = true;});
    for (const config of [
        {form:"driverLoginForm", feedback:"driverLoginStatus", shell:"driverShell", retry:() => driverAccount()},
        {form:"managementLoginForm", feedback:"managementStatus", shell:"managementShell", retry:() => openManagement()}
    ]) {
        const form = document.getElementById(config.form);
        const feedback = document.getElementById(config.feedback);
        if (!form || !feedback) continue;
        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn quiet wide reconnect-button";
        button.textContent = "Tentar reconectar";
        button.hidden = true;
        feedback.after(button);
        const update = () => {button.hidden = !/indisponível|conexão|não foi possível acessar/i.test(feedback.textContent);};
        new MutationObserver(update).observe(feedback, {childList:true, characterData:true, subtree:true});
        button.addEventListener("click", async () => {
            button.disabled = true;
            form.setAttribute("aria-busy", "true");
            feedback.textContent = "Verificando conexão e sessão…";
            try {
                await config.retry();
                if (!document.getElementById(config.shell).hidden) feedback.textContent = "";
                else if (feedback.textContent === "Verificando conexão e sessão…") feedback.textContent = "Entre com uma conta autorizada para continuar.";
            } catch (error) {
                feedback.textContent = error.message;
            } finally {
                button.disabled = false;
                form.removeAttribute("aria-busy");
            }
        });
        update();
    }
})();
