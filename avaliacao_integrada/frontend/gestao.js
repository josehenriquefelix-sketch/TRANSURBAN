"use strict";
const $ = id => document.getElementById(id);
const state = {
    user: null,
    catalog: null,
    queue: [],
    selectedReport: null
};
let renewal = null;
const dateTime = value => new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
    timeZone: "America/Sao_Paulo"
}).format(new Date(value));

function node(tag, text, cls = "") {
    const item = document.createElement(tag);
    item.textContent = text;
    item.className = cls;
    return item;
}

function status(id, message, error = false) {
    $(id).textContent = message;
    $(id).classList.toggle("error", error);
}

function toast(message) {
    $("toast").textContent = message;
    $("toast").hidden = false;
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => {
        $("toast").hidden = true;
    }, 6500);
}
async function api(path, options = {}, retry = true) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);
    let response;
    try {
        response = await fetch(path, {
            ...options,
            signal: controller.signal,
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                ...options.headers
            }
        });
    } catch {
        throw new Error("Não foi possível acessar o serviço. Confira a conexão e se o servidor está aberto.");
    } finally {
        clearTimeout(timeout);
    }
    if (response.status === 401 && retry && !path.startsWith("/auth/")) {
        if (!renewal) renewal = api("/auth/refresh", {
            method: "POST"
        }, false).then(() => true).catch(() => false).finally(() => {
            renewal = null;
        });
        if (await renewal) return api(path, options, false);
    }
    if (response.status === 204) return null;
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        if (Array.isArray(data.detail)) {
            const labels = {
                cpf: "CPF",
                senha: "Senha",
                nome: "Nome",
                email: "E-mail",
                relato: "Relato",
                prefixo: "Prefixo",
                modelo: "Modelo",
                nome_publico: "Nome público",
                ano_nascimento: "Ano de nascimento"
            };
            throw new Error(data.detail.map(error => {
                const name = labels[error.loc?.[error.loc.length - 1]] || "Campo informado";
                if (error.type === "value_error") return `${name} — ${error.msg.replace(/^Value error,\s*/,"")}`;
                if (error.type === "string_too_short") return `${name} — use pelo menos ${error.ctx.min_length} caracteres.`;
                return `${name} — confira o valor preenchido.`;
            }).join(" "));
        }
        throw new Error(typeof data.detail === "string" ? data.detail : "Não foi possível concluir esta operação.");
    }
    return data;
}
async function action(formId, feedback, work) {
    const button = $(formId).querySelector('button:not([type="button"])');
    button.disabled = true;
    status(feedback, "Aguarde…");
    try {
        await work();
    } catch (error) {
        status(feedback, error.message, true);
    } finally {
        button.disabled = false;
    }
}

function metric(label, value, detail = "") {
    const card = node("article", "", "metric");
    card.append(node("span", label), node("strong", value ?? "—"));
    if (detail) card.append(node("small", detail));
    return card;
}

function findLine(id) {
    return state.catalog?.linhas.find(line => line.id === id);
}

function renderQueue() {
    const records = state.queue.filter(record => (!$("managerStatus").value || record.status === $("managerStatus").value) && (!$("managerType").value || record.tipo === $("managerType").value));
    $("managerQueue").replaceChildren();
    for (const record of records) {
        const button = node("button", "", "record plain");
        button.type = "button";
        button.append(node("span", `TU-${String(record.numero).padStart(6,"0")} · ${record.status.replaceAll("_"," ")}`, "tag"), node("h3", `${record.tipo} · ${record.categoria}`), node("p", `${record.cidade} · ${findLine(record.linha_id)?.codigo||record.linha_id}`), node("small", dateTime(record.criada_em)));
        button.addEventListener("click", () => {
            state.selectedReport = record;
            $("managerDetail").replaceChildren(node("h3", `TU-${String(record.numero).padStart(6,"0")}`), node("p", `${record.tipo} · ${record.categoria} · competência ${record.competencia}`), node("p", record.relato), node("small", dateTime(record.criada_em)));
            $("responseForm").hidden = record.status === "encerrada";
            $("responseText").value = record.resposta || "";
            $("responseStatus").value = record.status === "recebida" ? "em_analise" : record.status;
            status("responseFeedback", "");
            if (record.status === "encerrada") $("managerDetail").append(node("p", record.resposta));
        });
        $("managerQueue").append(button);
    }
    if (!records.length) $("managerQueue").append(node("p", "Nenhuma manifestação para esses filtros.", "empty"));
}
async function managerPanel() {
    state.queue = await api("/mobilidade/gestao/manifestacoes");
    state.selectedReport = null;
    $("managerDetail").replaceChildren(node("p", "Selecione uma manifestação para analisar."));
    $("responseForm").hidden = true;
    $("managerStats").replaceChildren(metric("Recebidas", state.queue.filter(r => r.status === "recebida").length), metric("Em análise", state.queue.filter(r => r.status === "em_analise").length), metric("Respondidas", state.queue.filter(r => r.status === "respondida").length), metric("Encerradas", state.queue.filter(r => r.status === "encerrada").length));
    renderQueue();
}

function showLogin(message = "") {
    state.user = null;
    state.queue = [];
    state.selectedReport = null;
    $("managementLogin").hidden = false;
    $("managementShell").hidden = true;
    $("managerQueue").replaceChildren();
    $("managerDetail").replaceChildren();
    $("managerStats").replaceChildren();
    $("responseForm").hidden = true;
    status("managementStatus", message, Boolean(message));
}
async function openManagement() {
    let user;
    try {
        user = await api("/auth/me", {}, false);
    } catch {
        await api("/auth/refresh", {
            method: "POST"
        }, false);
        user = await api("/auth/me", {}, false);
    }
    if (!user.papeis?.includes("gestor")) {
        showLogin("Esta conta não possui autorização de gestão. Entre com uma conta autorizada.");
        return;
    }
    state.user = user;
    if (!state.catalog) state.catalog = await api("/mobilidade/catalogo");
    await managerPanel();
    $("managementName").textContent = user.nome;
    $("managementLogin").hidden = true;
    $("managementShell").hidden = false;
    window.TransurbanOps?.refresh();
}
$("managementLoginForm").addEventListener("submit", event => {
    event.preventDefault();
    action("managementLoginForm", "managementStatus", async () => {
        await api("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                identificador: $("managementEmail").value,
                senha: $("managementPassword").value,
                tipo_acesso: "gestor"
            })
        });
        $("managementPassword").value = "";
        await openManagement();
        status("managementStatus", "");
    });
});
$("managerStatus").addEventListener("change", renderQueue);
$("managerType").addEventListener("change", renderQueue);
$("refreshManager").addEventListener("click", async () => {
    try {
        await managerPanel();
        toast("Fila atualizada.");
    } catch (error) {
        if (error.message.includes("conta") || error.message.includes("Acesso")) showLogin(error.message);
        else toast(error.message);
    }
});
$("responseForm").addEventListener("submit", event => {
    event.preventDefault();
    action("responseForm", "responseFeedback", async () => {
        if (!state.selectedReport) throw new Error("Selecione uma manifestação.");
        await api(`/mobilidade/gestao/manifestacoes/${state.selectedReport.id}`, {
            method: "PUT",
            body: JSON.stringify({
                status: $("responseStatus").value,
                resposta: $("responseText").value
            })
        });
        toast("Atendimento salvo. A resposta está disponível ao cidadão.");
        await managerPanel();
    });
});
$("managementLogout").addEventListener("click", async () => {
    try {
        await api("/auth/logout", {
            method: "POST"
        });
        showLogin();
        toast("Você saiu do painel de gestão.");
    } catch (error) {
        toast(error.message);
    }
});
$("managementMenu").addEventListener("click", () => {
    const open = $("sidebar").classList.toggle("open");
    $("managementMenu").setAttribute("aria-expanded", String(open));
});
document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        $("sidebar").classList.remove("open");
        $("managementMenu").setAttribute("aria-expanded", "false");
    }
});
openManagement().catch(error => showLogin(error.message.includes("Entre") ? "" : error.message));
