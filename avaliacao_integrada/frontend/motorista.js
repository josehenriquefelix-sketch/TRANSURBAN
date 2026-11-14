"use strict";
const $ = id => document.getElementById(id);
const state = {
    user: null,
    catalog: null,
    driver: null
};
let renewal = null,
    watcher = null,
    lastPositionSent = 0,
    sendingPosition = false,
    driverAccuracyCircle = null,
    driverRefreshTimer = null,
    driverRefreshing = false;
const maps = {},
    markers = {};
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
    if (path === "/auth/logout") window.dispatchEvent(new Event("transurban:logout"));
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

function mapFor(id) {
    if (!window.L) {
        $(id).textContent = "O mapa não pôde ser carregado. Confira a conexão.";
        return null;
    }
    if (!maps[id]) {
        maps[id] = L.map(id).setView([-23.427, -51.902], 12);
        L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(maps[id]);
        markers[id] = L.layerGroup().addTo(maps[id]);
    }
    requestAnimationFrame(() => maps[id].invalidateSize());
    return maps[id];
}

function plotBus(id, position, label) {
    const map = mapFor(id);
    if (!map) return;
    const icon = L.divIcon({
        className: "",
        html: `<span class="bus-marker ${position.recente===false?"stale":""}">▣</span>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18]
    });
    const marker = L.marker([position.latitude, position.longitude], {
        icon
    });
    marker.bindPopup(node("span", label));
    marker.addTo(markers[id]);
}
function fillDriverLines(selected = "") {
    const city = $("driverCity").value;
    const lines = (state.catalog?.linhas || []).filter(line => city === "Maringá" ? line.ambito === "maringa" : city === "metropolitano" ? line.ambito === "metropolitano" : line.cidades.includes("Sarandi"));
    $("driverLine").replaceChildren(new Option("Selecione uma linha", ""), ...lines.map(line => new Option(`${line.codigo} · ${line.nome}`, line.id)));
    if (lines.some(line => line.id === selected)) $("driverLine").value = selected;
    fillDirections($("driverLine").value, "driverDirection");
    updateRouteSummary();
}
function updateRouteSummary() {
    const line = findLine($("driverLine").value);
    const trip = state.driver?.viagem;
    const prefix = trip?.prefixo || $("busPrefix").value.trim();
    const model = trip?.modelo || $("busModel").value.trim();
    $("driverRouteSummary").textContent = line ? `${prefix ? "Ônibus " + prefix : "Informe a numeração do ônibus"}${model ? " · " + model : ""} · ${line.codigo} · ${line.nome} · ${$("driverDirection").value}${trip ? " · viagem vinculada à sua conta" : ""}` : "Selecione uma linha para vincular o ônibus à sua viagem.";
    $("driverItinerary").hidden = !line;
    if (line) $("driverItinerary").href = line.consulta_oficial_url || line.fonte_url;
}
function profilePayload() {
    return {nome_publico: $("driverName").value, ano_nascimento: $("driverBirth").value ? Number($("driverBirth").value) : null, bio: $("driverBio").value, exibir_perfil: $("publicDriverConsent").checked, modelo: $("busModel").value, prefixo: $("busPrefix").value};
}
function initialPosition() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) return reject(new Error("Este navegador não oferece localização."));
        navigator.geolocation.getCurrentPosition(position => {
            const c = position.coords;
            if (![c.latitude,c.longitude,c.accuracy].every(Number.isFinite) || c.accuracy < 0 || c.accuracy > 1000) return reject(new Error("O sinal ainda não tem precisão suficiente. Confira o GPS e tente novamente com o ônibus parado."));
            resolve(position);
        }, error => reject(new Error(error.code === 1 ? "A viagem não foi iniciada: permita a localização para compartilhar o GPS." : "A viagem não foi iniciada: não foi possível obter o GPS. Tente novamente.")), {enableHighAccuracy:true,timeout:20000,maximumAge:0});
    });
}
async function driverPanel({background = false} = {}) {
    const previousTrip = state.driver?.viagem?.id;
    state.driver = await api("/mobilidade/motorista");
    if (previousTrip && previousTrip !== state.driver.viagem?.id) stopGps();
    const data = state.driver;
    $("driverStats").replaceChildren(metric("Minha avaliação", data.indicadores.avaliacao ? `${data.indicadores.avaliacao} ★` : "—", `${data.indicadores.quantidade_notas} notas vinculadas`), metric("Elogios", data.indicadores.elogios), metric("Reclamações", data.indicadores.reclamacoes), metric("Estado da viagem", data.viagem ? "Ativa" : "Preparação"));
    const profile = data.perfil;
    if (!profile && !$("driverName").value) $("driverName").value = state.user?.nome || "";
    if (profile && !background) {
        $("driverName").value = profile.nome_publico;
        $("busModel").value = profile.modelo;
        $("busPrefix").value = profile.prefixo;
        $("driverBirth").value = profile.ano_nascimento || "";
        $("driverBio").value = profile.bio;
        $("publicDriverConsent").checked = profile.exibir_perfil;
    }
    $("startTrip").hidden = Boolean(data.viagem);
    $("endTrip").hidden = !data.viagem;
    $("resumeGps").hidden = !data.viagem;
    $("driverTripBadge").textContent = data.viagem ? "Trajeto iniciado" : "Trajeto não iniciado";
    $("driverProfileForm").querySelectorAll("input,textarea,button").forEach(input => input.disabled = Boolean(data.viagem));
    $("driverCity").disabled = Boolean(data.viagem);
    $("driverLine").disabled = Boolean(data.viagem);
    $("driverDirection").disabled = Boolean(data.viagem);
    $("locationConsent").disabled = Boolean(data.viagem);
    if (data.viagem) {
        $("driverCity").value = findLine(data.viagem.linha_id)?.ambito === "maringa" ? "Maringá" : "metropolitano";
        fillDriverLines(data.viagem.linha_id);
        $("driverLine").value = data.viagem.linha_id;
        fillDirections(data.viagem.linha_id, "driverDirection");
        $("driverDirection").value = data.viagem.sentido;
        $("locationConsent").checked = true;
    }
    $("driverReviews").replaceChildren();
    for (const review of data.avaliacoes) {
        const card = node("article", "", "record");
        card.append(node("h3", `${review.tipo} · ${review.categoria}`), node("p", review.relato), node("small", `${dateTime(review.criada_em)} · TU-${String(review.numero).padStart(6,"0")}`));
        $("driverReviews").append(card);
    }
    if (!data.avaliacoes.length) $("driverReviews").append(node("p", "Ainda não há manifestações vinculadas às suas viagens.", "empty"));
    $("wazeLink").href = "https://www.waze.com/ul?q=" + encodeURIComponent($("driverDirection").value.includes("→ Sarandi") ? "Sarandi Paraná" : "Maringá Paraná");
    mapFor("driverMap");
    updateRouteSummary();
}

function stopGps() {
    if (watcher !== null) navigator.geolocation.clearWatch(watcher);
    watcher = null;
    markers.driverMap?.clearLayers();
    driverAccuracyCircle?.remove();
    driverAccuracyCircle = null;
    $("driverGpsStatus").textContent = "Compartilhamento GPS pausado.";
}

function startGps(firstPosition = null) {
    if (!state.driver?.viagem) {
        toast("Inicie uma viagem antes de compartilhar a posição.");
        return;
    }
    if (!navigator.geolocation) {
        status("tripStatus", "O navegador não oferece acesso à localização.", true);
        return;
    }
    stopGps();
    lastPositionSent = 0;
    $("driverGpsStatus").textContent = "Aguardando permissão e posição do dispositivo…";
    const tripId = state.driver.viagem.id;
    const receivePosition = async position => {
        if (sendingPosition || Date.now() - lastPositionSent < 10000 || state.driver?.viagem?.id !== tripId) return;
        const coords = position.coords;
        if (coords.accuracy > 1000) {
            $("driverGpsStatus").textContent = "Precisão insuficiente. Aguardando melhor sinal GPS.";
            return;
        }
        sendingPosition = true;
        try {
            await api(`/mobilidade/motorista/viagens/${tripId}/posicao`, {
                method: "POST",
                body: JSON.stringify({
                    latitude: coords.latitude,
                    longitude: coords.longitude,
                    precisao_m: coords.accuracy,
                    direcao: Number.isFinite(coords.heading) ? coords.heading : null
                })
            });
            if (watcher === null || state.driver?.viagem?.id !== tripId) return;
            lastPositionSent = Date.now();
            const map = mapFor("driverMap");
            if (map) {
                markers.driverMap.clearLayers();
                plotBus("driverMap", {
                    latitude: coords.latitude,
                    longitude: coords.longitude
                }, "Posição deste dispositivo");
                driverAccuracyCircle?.remove();
                driverAccuracyCircle = L.circle([coords.latitude, coords.longitude], {radius:coords.accuracy,color:"#de762f",weight:1,fillOpacity:.08}).addTo(map);
                map.setView([coords.latitude, coords.longitude], 15);
            }
            $("driverGpsStatus").textContent = `GPS compartilhado • ${new Date().toLocaleTimeString("pt-BR")} • precisão ${Math.round(coords.accuracy)} m`;
        } catch (error) {
            status("tripStatus", error.message, true);
        } finally {
            sendingPosition = false;
        }
    };
    watcher = navigator.geolocation.watchPosition(receivePosition, error => {
        status("tripStatus", error.code === 1 ? "Localização não autorizada. Permita o GPS e toque em Retomar compartilhamento." : "Posição indisponível. Confira o GPS e tente retomar.", true);
        $("driverGpsStatus").textContent = "Sem sinal GPS recente.";
    }, {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 3000
    });
    if (firstPosition?.coords) receivePosition(firstPosition);
}
async function endTrip() {
    if (!state.driver?.viagem) return;
    stopGps();
    await api(`/mobilidade/motorista/viagens/${state.driver.viagem.id}/encerrar`, {
        method: "POST"
    });
    await driverPanel();
    status("tripStatus", "Trajeto encerrado e compartilhamento finalizado.");
}


function findLine(id) {
    return state.catalog?.linhas.find(line => line.id === id);
}

function fillDirections(id, target) {
    $(target).replaceChildren(...(findLine(id)?.sentidos || ["Ida", "Volta"]).map(s => new Option(s, s)));
}
async function driverAccount() {
    let user;
    try {
        user = await api("/auth/me", {}, false);
    } catch {
        await api("/auth/refresh", {
            method: "POST"
        }, false);
        user = await api("/auth/me", {}, false);
    }
    if (!user.papeis?.includes("motorista")) throw new Error("Sua conta ainda não tem aprovação para motorista. Solicite o vínculo abaixo.");
    state.user = user;
    state.catalog = await api("/mobilidade/catalogo");
    fillDriverLines();
    $("driverAccountName").textContent = user.nome;
    $("driverSessionName").textContent = user.nome;
    $("driverLogin").hidden = true;
    $("driverShell").hidden = false;
    await driverPanel();
    window.TransurbanOps?.refresh();
    if (!driverRefreshTimer) driverRefreshTimer = setInterval(async () => {
        if (document.hidden || $("driverShell").hidden || driverRefreshing) return;
        driverRefreshing=true;
        try { await driverPanel({background:true}); }
        catch (error) { status("tripStatus", "Não foi possível atualizar a operação. O sistema tentará novamente.", true); }
        finally { driverRefreshing=false; }
    },15000);
}
$("driverLoginForm").addEventListener("submit", event => {
    event.preventDefault();
    action("driverLoginForm", "driverLoginStatus", async () => {
        await api("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                identificador: $("driverLoginId").value,
                senha: $("driverLoginPassword").value,
                tipo_acesso: "motorista"
            })
        });
        $("driverLoginPassword").value = "";
        await driverAccount();
    });
});
$("driverProfileForm").addEventListener("submit", event => {
    event.preventDefault();
    action("driverProfileForm", "driverProfileStatus", async () => {
        await api("/mobilidade/motorista/perfil", {
            method: "PUT",
            body: JSON.stringify(profilePayload())
        });
        status("driverProfileStatus", "Perfil salvo.");
        await driverPanel();
    });
});
$("driverCity").addEventListener("change", () => fillDriverLines());
$("driverLine").addEventListener("change", () => {fillDirections($("driverLine").value, "driverDirection"); updateRouteSummary();});
$("driverDirection").addEventListener("change", updateRouteSummary);
$("busModel").addEventListener("input", updateRouteSummary);
$("busPrefix").addEventListener("input", updateRouteSummary);
$("tripForm").addEventListener("submit", event => {
    event.preventDefault();
    return action("tripForm", "tripStatus", async () => {
        if (!$("locationConsent").checked) throw new Error("Autorize o compartilhamento durante esta viagem.");
        if (!$("driverProfileForm").reportValidity()) throw new Error("Preencha os dados do ônibus e do perfil antes de iniciar.");
        status("tripStatus", "Verificando a permissão e o sinal GPS antes de iniciar…");
        const firstPosition = await initialPosition();
        await api("/mobilidade/motorista/perfil", {method:"PUT", body:JSON.stringify(profilePayload())});
        state.driver.viagem = await api("/mobilidade/motorista/viagens", {
            method: "POST",
            body: JSON.stringify({
                linha_id: $("driverLine").value,
                sentido: $("driverDirection").value
            })
        });
        await driverPanel();
        startGps(firstPosition);
        status("tripStatus", "Viagem iniciada. O ônibus está vinculado à sua conta e à linha escolhida.");
    });
});
$("resumeGps").addEventListener("click", () => startGps());
$("endTrip").addEventListener("click", () => {
    if (confirm("Encerrar o trajeto e parar o compartilhamento?")) endTrip().catch(e => status("tripStatus", e.message, true));
});
$("driverLogout").addEventListener("click", async () => {
    try {
        if (state.driver?.viagem) {
            if (!confirm("Encerrar o trajeto ativo e sair?")) return;
            await endTrip();
        }
        await api("/auth/logout", {
            method: "POST"
        });
        stopGps();
        location.reload();
    } catch (e) {
        toast(e.message);
    }
});
$("driverMenu").addEventListener("click", () => $("sidebar").classList.toggle("open"));
window.addEventListener("pagehide", () => {stopGps(); clearInterval(driverRefreshTimer); driverRefreshTimer=null;});
driverAccount().catch(e => status("driverLoginStatus", e.message.includes("Entre") ? "" : e.message, true));
