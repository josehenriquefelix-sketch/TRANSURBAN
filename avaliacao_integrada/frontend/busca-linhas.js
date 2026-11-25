"use strict";
// Busca progressiva: a lista nativa continua disponível em todos os navegadores.
(() => {
    const normalizar = texto => String(texto || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim().replace(/\s+/g, " ");
    function encontrar(opcoes, consulta) {
        const busca = normalizar(consulta);
        if (!busca) return null;
        const validas = opcoes.filter(opcao => opcao.value);
        const exatas = validas.filter(opcao => normalizar(opcao.text) === busca);
        if (exatas.length) return exatas.length === 1 ? exatas[0] : null;
        const codigos = validas.filter(opcao => normalizar(opcao.text.split(" · ")[0]) === busca);
        if (codigos.length === 1) return codigos[0];
        const resultados = validas.filter(opcao => normalizar(opcao.text).includes(busca));
        return resultados.length === 1 ? resultados[0] : null;
    }
    window.TransurbanBusca = {encontrar};
    for (const id of ["homeLine", "scheduleLine", "driverLine"]) {
        const select = document.getElementById(id);
        if (!select) continue;
        const wrapper = document.createElement("div");
        wrapper.className = "line-quick-search";
        const input = document.createElement("input");
        input.type = "search";
        input.id = id + "QuickSearch";
        input.placeholder = "Buscar por bairro ou código";
        input.autocomplete = "off";
        input.setAttribute("aria-label", "Buscar linha por bairro ou código");
        input.setAttribute("enterkeyhint", "search");
        input.setAttribute("list", id + "Suggestions");
        const suggestions = document.createElement("datalist");
        suggestions.id = id + "Suggestions";
        const help = document.createElement("small");
        help.id = id + "SearchHelp";
        help.className = "line-search-help";
        help.textContent = "Digite para buscar ou escolha na lista abaixo.";
        help.setAttribute("role", "status");
        input.setAttribute("aria-describedby", help.id);
        wrapper.append(input, suggestions, help);
        select.before(wrapper);
        const options = () => [...select.options].map(option => ({value:option.value, text:option.text}));
        function refresh() {
            suggestions.replaceChildren(...options().filter(option => option.value).map(option => new Option(option.text, option.text)));
            input.value = "";
            input.disabled = select.disabled || !suggestions.children.length;
            help.textContent = suggestions.children.length ? "Digite para buscar ou escolha na lista abaixo." : "Selecione a cidade para carregar as linhas disponíveis.";
        }
        function choose(option) {
            if (!option || select.disabled) return;
            const mudou = select.value !== option.value;
            select.value = option.value;
            input.value = option.text;
            help.textContent = "Linha selecionada: " + option.text;
            if (mudou) select.dispatchEvent(new Event("change", {bubbles:true}));
        }
        input.addEventListener("change", () => {
            const opcoes = options().filter(option => option.value && normalizar(option.text) === normalizar(input.value));
            if (opcoes.length === 1) choose(opcoes[0]);
        });
        input.addEventListener("keydown", event => {
            if (event.key !== "Enter") return;
            event.preventDefault();
            const option = encontrar(options(), input.value);
            if (option) choose(option);
            else help.textContent = "Escolha uma sugestão ou informe um código ou bairro mais específico.";
        });
        new MutationObserver(refresh).observe(select, {childList:true, attributes:true, attributeFilter:["disabled"]});
        refresh();
    }
})();
