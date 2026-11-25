"use strict";
// Enquadramento de navegação da área urbana; não representa divisas municipais.
(() => {
    const bounds = [[-23.51, -52.03], [-23.34, -51.79]];
    const contains = (lat, lon) => Number.isFinite(lat) && Number.isFinite(lon) && lat >= bounds[0][0] && lat <= bounds[1][0] && lon >= bounds[0][1] && lon <= bounds[1][1];
    function apply(map) {
        map.setMaxBounds(bounds);
        map.setMinZoom(10);
        map.setMaxZoom(19);
        map.options.maxBoundsViscosity = 1;
        map.options.zoomSnap = 0.25;
        map.fitBounds(bounds, {padding:[12,12], maxZoom:13});
        const bar = document.createElement("div");
        bar.className = "region-toolbar";
        const title = document.createElement("span");
        title.textContent = "Maringá e Sarandi";
        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn quiet";
        button.textContent = "Ver região";
        button.addEventListener("click", () => map.fitBounds(bounds, {padding:[12,12], maxZoom:13}));
        bar.append(title, button);
        map.getContainer().before(bar);
    }
    window.TransurbanRegion = {apply, contains};
})();
