"use strict";
(() => {
    const $ = id => document.getElementById(id),
        role = document.body.dataset.area || "passageiro";
    let map = null,
        eventsLayer = null,
        meMarker = null,
        accuracyCircle = null,
        selectedMarker = null,
        activeUser = null,
        reportsLayer = null,
        fleetLayer = null,
        updateTimer = null,
        updating = false;
    const text = (tag, value, cls = "") => {
        const e = document.createElement(tag);
        e.textContent = value;
        e.className = cls;
        return e;
    };
    const feedback = (id, message, error = false) => {
        if ($(id)) {
            $(id).textContent = message;
            $(id).classList.toggle("error", error);
        }
    };
    const request = (url, options = {}) => api(url, options);

    function options(city, id, optional = true) {
        if (!$(id)) return;
        $(id).replaceChildren(...(optional ? [new Option("Sem linha específica", "")] : []), ...(state.catalog?.linhas || []).filter(l => l.cidades.includes(city)).map(l => new Option(`${l.codigo} · ${l.nome}`, l.id)));
    }

    function setupMap() {
        if (map || !$("opsMap") || !window.L || !$("opsMap").getClientRects().length) return;
        map = L.map("opsMap").setView([-23.432, -51.9], 12);
        window.TransurbanRegion?.apply(map);
        L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
        }).addTo(map);
        eventsLayer = L.layerGroup().addTo(map);
        map.on("click", event => {
            const lat = event.latlng.lat.toFixed(6),
                lon = event.latlng.lng.toFixed(6);
            const prefix = role === "gestao" ? "alert" : "support";
            if ($(prefix + "Lat")) $(prefix + "Lat").value = lat;
            if ($(prefix + "Lon")) $(prefix + "Lon").value = lon;
            if (selectedMarker) selectedMarker.remove();
            selectedMarker = L.marker(event.latlng, {
                icon: L.divIcon({
                    className: "",
                    html: '<div style="width:18px;height:18px;border:3px solid white;border-radius:50%;background:#254b68;box-shadow:0 0 0 2px #254b68"></div>',
                    iconSize: [18, 18]
                })
            }).addTo(map).bindPopup(text("span", "Local selecionado para o formulário")).openPopup();
        });
        window.TransurbanLocation?.attach(map, {buttonId: "locateMe", statusId: "locationFeedback"});
    }

    function paintReceivedReports(calls) {
        if (role !== "gestao" || !activeUser?.papeis?.includes("gestor") || !map) return;
        if (!reportsLayer) reportsLayer = L.layerGroup().addTo(map);
        reportsLayer.clearLayers();
        for (const call of calls) {
            if (call.latitude == null || call.longitude == null || call.status === "encerrado") continue;
            const popup = text("div", "");
            popup.append(text("strong", call.assunto), text("p", `${call.cidade} · ${call.categoria}`), text("small", "Relato recebido para análise. Visível somente para a gestão."));
            const open = text("button", "Analisar relato", "btn quiet");
            open.type = "button";
            open.onclick = () => {
                location.hash = "relatosGestao";
                window.TransurbanManagement?.show("relatosGestao");
                const card = $("relato-" + call.id);
                card?.scrollIntoView({block:"center",behavior:"smooth"});
                card?.focus({preventScroll:true});
            };
            popup.append(open);
            L.circleMarker([call.latitude, call.longitude], {radius:9,color:"white",weight:3,fillColor:"#62666b",fillOpacity:1}).bindPopup(popup).addTo(reportsLayer);
        }
    }

    async function loadAlerts() {
        setupMap();
        if (role === "gestao") paintReceivedReports(state.calls || []);
        const alerts = await request("/atendimento/alertas");
        eventsLayer?.clearLayers();
        $("opsAlerts")?.replaceChildren();
        const colors = {
            vermelho: "#b94035",
            amarelo: "#d09c20",
            verde: "#2f8a5b"
        };
        for (const a of alerts) {
            const card = text("article", "", "record");
            card.append(text("strong", a.titulo), text("p", a.orientacao), text("small", `${a.cidade} · ${a.nivel} · confirmado em ${dateTime(a.criado_em)} · válido até ${dateTime(a.expira_em)}`));
            $("opsAlerts")?.append(card);
            if (eventsLayer) {
                const popup = text("div", "");
                popup.append(text("strong", a.titulo), text("p", a.orientacao), text("small", `Atualização manual da gestão • ${dateTime(a.criado_em)}`));
                L.circleMarker([a.latitude, a.longitude], {
                    radius: 11,
                    color: "white",
                    weight: 3,
                    fillColor: colors[a.nivel],
                    fillOpacity: 1
                }).bindPopup(popup).addTo(eventsLayer);
            }
            if (role === "gestao") {
                const b = text("button", "Retirar ocorrência", "btn quiet");
                b.type = "button";
                b.onclick = async () => {
                    try {
                        await request(`/atendimento/gestao/alertas/${a.id}`, {
                            method: "DELETE"
                        });
                        await loadAlerts();
                    } catch (e) {
                        toast(e.message);
                    }
                };
                card.append(b);
            }
        }
        if (!alerts.length) $("opsAlerts")?.append(text("p", "Nenhuma ocorrência confirmada publicada no momento. Isso não significa que todas as vias estejam livres.", "empty"));
    }
    async function history() {
        if (!$("supportHistory")) return;
        $("supportHistory").replaceChildren();
        if (!activeUser) {
            $("supportHistory").append(text("p", "Entre na sua conta para enviar e acompanhar chamados."));
            return;
        }
        const calls = await request("/atendimento/meus-chamados");
        for (const c of calls) {
            const card = text("article", "", "record");
            card.append(text("strong", `SUP-${String(c.numero).padStart(6,"0")} · ${c.assunto}`), text("p", c.mensagem), text("small", `${c.status.replaceAll("_"," ")} · ${dateTime(c.criado_em)}`));
            if (c.resposta) card.append(text("p", `Resposta: ${c.resposta}`));
            $("supportHistory").append(card);
        }
        if (!calls.length) $("supportHistory").append(text("p", "Você ainda não enviou relatos."));
    }

    function managementForms() {
        if (!$("managementOperations")) return;
        $("managementOperations").innerHTML = `<form id="alertForm" class="card" style="margin-top:20px"><h2>Publicar orientação aos usuários</h2><p>Confirme a situação antes de publicar. Clique no mapa para marcar o local. O alerta informa uma condição; não altera automaticamente uma rota oficial.</p><div class="two-fields"><div><label for="alertCity">Cidade</label><select id="alertCity"><option>Maringá</option><option>Sarandi</option></select></div><div><label for="alertLine">Linha (opcional)</label><select id="alertLine"></select></div></div><label for="alertLevel">Situação confirmada</label><select id="alertLevel"><option value="vermelho">Vermelho — bloqueio, obra ou desvio</option><option value="amarelo">Amarelo — atenção / lentidão</option><option value="verde">Verde — condição tranquila informada</option></select><label for="alertTitle">O que aconteceu?</label><input id="alertTitle" required minlength="5" maxlength="120"><label for="alertAdvice">Orientação para passageiros e motoristas</label><textarea id="alertAdvice" required minlength="10" maxlength="1000"></textarea><details><summary>Local marcado no mapa</summary><div class="two-fields"><div><label for="alertLat">Latitude</label><input type="number" step="any" id="alertLat" required min="-90" max="90"></div><div><label for="alertLon">Longitude</label><input type="number" step="any" id="alertLon" required min="-180" max="180"></div></div></details><label for="alertValidity">Por quantas horas este aviso fica visível?</label><input type="number" id="alertValidity" value="2" min="1" max="24" required><button class="btn primary wide">Publicar ocorrência confirmada</button><p id="alertStatus" class="status" role="status"></p></form>`;
        $("professionalApprovals").innerHTML = `<section class="card" id="approvalSection" hidden><h2>Contas profissionais</h2><p>Analise os pedidos antes de autorizar motorista ou gestão.</p><div id="approvalQueue" class="stack"></div></section>`;
        options("Maringá", "alertLine");
        $("alertCity").onchange = () => options($("alertCity").value, "alertLine");
        $("alertForm").onsubmit = async e => {
            e.preventDefault();
            const b = $("alertForm").querySelector('button');
            b.disabled = true;
            try {
                await request("/atendimento/gestao/alertas", {
                    method: "POST",
                    body: JSON.stringify({
                        cidade: $("alertCity").value,
                        linha_id: $("alertLine").value || null,
                        nivel: $("alertLevel").value,
                        titulo: $("alertTitle").value,
                        orientacao: $("alertAdvice").value,
                        latitude: Number($("alertLat").value),
                        longitude: Number($("alertLon").value),
                        validade_horas: Number($("alertValidity").value)
                    })
                });
                feedback("alertStatus", "Ocorrência publicada com a validade informada.");
                await loadAlerts();
            } catch (error) {
                feedback("alertStatus", error.message, true);
            } finally {
                b.disabled = false;
            }
        };
        $("refreshSupport").onclick = () => managementCalls().catch(e => toast(e.message));
    }
    async function managementCalls({background = false} = {}) {
        if (background && $("supportQueue")?.contains(document.activeElement) && document.activeElement.matches("input,textarea,select")) return;
        if (!$("supportQueue")) return;
        const received = await request("/atendimento/gestao/chamados");
        state.calls = received;
        paintReceivedReports(received);
        window.dispatchEvent(new Event("transurban:operation-update"));
        const calls = received.filter(c => (!$("callCityFilter").value || c.cidade === $("callCityFilter").value) && (!$("callStateFilter").value || c.status === $("callStateFilter").value));
        feedback("receivedCallsStatus", `${calls.length} relato(s) nesta seleção. Atualização automática a cada 15 segundos.`);
        $("supportQueue").replaceChildren();
        for (const c of calls) {
            const card = text("article", "", "record");
            card.id = "relato-" + c.id;
            card.tabIndex = -1;
            card.append(text("h3", `SUP-${String(c.numero).padStart(6,"0")} · ${c.assunto}`), text("p", `${c.perfil} · ${c.cidade} · ${c.categoria}`), text("p", c.mensagem), text("small", `${c.status} · ${dateTime(c.criado_em)}`));
            if (c.latitude != null) {
                const locate = text("button", "Ver local informado", "btn quiet");
                locate.type = "button";
                locate.onclick = () => {
                    location.hash = "operacaoGestao";
                    window.TransurbanManagement?.show("operacaoGestao");
                    setupMap();
                    paintReceivedReports(state.calls || []);
                    if (map) {
                        if (selectedMarker) selectedMarker.remove();
                        const popup = text("div", "");
                        popup.append(text("strong", "Local relatado • " + c.assunto), text("p", "Informação enviada pelo solicitante para análise. Este marcador é privado da gestão e não é um alerta confirmado."));
                        selectedMarker = L.circleMarker([c.latitude, c.longitude], {radius: 10, color: "#fff", weight: 3, fillColor: "#62666b", fillOpacity: 1}).addTo(map).bindPopup(popup).openPopup();
                        map.setView([c.latitude, c.longitude], 16);
                        map.invalidateSize();
                        $("alertLat").value = c.latitude;
                        $("alertLon").value = c.longitude;
                        $("alertTitle").value = c.assunto;
                        $("alertCity").value = c.cidade;
                        options(c.cidade, "alertLine");
                        $("alertLine").value = c.linha_id || "";
                    }
                    toast("Local informado no chamado. A posição não foi publicada como ocorrência.");
                };
                card.append(locate);
            }
            if (c.resposta) card.append(text("p", c.resposta));
            if (c.status !== "encerrado") {
                const form = text("form", "");
                const label = text("label", "Resposta ao solicitante"),
                    answer = document.createElement("textarea"),
                    statusSelect = document.createElement("select"),
                    button = text("button", "Salvar atendimento", "btn primary");
                answer.required = true;
                answer.minLength = 10;
                answer.maxLength = 2000;
                label.append(answer);
                for (const [value, name] of [
                        ["em_analise", "Em análise"],
                        ["respondido", "Respondido"],
                        ["encerrado", "Encerrado"]
                    ]) statusSelect.add(new Option(name, value));
                form.append(label, statusSelect, button);
                form.onsubmit = async e => {
                    e.preventDefault();
                    button.disabled = true;
                    try {
                        await request(`/atendimento/gestao/chamados/${c.id}`, {
                            method: "PUT",
                            body: JSON.stringify({
                                status: statusSelect.value,
                                resposta: answer.value
                            })
                        });
                        await managementCalls();
                    } catch (error) {
                        toast(error.message);
                        button.disabled = false;
                    }
                };
                card.append(form);
            }
            $("supportQueue").append(card);
        }
        if (!calls.length) $("supportQueue").append(text("p", "Nenhum relato recebido na sua área."));
    }
    async function approvals({background = false} = {}) {
        if (background && $("approvalQueue")?.contains(document.activeElement) && document.activeElement.matches("input,textarea,select")) return;
        if (!activeUser?.administrador || !$("approvalSection")) return;
        $("approvalSection").hidden = false;
        const rows = await request("/atendimento/gestao/pedidos-acesso");
        $("approvalQueue").replaceChildren();
        for (const p of rows) {
            const card = text("article", "", "record");
            card.append(text("h3", `${p.solicitante.nome||"Conta"} · ${p.papel}`), text("p", p.solicitante.email || ""), text("p", p.justificativa), text("small", p.status));
            if (p.status === "pendente") {
                const form = document.createElement("form"),
                    scope = document.createElement("select"),
                    reason = document.createElement("textarea"),
                    approve = text("button", "Aprovar vínculo", "btn primary"),
                    reject = text("button", "Recusar pedido", "btn quiet");
                scope.setAttribute("aria-label", "Escopo autorizado");
                for (const [v, n] of [
                        ["maringa", "Maringá"],
                        ["sarandi", "Sarandi"],
                        ["metropolitano", "Metropolitano"],
                        ["todos", "Todos os escopos"]
                    ]) scope.add(new Option(n, v));
                reason.required = true;
                reason.minLength = 10;
                reason.maxLength = 1000;
                reason.setAttribute("aria-label", "Justificativa da decisão");
                reason.placeholder = "Registre a conferência e a justificativa da decisão.";
                reject.type = "button";
                const decide = async value => {
                    if (!form.reportValidity()) return;
                    approve.disabled = true;
                    reject.disabled = true;
                    try {
                        await request(`/atendimento/gestao/pedidos-acesso/${p.id}`, {
                            method: "PUT",
                            body: JSON.stringify({
                                aprovar: value,
                                escopo: scope.value,
                                decisao: reason.value
                            })
                        });
                        await approvals();
                        toast("Decisão registrada.");
                    } catch (e) {
                        toast(e.message);
                        approve.disabled = false;
                        reject.disabled = false;
                    }
                };
                form.onsubmit = e => {
                    e.preventDefault();
                    decide(true);
                };
                reject.onclick = () => decide(false);
                form.append(scope, reason, approve, reject);
                card.append(form);
            }
            $("approvalQueue").append(card);
        }
        if (!rows.length) $("approvalQueue").append(text("p", "Nenhum pedido de vínculo recebido."));
    }
    async function loadFleet() {
        if (role !== "gestao" || !activeUser?.papeis?.includes("gestor")) return;
        const trips = await request("/mobilidade/gestao/viagens");
        state.fleet = trips;
        window.dispatchEvent(new Event("transurban:operation-update"));
        if (map && !fleetLayer) fleetLayer = L.layerGroup().addTo(map);
        fleetLayer?.clearLayers();
        $("fleetList")?.replaceChildren();
        let recent = 0;
        for (const trip of trips) {
            const line = state.catalog?.linhas.find(item => item.id === trip.linha_id);
            const title = `Ônibus ${trip.prefixo} · ${trip.modelo} · ${line?.nome || trip.linha_id}`;
            const card = text("article", "", "record");
            card.append(text("strong", title), text("p", `Motorista: ${trip.motorista?.nome || "Conta autorizada"} · ${trip.sentido}`), text("small", trip.posicao ? `${trip.posicao.recente ? "Sinal recente" : "Sinal desatualizado"} · ${dateTime(trip.posicao.registrada_em)} · precisão ${Math.round(trip.posicao.precisao_m)} m` : "Aguardando GPS do motorista."));
            $("fleetList")?.append(card);
            if (trip.posicao?.recente) recent++;
            if (!trip.posicao || !fleetLayer) continue;
            const popup = text("div", "");
            popup.append(text("strong", title), text("p", trip.sentido), text("small", trip.posicao.recente ? "Posição compartilhada pelo motorista" : "Última posição recebida; sem sinal recente"));
            L.marker([trip.posicao.latitude, trip.posicao.longitude], {icon: L.divIcon({className: "", html: `<span class="bus-marker ${trip.posicao.recente ? "" : "stale"}">▣</span>`, iconSize: [36,36], iconAnchor: [18,18]})}).bindPopup(popup).addTo(fleetLayer);
        }
        feedback("fleetStatus", `${trips.length} viagem(ns) ativa(s) · ${recent} ônibus com sinal recente. Atualização automática a cada 15 segundos.`);
    }
    function startUpdates() {
        if (updateTimer) return;
        updateTimer = setInterval(async () => {
            if (document.hidden || updating || (role !== "gestao" && !$("opsMap")?.getClientRects().length)) return;
            if (role === "gestao" && !activeUser?.papeis?.includes("gestor")) return;
            updating = true;
            try {
                const tasks = [loadAlerts()];
                if (role === "gestao") {
                    tasks.push(managementCalls({background:true}), loadFleet());
                    if (location.hash === "#autorizacoesGestao") tasks.push(approvals({background:true}));
                } else if (activeUser && (role === "motorista" || location.hash === "#suporte")) {
                    if (!$("supportHistory")?.contains(document.activeElement)) tasks.push(history());
                }
                const results = await Promise.allSettled(tasks);
                const failed = results.some(r => r.status === "rejected");
                const message = failed ? "Parte da operação está temporariamente indisponível. Nova tentativa automática em 15 segundos." : "Última consulta às " + new Date().toLocaleTimeString("pt-BR") + ". Atualização automática a cada 15 segundos.";
                feedback("opsSyncStatus", message, failed);
                feedback("operationFeedback", message, failed);
            } catch (error) { feedback("opsSyncStatus", "A atualização está temporariamente indisponível. Tentaremos novamente automaticamente.", true); }
            finally {updating = false;}
        }, 15000);
    }
    window.addEventListener("transurban:logout", () => {
        activeUser = null;
        clearInterval(updateTimer);
        updateTimer = null;
        fleetLayer?.clearLayers();
        reportsLayer?.clearLayers();
        $("supportHistory")?.replaceChildren();
        $("supportQueue")?.replaceChildren();
        $("approvalQueue")?.replaceChildren();
        $("fleetList")?.replaceChildren();
    });
    window.addEventListener("pagehide", () => {clearInterval(updateTimer); updateTimer = null;});
    window.addEventListener("pageshow", event => {if (event.persisted) refresh().catch(() => {});});
    async function refresh() {
        try {
            activeUser = state.user || await request("/auth/me", {}, false);
        } catch {
            activeUser = null,
        fleetLayer = null,
        updateTimer = null,
        updating = false;
        }
        if (!state.catalog) try {
            state.catalog = await request("/mobilidade/catalogo");
        } catch {}
        if ($("supportLine")) options($("supportCity").value, "supportLine");
        if (role === "gestao" && activeUser?.papeis?.includes("gestor")) {
            if (!$("alertForm")) managementForms();
        }
        startUpdates();
        const tasks = [loadAlerts(), history(), loadFleet()];
        if (role === "gestao" && activeUser?.papeis?.includes("gestor")) tasks.push(managementCalls(), approvals());
        const results = await Promise.allSettled(tasks);
        const failed = results.some(r => r.status === "rejected");
        feedback("operationFeedback", failed ? "Alguns dados não puderam ser consultados. O sistema tentará novamente automaticamente." : "Operação sincronizada. Atualização automática a cada 15 segundos.", failed);
        setTimeout(() => map?.invalidateSize(), 0);
    }
    document.querySelectorAll('.requestAccessForm').forEach(form => form.onsubmit = async e => {
        e.preventDefault();
        const target = form.querySelector('.requestStatus'),
            button = form.querySelector('button');
        button.disabled = true;
        try {
            await request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({
                    identificador: form.elements.identificador.value,
                    senha: form.elements.senha.value,
                    tipo_acesso: 'passageiro'
                })
            });
            form.elements.senha.value = '';
            const result = await request('/atendimento/pedidos-acesso', {
                method: 'POST',
                body: JSON.stringify({
                    papel: form.dataset.papel,
                    justificativa: form.elements.justificativa.value
                })
            });
            target.textContent = result.mensagem;
        } catch (error) {
            target.textContent = error.message;
        } finally {
            button.disabled = false;
        }
    });
    for (const id of ["callCityFilter", "callStateFilter"]) $(id)?.addEventListener("change", () => managementCalls().catch(e => toast(e.message)));
    $("supportCity")?.addEventListener("change", () => options($("supportCity").value, "supportLine"));
    $("supportForm")?.addEventListener("submit", async e => {
        e.preventDefault();
        const b = $("supportForm").querySelector('button');
        b.disabled = true;
        try {
            if (!activeUser) throw new Error("Entre na sua conta para enviar um chamado.");
            const result = await request(`/atendimento/${role==="motorista"?"motorista":"passageiro"}/chamados`, {
                method: "POST",
                body: JSON.stringify({
                    cidade: $("supportCity").value,
                    linha_id: $("supportLine").value || null,
                    categoria: $("supportCategory").value,
                    assunto: $("supportSubject").value,
                    mensagem: $("supportMessage").value,
                    latitude: $("supportLat").value ? Number($("supportLat").value) : null,
                    longitude: $("supportLon").value ? Number($("supportLon").value) : null
                })
            });
            feedback("supportStatus", `${result.protocolo} · Relato recebido pela gestão responsável. Acompanhe a análise e a resposta aqui.`);
            $("supportMessage").value = "";
            await history();
        } catch (error) {
            feedback("supportStatus", error.message, true);
        } finally {
            b.disabled = false;
        }
    });
    window.addEventListener("hashchange", () => {
        if (role === "gestao" && activeUser?.papeis?.includes("gestor")) {
            setupMap();
            paintReceivedReports(state.calls || []);
        }
        setTimeout(() => map?.invalidateSize(), 0);
        if (location.hash === "#suporte" || (role === "gestao" && location.hash === "#operacaoGestao")) refresh().catch(e => feedback("supportStatus", e.message, true));
    });
    window.TransurbanOps = {
        refresh
    };
    document.addEventListener("DOMContentLoaded", () => refresh().catch(e => {
        feedback("locationFeedback", "O mapa de ocorrências está temporariamente indisponível.", true);
        feedback("supportStatus", e.message, true);
    }));
})();
