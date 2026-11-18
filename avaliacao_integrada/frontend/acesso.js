"use strict";
// Ajuda de entrada compartilhada. Nenhuma senha é salva no navegador.
(() => {
    const campos = ["loginPassword", "driverLoginPassword", "managementPassword"];
    for (const id of campos) {
        const input = document.getElementById(id);
        if (!input) continue;
        const button = document.createElement("button");
        button.type = "button";
        button.className = "password-toggle";
        button.textContent = "Mostrar senha";
        button.setAttribute("aria-controls", id);
        button.setAttribute("aria-pressed", "false");
        button.addEventListener("click", () => {
            const mostrar = input.type === "password";
            input.type = mostrar ? "text" : "password";
            button.textContent = mostrar ? "Ocultar senha" : "Mostrar senha";
            button.setAttribute("aria-pressed", String(mostrar));
        });
        input.after(button);
        const aviso = document.createElement("small");
        aviso.className = "status";
        aviso.setAttribute("role", "status");
        button.after(aviso);
        input.addEventListener("keyup", event => {
            aviso.textContent = event.getModifierState?.("CapsLock") ? "A tecla de letras maiúsculas está ligada." : "";
        });
        input.addEventListener("blur", () => { aviso.textContent = ""; });
    }
    for (const id of ["driverLoginForm", "managementLoginForm"]) {
        const form = document.getElementById(id);
        if (!form) continue;
        const info = document.createElement("p");
        info.className = "access-help";
        info.textContent = "Entre com sua conta profissional já cadastrada. Se ainda não possui acesso autorizado, procure o responsável pelo TRANSURBAN.";
        form.append(info);
    }
})();
