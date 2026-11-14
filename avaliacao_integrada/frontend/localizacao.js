"use strict";
// Localização do visitante: permanece no navegador e não é enviada à API.
(() => {
    const controls = new Map();
    function attach(map, {buttonId, statusId, maxZoom = 17}) {
        if (controls.has(buttonId)) return controls.get(buttonId);
        const button = document.getElementById(buttonId), status = document.getElementById(statusId);
        if (!map || !button || !status) return null;
        const originalText = button.textContent.trim();
        let watch = null, marker = null, circle = null, first = true, generation = 0;
        const message = (value, error = false) => {
            status.textContent = value;
            status.classList.toggle("error", error);
        };
        function stop(note = "Localização pausada. Toque em Minha localização para retomar.") {
            generation++;
            if (watch !== null) navigator.geolocation.clearWatch(watch);
            watch = null;
            button.textContent = originalText;
            button.setAttribute("aria-pressed", "false");
            if (marker) marker.remove();
            if (circle) circle.remove();
            marker = circle = null;
            message(note);
        }
        function start() {
            if (!navigator.geolocation) return message("Este navegador não oferece localização.", true);
            first = true;
            const current = ++generation;
            button.textContent = "Parar localização";
            button.setAttribute("aria-pressed", "true");
            message("Permita a localização no navegador. Aguardando a posição do aparelho…");
            watch = navigator.geolocation.watchPosition(position => {
                if (generation !== current) return;
                const {latitude, longitude, accuracy} = position.coords;
                if (![latitude, longitude, accuracy].every(Number.isFinite) || accuracy < 0 || Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
                    message("O aparelho não forneceu uma posição válida. Aguardando novo sinal…", true);
                    return;
                }
                if (!marker) {
                    marker = L.circleMarker([latitude, longitude], {radius: 8, color: "#fff", weight: 3, fillColor: "#286ca1", fillOpacity: 1}).addTo(map);
                    circle = L.circle([latitude, longitude], {radius: accuracy, color: "#286ca1", weight: 1, fillOpacity: .08}).addTo(map);
                } else {
                    marker.setLatLng([latitude, longitude]);
                    circle.setLatLng([latitude, longitude]).setRadius(accuracy);
                }
                const popup = document.createElement("span");
                popup.textContent = `Sua localização • precisão informada: ${Math.round(accuracy)} m`;
                marker.bindPopup(popup);
                if (first) {
                    map.setView([latitude, longitude], accuracy > 300 ? 14 : maxZoom);
                    first = false;
                } else if (!map.getBounds().contains([latitude, longitude])) map.panTo([latitude, longitude]);
                const time = new Date(position.timestamp || Date.now()).toLocaleTimeString("pt-BR");
                message(`Sua localização • atualização ${time} • margem informada ${Math.round(accuracy)} m. O círculo mostra essa margem. Atualização automática enquanto esta página estiver visível.`);
            }, error => {
                if (generation !== current) return;
                if (error.code === 1) stop("Localização não autorizada. Ative a permissão nas configurações do navegador e tente novamente.");
                else message("Sinal indisponível ou demorado. Aguardando nova posição; você pode parar e tentar novamente.", true);
            }, {enableHighAccuracy: true, timeout: 20000, maximumAge: 3000});
        }
        button.addEventListener("click", () => watch === null ? start() : stop());
        button.setAttribute("aria-pressed", "false");
        const control = {stop, visible: () => !!map.getContainer().getClientRects().length, get active() {return watch !== null;}};
        controls.set(buttonId, control);
        return control;
    }
    function stopAll(note) {for (const control of controls.values()) if (control.active) control.stop(note);}
    document.addEventListener("visibilitychange", () => {if (document.hidden) stopAll("Localização pausada porque a página ficou em segundo plano. Toque em Minha localização para retomar.");});
    window.addEventListener("pagehide", () => stopAll());
    window.addEventListener("hashchange", () => {for (const control of controls.values()) if (control.active && !control.visible()) control.stop("Localização pausada ao sair do mapa.");});
    window.addEventListener("transurban:logout", () => stopAll("Você saiu da conta. Localização interrompida."));
    window.TransurbanLocation = {attach, stopAll};
})();
