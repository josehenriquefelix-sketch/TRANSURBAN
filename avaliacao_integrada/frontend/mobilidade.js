"use strict";
const $ = id => document.getElementById(id);
const state = {
    ready: false,
    user: null,
    catalog: null,
    city: "Maringá",
    line: null,
    favorites: [],
    trips: [],
    driver: null,
    queue: [],
    selectedReport: null,
    loginRole: "passageiro",
    page: "inicio"
};
let renewal = null,
    polling = null,
    watcher = null,
    lastPositionSent = 0,
    sendingPosition = false,
    recoveryToken = null;
const maps = {},
    markers = {};
const titles = {
    inicio: "Visão geral",
    dashboard: "Dashboard de mobilidade",
    cidades: "Cidades e linhas",
    horarios: "Horários e mapa",
    favoritos: "Minhas linhas",
    avaliacoes: "Avaliações",
    passe: "Meu passe",
    sobre: "Sobre o projeto",
    motorista: "Área do motorista",
    gestao: "Central de gestão",
    conta: "Minha conta"
};
const authScreens = {
    login: "loginForm",
    cadastro: "signupForm",
    "esqueci-senha": "forgotForm",
    "nova-senha": "resetForm"
};
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

function hasRole(role) {
    return Boolean(state.user?.papeis?.includes(role));
}

function accountUI() {
    $("userName").textContent = state.user ? state.user.nome.split(" ")[0] : "Entrar";
    $("avatar").textContent = state.user ? state.user.nome.slice(0, 1).toUpperCase() : "↗";
    $("userLink").href = state.user ? "#conta" : "#login";
    document.querySelectorAll("[data-logout]").forEach(button => button.hidden = !state.user);
    document.querySelectorAll("[data-role]").forEach(element => element.hidden = !hasRole(element.dataset.role));
}
async function account() {
    try {
        state.user = await api("/auth/me", {}, false);
    } catch {
        try {
            await api("/auth/refresh", {
                method: "POST"
            }, false);
            state.user = await api("/auth/me", {}, false);
        } catch {
            state.user = null;
        }
    }
    accountUI();
}

function linesFor(city) {
    return (state.catalog?.linhas || []).filter(line => city === "todas" || (city === "metropolitano" ? line.ambito === "metropolitano" : city === "Maringá" ? line.ambito === "maringa" : line.cidades.includes("Sarandi")));
}

function fillLines(id, city, placeholder = true) {
    const previous = $(id).value;
    $(id).replaceChildren();
    if (placeholder) $(id).add(new Option("Selecione uma linha", ""));
    for (const line of linesFor(city)) $(id).add(new Option(`${line.codigo} · ${line.nome}`, line.id));
    if ([...$(id).options].some(option => option.value === previous)) $(id).value = previous;
}

function findLine(id) {
    return state.catalog?.linhas.find(line => line.id === id);
}

function fillDirections(lineId, selectId) {
    const select = $(selectId),
        previous = select.value;
    select.replaceChildren(...(findLine(lineId)?.sentidos || ["Maringá → Sarandi", "Sarandi → Maringá"]).map(value => new Option(value, value)));
    if ([...select.options].some(option => option.value === previous)) select.value = previous;
}

function openLine(id, city) {
    const line = findLine(id);
    if (!line) return;
    state.line = id;
    $("scheduleCity").value = city || (line.ambito === "maringa" ? "Maringá" : "Sarandi");
    fillLines("scheduleLine", $("scheduleCity").value);
    $("scheduleLine").value = id;
    fillDirections(id, "scheduleDirection");
    if ($("scheduleCity").value === "Sarandi" && line.ambito === "metropolitano") $("scheduleDirection").value = "Sarandi → Maringá";
    if (state.page === "horarios") schedules();
    else location.hash = "horarios";
}

function showOfficial(line, points = false) {
    $("officialCard").hidden = !line?.consulta_oficial_url;
    if (!line?.consulta_oficial_url) {
        $("officialFrame").removeAttribute("src");
        return;
    }
    const url = points ? line.consulta_pontos_url : line.consulta_oficial_url;
    if ($("officialFrame").getAttribute("src") !== url) $("officialFrame").src = url;
    $("officialExternal").href = url;
    $("officialHelp").textContent = points ? "Busque o endereço ou toque no ponto no mapa da consulta oficial. Confira se a linha desejada atende esse ponto. Previsões dependem da disponibilidade do provedor." : `${line.codigo} · ${line.nome}. Escolha o sentido e o dia abaixo. Na aba Pontos e trajeto, veja as paradas da viagem selecionada.`;
}

function sourceLink(text, url) {
    const link = node("a", text);
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener";
    return link;
}

function lineCard(line) {
    const card = node("article", "", "card line-card");
    card.append(node("span", line.codigo, "code"), node("h3", line.nome), node("span", line.tipo_servico === "municipal" ? "Municipal • Maringá" : "Metropolitana • Sarandi ↔ Maringá", "tag"), node("p", line.operador), node("small", `Fonte ${line.fonte} • ${line.vigencia ? "Vigência " + line.vigencia.split("-").reverse().join("/") : "Consulta em 12/11/2026"}`));
    if (line.variante_codigo) card.append(node("small", `Atendimento ${line.variante_codigo} da tabela ${line.documento_id.replace("der-", "")}; variante identificada no documento.`));
    if (line.bairros_atendidos?.length > 1) card.append(node("p", "Atendimentos documentados: " + line.bairros_atendidos.join(" · "), "muted"));
    const actions = node("div", "", "line-actions"),
        open = node("button", "Ver horários →", "btn primary"),
        favorite = node("button", state.favorites.some(item => item.id === line.id) ? "★ Salva" : "☆ Salvar", "btn quiet");
    open.type = "button";
    favorite.type = "button";
    open.addEventListener("click", () => {
        openLine(line.id);
    });
    favorite.addEventListener("click", () => toggleFavorite(line.id));
    actions.append(open, favorite, sourceLink("Fonte oficial ↗", line.fonte_url));
    card.append(actions);
    return card;
}

function renderCatalog() {
    const cityLines = linesFor(state.city);
    const message = state.city === "Maringá" ? `${cityLines.length} linhas municipais publicadas na consulta oficial Na Hora Maringá. As ligações com Sarandi estão na aba Maringá ↔ Sarandi. Os nomes abaixo identificam as linhas; bairros intermediários e pontos constam no itinerário de cada viagem.` : state.city === "Sarandi" ? "Linhas metropolitanas que atendem bairros de Sarandi e fazem a ligação com Maringá. Cada documento pode conter variantes para outros bairros. O transporte municipal interbairros de Sarandi é um serviço separado; sua página pública não informa vigência recente." : "Ligações metropolitanas Maringá ↔ Sarandi, operadas pela Cidade Verde e documentadas pelo DER/PR. Elas atendem as duas cidades e não são linhas municipais de Maringá.";
    $("coverage").replaceChildren(node("p", message));
    if (state.city === "Sarandi") $("coverage").append(sourceLink("Consultar interbairros Alvamar ↔ Conjunto Floresta na Prefeitura; confirme a vigência ↗", "https://sarandi.pr.gov.br/web/index.php/servicos/horarios-transporte-publico"));
    const query = $("lineSearch").value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    const filtered = cityLines.filter(line => `${line.codigo} ${line.nome} ${(line.bairros_atendidos || []).join(" ")}`.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().includes(query));
    $("lineCards").replaceChildren(...filtered.map(lineCard));
    if (!filtered.length) $("lineCards").append(node("p", "Nenhuma linha encontrada para esta busca. Consulte os pontos e itinerários na fonte oficial.", "empty"));
    document.querySelectorAll("[data-city]").forEach(button => button.classList.toggle("active", button.dataset.city === state.city));
}
async function loadFavorites() {
    if (!state.user) {
        state.favorites = [];
        $("favoritesList").replaceChildren(node("p", "Entre na sua conta para salvar e consultar suas linhas.", "empty"));
        return;
    }
    state.favorites = await api("/mobilidade/favoritos");
    $("favoritesList").replaceChildren(...state.favorites.map(lineCard));
    if (!state.favorites.length) $("favoritesList").append(node("p", "Você ainda não salvou uma linha. Explore Cidades e linhas para começar.", "empty"));
}
async function toggleFavorite(id) {
    if (!id) {
        toast("Selecione uma linha primeiro.");
        return;
    }
    if (!state.user) {
        toast("Entre na sua conta para salvar uma linha.");
        location.hash = "login";
        return;
    }
    try {
        const saved = state.favorites.some(line => line.id === id);
        await api(`/mobilidade/favoritos/${id}`, {
            method: saved ? "DELETE" : "PUT"
        });
        await loadFavorites();
        renderCatalog();
        toast(saved ? "Linha removida dos favoritos." : "Linha salva em Minhas linhas.");
    } catch (error) {
        toast(error.message);
    }
}

function metric(label, value, detail = "") {
    const card = node("article", "", "metric");
    card.append(node("span", label), node("strong", value ?? "—"));
    if (detail) card.append(node("small", detail));
    return card;
}
async function dashboard() {
    $("publicStats").replaceChildren(metric("Cidades conectadas", "2"), metric("Linhas municipais de Maringá", linesFor("Maringá").length, "Catálogo público Na Hora"), metric("Linhas e variantes de Sarandi", linesFor("metropolitano").length, "12 tabelas DER/PR"), metric("Minhas linhas", state.user ? state.favorites.length : "—"));
    const data = await api("/portal/contexto");
    $("officialInfo").replaceChildren();
    const information = node("article", "", "card");
    information.append(node("span", "INFORMAÇÕES DOCUMENTAIS", "eyebrow"), node("h2", data.titulo), node("p", data.descricao));
    for (const indicator of data.indicadores) information.append(node("p", `${indicator.valor} · ${indicator.rotulo} — ${indicator.contexto}`));
    for (const source of data.fontes) information.append(sourceLink(`${source.titulo} ↗`, source.url), document.createElement("br"));
    information.append(node("p", data.limite, "subtle"));
    $("officialInfo").append(information);
    for (const record of data.registros) {
        const card = node("article", "", "card");
        card.append(node("h3", record.titulo), node("p", record.texto));
        if (record.citacao) {
            const quote = node("blockquote", `“${record.citacao}”`);
            quote.append(node("cite", record.atribuicao));
            card.append(quote);
        }
        const source = data.fontes.find(source => source.id === record.fonte_id);
        card.append(sourceLink("Consultar fonte ↗", source.url));
        $("officialInfo").append(card);
    }
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
async function liveTrips() {
    const id = $("scheduleLine").value;
    if (!id) return;
    const trips = await api(`/mobilidade/viagens?linha_id=${encodeURIComponent(id)}`);
    if (state.page !== "horarios" || $("scheduleLine").value !== id) return;
    state.trips = trips;
    const map = mapFor("passengerMap");
    if (map) markers.passengerMap.clearLayers();
    $("busDetails").replaceChildren();
    for (const trip of trips) {
        if (trip.posicao) plotBus("passengerMap", trip.posicao, `${trip.prefixo} · ${trip.sentido} · ${trip.posicao.recente?"Posição recente":"Sem atualização recente"}`);
        const card = node("div", "", "record");
        card.append(node("h3", `${trip.prefixo} · ${trip.modelo}`), node("p", trip.sentido));
        if (trip.motorista) {
            card.append(node("p", `Motorista ${trip.motorista.nome}${trip.motorista.idade_aproximada?` · idade aproximada ${trip.motorista.idade_aproximada} anos`:""}`), node("p", trip.motorista.bio || ""), node("p", trip.motorista.avaliacao ? `${trip.motorista.avaliacao} ★ · ${trip.motorista.quantidade_notas} avaliações` : "Ainda sem avaliações vinculadas."));
        } else card.append(node("p", "O motorista não disponibilizou perfil público."));
        card.append(node("small", trip.posicao ? `${trip.posicao.recente?"Sinal recente":"Sem sinal recente"} · ${dateTime(trip.posicao.registrada_em)} · precisão ${Math.round(trip.posicao.precisao_m)} m` : "Aguardando posição do dispositivo."));
        const review = node("button", "Avaliar esta viagem", "btn quiet");
        review.type = "button";
        review.addEventListener("click", () => {
            state.reviewTrip = trip;
            location.hash = "avaliacoes";
        });
        card.append(review);
        $("busDetails").append(card);
    }
    if (!trips.length) $("busDetails").append(node("p", "Nenhuma viagem está compartilhando posição nesta linha pelo TRANSURBAN.", "empty"));
    const recent = trips.filter(trip => trip.posicao?.recente).length;
    $("gpsStatus").textContent = recent ? `${recent} veículo(s) com sinal recente. Atualização a cada 10 segundos.` : "Sem posição recente disponível. A previsão da operadora fica na consulta oficial, quando disponível.";
}

async function schedules() {
    const id = $("scheduleLine").value;
    if (!id) return;
    state.line = id;
    const line = findLine(id),
        official = Boolean(line?.consulta_oficial_url);
    $("scheduleDirectionField").hidden = official;
    $("scheduleDayField").hidden = official;
    $("documentScheduleCard").hidden = official;
    showOfficial(line);
    status("scheduleStatus", "Consultando a programação documentada…");
    try {
        const result = await api(`/mobilidade/horarios/${encodeURIComponent(id)}?tipo_dia=${$("scheduleDay").value}&sentido=${encodeURIComponent($("scheduleDirection").value)}`);
        if ($("scheduleLine").value !== id) return;
        $("scheduleRows").replaceChildren();
        for (const schedule of result.horarios) {
            const row = document.createElement("tr");
            for (const value of [schedule.partida, schedule.sentido, result.linha.legendas_variantes?.[schedule.variante] || "Atendimento da linha", schedule.chegada_prevista || "Não publicada"]) row.append(node("td", value));
            $("scheduleRows").append(row);
        }
        if (!result.horarios.length) {
            const row = document.createElement("tr"),
                cell = node("td", result.linha.horarios_completos ? "O documento não prevê partidas para esse tipo de dia e sentido." : "A tabela completa desta linha está no documento oficial. Abra a fonte abaixo.");
            cell.colSpan = 4;
            row.append(cell);
            $("scheduleRows").append(row);
        }
        $("scheduleSource").replaceChildren(node("p", result.linha.nome), node("p", result.linha.vigencia ? `Vigência ${result.linha.vigencia.split("-").reverse().join("/")}` : "Catálogo consultado em 12/11/2026"), sourceLink(official ? "Na Hora Maringá · fonte oficial ↗" : "Abrir tabela oficial DER/PR ↗", result.linha.fonte_url));
        status("scheduleStatus", official ? "A consulta oficial da linha está abaixo. Escolha o sentido, o dia e consulte os pontos diretamente no quadro da operadora." : result.aviso);
        mapFor("passengerMap");
        await liveTrips();
    } catch (error) {
        status("scheduleStatus", error.message, true);
    }
}
async function loadReviewTrips() {
    $("reviewTrip").replaceChildren(new Option("Não vincular uma viagem", ""));
    if (!$("reviewLine").value) return;
    const trips = await api(`/mobilidade/viagens?linha_id=${encodeURIComponent($("reviewLine").value)}`);
    for (const trip of trips) $("reviewTrip").add(new Option(`${trip.prefixo} · ${trip.sentido}`, trip.id));
    if (state.reviewTrip?.linha_id === $("reviewLine").value) $("reviewTrip").value = state.reviewTrip.id;
}
async function reviewHistory() {
    $("reviewHistory").replaceChildren();
    if (!state.user) {
        $("reviewHistory").append(node("p", "Entre na sua conta para enviar e acompanhar manifestações.", "empty"));
        return;
    }
    const records = await api("/mobilidade/minhas-manifestacoes");
    for (const record of records) {
        const card = node("article", "", "record");
        card.append(node("span", `TU-${String(record.numero).padStart(6,"0")} · ${record.status.replaceAll("_"," ")}`, "tag"), node("h3", `${record.tipo} · ${record.categoria}`), node("p", record.relato), node("small", dateTime(record.criada_em)));
        if (record.resposta) card.append(node("p", `Resposta da central TRANSURBAN: ${record.resposta}`));
        $("reviewHistory").append(card);
    }
    if (!records.length) $("reviewHistory").append(node("p", "Você ainda não enviou uma manifestação.", "empty"));
}
async function driverPanel() {
    state.driver = await api("/mobilidade/motorista");
    const data = state.driver;
    $("driverStats").replaceChildren(metric("Minha avaliação", data.indicadores.avaliacao ? `${data.indicadores.avaliacao} ★` : "—", `${data.indicadores.quantidade_notas} notas vinculadas`), metric("Elogios", data.indicadores.elogios), metric("Reclamações", data.indicadores.reclamacoes), metric("Estado da viagem", data.viagem ? "Ativa" : "Preparação"));
    const profile = data.perfil;
    if (profile) {
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
    $("driverLine").disabled = Boolean(data.viagem);
    $("driverDirection").disabled = Boolean(data.viagem);
    $("locationConsent").disabled = Boolean(data.viagem);
    if (data.viagem) {
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
}

function stopGps() {
    if (watcher !== null) navigator.geolocation.clearWatch(watcher);
    watcher = null;
    $("driverGpsStatus").textContent = "Compartilhamento GPS pausado.";
}

function startGps() {
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
    watcher = navigator.geolocation.watchPosition(async position => {
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
                map.setView([coords.latitude, coords.longitude], 15);
            }
            $("driverGpsStatus").textContent = `GPS compartilhado • ${new Date().toLocaleTimeString("pt-BR")} • precisão ${Math.round(coords.accuracy)} m`;
        } catch (error) {
            status("tripStatus", error.message, true);
        } finally {
            sendingPosition = false;
        }
    }, error => {
        status("tripStatus", error.code === 1 ? "Localização não autorizada. Permita o GPS e toque em Retomar compartilhamento." : "Posição indisponível. Confira o GPS e tente retomar.", true);
        $("driverGpsStatus").textContent = "Sem sinal GPS recente.";
    }, {
        enableHighAccuracy: true,
        timeout: 20000,
        maximumAge: 5000
    });
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
async function navigate() {
    let page = location.hash.slice(1) || "inicio";
    if (!titles[page] && !authScreens[page]) page = "inicio";
    clearInterval(polling);
    polling = null;
    if (page !== "horarios") $("officialFrame").removeAttribute("src");
    const auth = Boolean(authScreens[page]);
    $("auth").hidden = !auth;
    $("shell").hidden = auth;
    for (const [name, id] of Object.entries(authScreens)) $(id).hidden = page !== name;
    document.querySelectorAll(".screen").forEach(screen => screen.hidden = screen.id !== page);
    state.page = page;
    document.title = `TRANSURBAN | ${titles[page]||"Sua conta"}`;
    $("breadcrumb").textContent = titles[page] || "Conta";
    document.body.dataset.area = page === "motorista" ? "motorista" : page === "gestao" ? "gestao" : "passageiro";
    document.querySelectorAll("[data-nav],.bottom-nav a").forEach(link => link.classList.toggle("active", link.getAttribute("href") === "#" + page));
    $("sidebar").classList.remove("open");
    $("menuButton").setAttribute("aria-expanded", "false");
    window.scrollTo(0, 0);
    if (!state.ready) return;
    if (page === "motorista" && !hasRole("motorista")) {
        location.hash = "login";
        setLoginRole("motorista");
        toast("Entre com uma conta de motorista autorizada.");
        return;
    }
    if (page === "gestao" && !hasRole("gestor")) {
        location.hash = "login";
        setLoginRole("gestor");
        toast("Entre com uma conta de gestão autorizada.");
        return;
    }
    try {
        if (page === "cidades") renderCatalog();
        if (page === "favoritos") await loadFavorites();
        if (page === "dashboard") await dashboard();
        if (page === "horarios") {
            mapFor("passengerMap");
            if (state.line) {
                const line = findLine(state.line);
                if (line && ![...$("scheduleLine").options].some(option => option.value === state.line)) {
                    $("scheduleCity").value = line.ambito === "maringa" ? "Maringá" : "Sarandi";
                    fillLines("scheduleLine", $("scheduleCity").value);
                }
                $("scheduleLine").value = state.line;
                fillDirections(state.line, "scheduleDirection");
            }
            if ($("scheduleLine").value) await schedules();
            polling = setInterval(() => liveTrips().catch(error => status("scheduleStatus", error.message, true)), 10000);
        }
        if (page === "avaliacoes") {
            if (state.reviewTrip) {
                $("reviewLine").value = state.reviewTrip.linha_id;
                await loadReviewTrips();
            }
            await reviewHistory();
        }
        if (page === "motorista") await driverPanel();
        if (page === "gestao") await managerPanel();
        if (page === "conta") {
            $("accountDetails").replaceChildren();
            if (!state.user) {
                $("accountDetails").append(node("p", "Entre para acessar sua conta."));
                const link = node("a", "Entrar →", "btn primary");
                link.href = "#login";
                $("accountDetails").append(link);
            } else {
                $("accountDetails").append(node("h2", state.user.nome), node("p", state.user.email), node("p", `Acessos autorizados: ${state.user.papeis.join(", ")}`));
                const forgot = node("a", "Alterar ou recuperar minha senha", "btn quiet");
                forgot.href = "#esqueci-senha";
                $("accountDetails").append(forgot);
            }
        }
    } catch (error) {
        toast(error.message);
    }
}

function setLoginRole(role) {
    state.loginRole = role;
    document.querySelectorAll("[data-login-role]").forEach(button => button.classList.toggle("active", button.dataset.loginRole === role));
    $("loginEyebrow").textContent = {
        passageiro: "ÁREA DO PASSAGEIRO",
        motorista: "ÁREA DO MOTORISTA",
        gestor: "GESTÃO E FISCALIZAÇÃO"
    } [role];
    $("loginRoleInfo").textContent = role === "passageiro" ? "Entre para salvar suas linhas e acompanhar suas manifestações." : "O acesso exige autorização da equipe responsável pelo seu vínculo.";
}

function passwordValid(value) {
    return value.length >= 8 && /[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]/.test(value) && /[a-záàâãéêíóôõúç]/.test(value) && /\d/.test(value) && /[^\p{L}\p{N}\s]/u.test(value);
}
$("loginForm").addEventListener("submit", event => {
    event.preventDefault();
    action("loginForm", "loginStatus", async () => {
        await api("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                identificador: $("loginId").value,
                senha: $("loginPassword").value,
                tipo_acesso: state.loginRole
            })
        });
        $("loginPassword").value = "";
        status("loginStatus", "");
        await account();
        await loadFavorites();
        location.hash = {
            motorista: "motorista",
            gestor: "gestao"
        } [state.loginRole] || "inicio";
    });
});
$("signupForm").addEventListener("submit", event => {
    event.preventDefault();
    action("signupForm", "signupStatus", async () => {
        if (!passwordValid($("signupPassword").value)) throw new Error("Use pelo menos 8 caracteres, com maiúscula, minúscula, número e símbolo.");
        if ($("signupPassword").value !== $("signupConfirm").value) throw new Error("As senhas precisam ser iguais.");
        const result = await api("/auth/cadastro", {
            method: "POST",
            body: JSON.stringify({
                nome: $("signupName").value,
                email: $("signupEmail").value,
                cpf: $("signupCpf").value,
                senha: $("signupPassword").value
            })
        });
        $("signupForm").reset();
        status("signupStatus", result.mensagem);
        if (result.autenticado) {
            await account();
            location.hash = "inicio";
        }
    });
});
$("forgotForm").addEventListener("submit", event => {
    event.preventDefault();
    action("forgotForm", "forgotStatus", async () => {
        const result = await api("/auth/esqueci-senha", {
            method: "POST",
            body: JSON.stringify({
                email: $("forgotEmail").value
            })
        });
        status("forgotStatus", result.mensagem);
    });
});
$("resetForm").addEventListener("submit", event => {
    event.preventDefault();
    action("resetForm", "resetStatus", async () => {
        if (!recoveryToken) throw new Error("Abra o link recebido no seu e-mail. Se expirou, solicite um novo.");
        if (!passwordValid($("newPassword").value)) throw new Error("Use pelo menos 8 caracteres, com maiúscula, minúscula, número e símbolo.");
        if ($("newPassword").value !== $("newConfirm").value) throw new Error("As senhas precisam ser iguais.");
        const result = await api("/auth/redefinir-senha", {
            method: "POST",
            body: JSON.stringify({
                access_token: recoveryToken,
                senha: $("newPassword").value
            })
        });
        recoveryToken = null;
        $("resetForm").reset();
        status("resetStatus", result.mensagem);
    });
});
document.querySelectorAll("[data-login-role]").forEach(button => button.addEventListener("click", () => setLoginRole(button.dataset.loginRole)));
$("googleLogin").addEventListener("click", async () => {
    try {
        const config = await api("/auth/configuracao");
        if (!config.google) throw new Error("Login com Google aguardando configuração do provedor no Supabase.");
        location.href = `/auth/google?tipo_acesso=${state.loginRole}`;
    } catch (error) {
        status("loginStatus", error.message, true);
    }
});
document.querySelectorAll("[data-logout]").forEach(button => button.addEventListener("click", async () => {
    try {
        if (state.driver?.viagem) {
            if (!confirm("Encerrar o trajeto ativo e sair da conta?")) return;
            await endTrip();
        }
        await api("/auth/logout", {
            method: "POST"
        });
        stopGps();
        state.user = null;
        state.driver = null;
        state.favorites = [];
        state.reviewTrip = null;
        status("loginStatus", "");
        accountUI();
        $("reviewHistory").replaceChildren();
        $("managerQueue").replaceChildren();
        $("managerDetail").replaceChildren();
        $("responseForm").hidden = true;
        location.hash = "login";
        toast("Você saiu da conta.");
    } catch (error) {
        toast(error.message);
    }
}));
$("menuButton").addEventListener("click", () => {
    const open = $("sidebar").classList.toggle("open");
    $("menuButton").setAttribute("aria-expanded", String(open));
});
document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        $("sidebar").classList.remove("open");
        $("menuButton").setAttribute("aria-expanded", "false");
    }
});
document.querySelectorAll("[data-city]").forEach(button => button.addEventListener("click", () => {
    state.city = button.dataset.city;
    $("lineSearch").value = "";
    renderCatalog();
}));
$("homeCity").addEventListener("change", () => fillLines("homeLine", $("homeCity").value));
$("homeLine").addEventListener("change", () => {
    if ($("homeLine").value) openLine($("homeLine").value, $("homeCity").value);
});
$("homePlanner").addEventListener("submit", event => {
    event.preventDefault();
    if (!$("homeLine").value) {
        toast("Selecione uma linha.");
        return;
    }
    openLine($("homeLine").value, $("homeCity").value);
});
$("scheduleCity").addEventListener("change", () => {
    fillLines("scheduleLine", $("scheduleCity").value);
    fillDirections(null, "scheduleDirection");
    $("scheduleDirection").value = $("scheduleCity").value === "Sarandi" ? "Sarandi → Maringá" : "Maringá → Sarandi";
    state.line = null;
    $("scheduleRows").replaceChildren();
    $("busDetails").replaceChildren();
    if (markers.passengerMap) markers.passengerMap.clearLayers();
    $("gpsStatus").textContent = "Selecione uma linha.";
    $("officialCard").hidden = true;
    $("officialFrame").removeAttribute("src");
    $("scheduleDirectionField").hidden = false;
    $("scheduleDayField").hidden = false;
    $("documentScheduleCard").hidden = false;
});
$("scheduleLine").addEventListener("change", () => {
    if (!$("scheduleLine").value) {
        state.line = null;
        showOfficial(null);
        $("scheduleRows").replaceChildren();
        $("busDetails").replaceChildren(node("p", "Selecione uma linha."));
        $("scheduleSource").replaceChildren(node("p", "Selecione uma linha."));
        if (markers.passengerMap) markers.passengerMap.clearLayers();
        $("gpsStatus").textContent = "Selecione uma linha.";
        status("scheduleStatus", "Selecione uma linha para consultar.");
        return;
    }
    fillDirections($("scheduleLine").value, "scheduleDirection");
    schedules();
});
$("officialScheduleButton").addEventListener("click", () => showOfficial(findLine($("scheduleLine").value)));
$("officialPointButton").addEventListener("click", () => showOfficial(findLine($("scheduleLine").value), true));
$("lineSearch").addEventListener("input", renderCatalog);
$("driverLine").addEventListener("change", () => fillDirections($("driverLine").value, "driverDirection"));
$("scheduleForm").addEventListener("submit", event => {
    event.preventDefault();
    schedules();
});
$("favoriteCurrent").addEventListener("click", () => toggleFavorite($("scheduleLine").value));
$("reviewCity").addEventListener("change", () => {
    fillLines("reviewLine", $("reviewCity").value);
    $("reviewTrip").replaceChildren(new Option("Não vincular uma viagem", ""));
});
$("reviewLine").addEventListener("change", () => loadReviewTrips().catch(error => status("reviewStatus", error.message, true)));
$("reviewForm").addEventListener("submit", event => {
    event.preventDefault();
    action("reviewForm", "reviewStatus", async () => {
        if (!state.user) throw new Error("Entre na sua conta para enviar uma manifestação.");
        const result = await api("/mobilidade/manifestacoes", {
            method: "POST",
            body: JSON.stringify({
                linha_id: $("reviewLine").value,
                viagem_id: $("reviewTrip").value || null,
                cidade: $("reviewCity").value,
                tipo: $("reviewType").value,
                categoria: $("reviewCategory").value,
                nota_onibus: $("busRating").value ? Number($("busRating").value) : null,
                nota_motorista: $("driverRating").value ? Number($("driverRating").value) : null,
                relato: $("reviewText").value
            })
        });
        $("reviewText").value = "";
        status("reviewStatus", `${result.protocolo} · ${result.mensagem}`);
        await reviewHistory();
    });
});
$("driverProfileForm").addEventListener("submit", event => {
    event.preventDefault();
    action("driverProfileForm", "driverProfileStatus", async () => {
        await api("/mobilidade/motorista/perfil", {
            method: "PUT",
            body: JSON.stringify({
                nome_publico: $("driverName").value,
                ano_nascimento: $("driverBirth").value ? Number($("driverBirth").value) : null,
                bio: $("driverBio").value,
                exibir_perfil: $("publicDriverConsent").checked,
                modelo: $("busModel").value,
                prefixo: $("busPrefix").value
            })
        });
        status("driverProfileStatus", "Perfil e veículo salvos.");
        await driverPanel();
    });
});
$("tripForm").addEventListener("submit", event => {
    event.preventDefault();
    action("tripForm", "tripStatus", async () => {
        if (!$("locationConsent").checked) throw new Error("Autorize o compartilhamento de localização para esta viagem.");
        const trip = await api("/mobilidade/motorista/viagens", {
            method: "POST",
            body: JSON.stringify({
                linha_id: $("driverLine").value,
                sentido: $("driverDirection").value
            })
        });
        state.driver.viagem = trip;
        await driverPanel();
        status("tripStatus", "Trajeto iniciado. Autorize o GPS no navegador para compartilhar sua posição.");
        startGps();
    });
});
$("resumeGps").addEventListener("click", startGps);
$("endTrip").addEventListener("click", () => {
    if (confirm("Encerrar este trajeto e parar o compartilhamento?")) endTrip().catch(error => status("tripStatus", error.message, true));
});
$("driverDirection").addEventListener("change", () => {
    $("wazeLink").href = "https://www.waze.com/ul?q=" + encodeURIComponent($("driverDirection").value.includes("→ Sarandi") ? "Sarandi Paraná" : "Maringá Paraná");
});
$("managerStatus").addEventListener("change", renderQueue);
$("managerType").addEventListener("change", renderQueue);
$("refreshManager").addEventListener("click", () => managerPanel().catch(error => toast(error.message)));
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
async function init() {
    const fragment = new URLSearchParams(location.hash.slice(1)),
        params = new URLSearchParams(location.search);
    if (fragment.get("type") === "recovery" && fragment.get("access_token")) {
        recoveryToken = fragment.get("access_token");
        history.replaceState(null, "", "/#nova-senha");
    } else if (fragment.get("access_token")) {
        history.replaceState(null, "", "/#login");
        status("loginStatus", "E-mail confirmado. Entre com sua senha.");
    } else if (fragment.get("error_description")) {
        history.replaceState(null, "", "/#esqueci-senha");
        status("forgotStatus", "O link expirou ou já foi utilizado. Solicite outro.", true);
    }
    if (params.get("erro")) {
        status("loginStatus", "Não foi possível concluir o acesso com Google. Confira o provedor, a sessão e as permissões do perfil.", true);
        history.replaceState(null, "", "/#login");
    }
    window.addEventListener("hashchange", () => navigate().catch(error => toast(error.message)));
    accountUI();
    await navigate();
    try {
        state.catalog = await api("/mobilidade/catalogo");
        for (const [id, city] of [
                ["homeLine", $("homeCity").value],
                ["scheduleLine", $("scheduleCity").value],
                ["reviewLine", $("reviewCity").value],
                ["driverLine", "todas"]
            ]) fillLines(id, city);
        $("serviceText").textContent = "API conectada";
    } catch (error) {
        $("serviceText").textContent = "Catálogo indisponível";
        toast(error.message);
    }
    await account();
    if (state.user) await loadFavorites().catch(error => toast(error.message));
    state.ready = true;
    await navigate();
}
window.addEventListener("pagehide", stopGps);
init().catch(error => toast(error.message));
