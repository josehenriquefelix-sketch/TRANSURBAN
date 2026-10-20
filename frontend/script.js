"use strict";
const byId = id => document.getElementById(id);
let currentCities = [];
let currentLines = [];
let dataReady = false;
let savingLine = false;
const cityFields = [["id_cidade", "ID"], ["nome", "Cidade"]];
const lineFields = [["id_linha", "ID"], ["codigo", "Código"], ["nome", "Linha"], ["cidade", "Cidade"]];
function feedback(id, message, error = false) {
  const node = byId(id); node.textContent = message; node.dataset.error = String(error);
}
async function request(path, body) {
  const options = body === undefined ? {} : {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)};
  let response;
  try { response = await fetch(path, options); }
  catch { throw new Error("Não foi possível conectar à API. Confira se o servidor está ativo."); }
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = result.detail;
    throw new Error(typeof detail === "string" ? detail : response.status === 422 ? "Dados inválidos. Confira os campos obrigatórios e seus limites." : "Não foi possível concluir a operação.");
  }
  return result;
}
function renderRows(target, records, fields, emptyMessage = "Nenhum registro cadastrado.") {
  const rows = byId(target); rows.replaceChildren();
  if (!records.length) {
    const row = rows.insertRow(); const cell = row.insertCell();
    cell.colSpan = fields.length; cell.textContent = emptyMessage; return;
  }
  for (const record of records) {
    const row = rows.insertRow();
    for (const [field, label] of fields) {
      const cell = row.insertCell(); cell.dataset.label = label;
      cell.textContent = String(record[field]);
    }
  }
}
function normalize(value) {
  return String(value).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR").trim();
}
function filterLines() {
  const term = normalize(byId("lineSearch").value);
  const city = byId("cityFilter").value;
  const filtered = currentLines.filter(line => (!city || line.cidade === city) && (!term || [line.codigo, line.nome, line.cidade].some(value => normalize(value).includes(term))));
  renderRows("lineRows", filtered, lineFields, currentLines.length ? "Nenhuma linha encontrada. Ajuste ou limpe os filtros." : "Nenhuma linha cadastrada.");
  byId("lineResultCount").textContent = dataReady ? filtered.length + " de " + currentLines.length + (currentLines.length === 1 ? " linha" : " linhas") : "";
}
function fillCities(select, cities, placeholder, useName = false) {
  const previous = select.value;
  select.replaceChildren(new Option(placeholder, ""));
  for (const city of cities) select.add(new Option(city.nome, useName ? city.nome : String(city.id_cidade)));
  if ([...select.options].some(option => option.value === previous)) select.value = previous;
}
function updateControls() {
  byId("saveLine").disabled = savingLine || !dataReady || currentCities.length === 0;
  for (const id of ["lineSearch", "cityFilter", "clearFilters"]) byId(id).disabled = !dataReady;
}
async function refresh() {
  byId("refresh").disabled = true;
  byId("consultas").setAttribute("aria-busy", "true");
  feedback("queryFeedback", "Consultando registros…");
  try {
    const [cities, lines] = await Promise.all([request("/cidades"), request("/linhas")]);
    currentCities = cities; currentLines = lines; dataReady = true;
    renderRows("cityRows", cities, cityFields);
    byId("cityCount").textContent = cities.length;
    byId("lineCount").textContent = lines.length;
    fillCities(byId("lineCity"), cities, "Selecione uma cidade");
    fillCities(byId("cityFilter"), cities, "Todas as cidades", true);
    filterLines(); updateControls();
    feedback("connection", "Banco conectado");
    feedback("queryFeedback", "Registros atualizados. Use a busca e os filtros para consultar as linhas.");
    return true;
  } catch (error) {
    dataReady = false; currentCities = []; currentLines = [];
    feedback("connection", "Conexão pendente", true);
    feedback("queryFeedback", error.message, true);
    byId("cityCount").textContent = "—"; byId("lineCount").textContent = "—";
    byId("lineResultCount").textContent = "";
    renderRows("cityRows", [], cityFields, "Consulta indisponível. Tente atualizar.");
    renderRows("lineRows", [], lineFields, "Consulta indisponível. Tente atualizar.");
    fillCities(byId("lineCity"), [], "Consulta indisponível");
    fillCities(byId("cityFilter"), [], "Todas as cidades", true);
    updateControls(); return false;
  } finally {
    byId("refresh").disabled = false;
    byId("consultas").setAttribute("aria-busy", "false");
  }
}
byId("cityForm").addEventListener("submit", async event => {
  event.preventDefault(); const button = event.target.querySelector("button"); button.disabled = true;
  try {
    const city = await request("/cidades", {nome:byId("cityName").value.trim()});
    event.target.reset();
    const updated = await refresh();
    if (updated) byId("lineCity").value = String(city.id_cidade);
    feedback("cityFeedback", "Cidade cadastrada. ID: " + city.id_cidade + (updated ? ". Agora você pode associar uma linha." : ". Atualize a consulta quando a conexão voltar."));
  } catch (error) { feedback("cityFeedback", error.message, true); }
  finally { button.disabled = false; }
});
byId("lineForm").addEventListener("submit", async event => {
  event.preventDefault(); savingLine = true; updateControls();
  try {
    const line = await request("/linhas", {id_cidade:Number(byId("lineCity").value),codigo:byId("lineCode").value.trim(),nome:byId("lineName").value.trim()});
    event.target.reset(); const updated = await refresh();
    feedback("lineFeedback", "Linha cadastrada. ID: " + line.id_linha + ". Cidade: " + line.cidade + (updated ? "." : ". Atualize a consulta quando a conexão voltar."));
  } catch (error) { feedback("lineFeedback", error.message, true); }
  finally { savingLine = false; updateControls(); }
});
byId("refresh").addEventListener("click", refresh);
byId("lineSearch").addEventListener("input", filterLines);
byId("cityFilter").addEventListener("change", filterLines);
byId("clearFilters").addEventListener("click", () => {
  byId("lineSearch").value = ""; byId("cityFilter").value = "";
  filterLines(); byId("lineSearch").focus();
});
refresh();
