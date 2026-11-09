"use strict";
const API = window.TRANSURBAN_API_URL || (location.port === "5500" ? "http://127.0.0.1:8091" : window.location.origin);
let mutationBusy = false;
const $ = id => document.getElementById(id);
let cityEditId = null;
let lineEditId = null;
let cityRecords = [];
let lineRecords = [];
const locale = new Intl.NumberFormat("pt-BR", {maximumFractionDigits: 2});

function setStatus(id, text, error = false) {
  const node = $(id);
  node.textContent = text;
  node.dataset.error = String(error);
}
function fmt(value) { return value == null ? "—" : locale.format(value); }
async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(API + path, {
      ...options,
      headers: {"Content-Type": "application/json", ...(options.headers || {})},
    });
  } catch {
    throw new Error("Serviço indisponível. Abra o atalho ABRIR TRANSURBAN e tente novamente.");
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    throw new Error(typeof detail === "string" ? detail : response.status === 422 ? "Confira os campos informados." : "A operação não foi concluída.");
  }
  return data;
}
async function checkService() {
  const badge = $("serviceStatus");
  try {
    const health = await api("/health/banco");
    const label = badge.querySelector("span:last-child");
    if (health.conectado) {
      badge.dataset.state = "ok";
      label.textContent = health.modo === "demo" ? "ENSAIO LOCAL · SQLite, sem Supabase" : "API e Supabase conectados";
    } else {
      badge.dataset.state = "warning";
      label.textContent = "API ativa · configure o Supabase";
    }
  } catch {
    badge.dataset.state = "error";
    badge.querySelector("span:last-child").textContent = "Banco indisponível · confira a configuração";
  }
}

function syncCitySelect() {
  const select = $("lineCity"); const previous = select.value;
  select.replaceChildren(new Option("Selecione uma cidade", ""));
  for (const city of cityRecords) select.add(new Option(city.nome, String(city.id_cidade)));
  if ([...select.options].some(option => option.value === previous)) select.value = previous;
  $("saveLine").disabled = !cityRecords.length;
  showSelectedCity();
}
function renderCities(items = cityRecords) {
  const body = $("cityRows"); body.replaceChildren();
  $("cityCount").textContent = `${items.length} ${items.length === 1 ? "cidade" : "cidades"}`;
  if (!items.length) { const tr = body.insertRow(); const td = tr.insertCell(); td.colSpan = 3; td.textContent = "Nenhuma cidade cadastrada."; syncCitySelect(); return; }
  for (const city of items) {
    const tr = body.insertRow(); tr.insertCell().textContent = String(city.id_cidade); tr.insertCell().textContent = city.nome;
    const actions = tr.insertCell();
    const edit = document.createElement("button"); edit.className = "table-action"; edit.type = "button"; edit.textContent = "Editar"; edit.dataset.action = "edit"; edit.dataset.id = city.id_cidade; edit.dataset.name = city.nome;
    const remove = document.createElement("button"); remove.className = "table-action danger"; remove.type = "button"; remove.textContent = "Excluir"; remove.dataset.action = "delete"; remove.dataset.id = city.id_cidade;
    actions.append(edit, remove);
  }
  syncCitySelect();
}
function renderLines(items = lineRecords) {
  const body = $("lineRows"); body.replaceChildren();
  $("lineCount").textContent = `${items.length} ${items.length === 1 ? "linha" : "linhas"}`;
  if (!items.length) { const tr = body.insertRow(); const td = tr.insertCell(); td.colSpan = 5; td.textContent = "Nenhuma linha cadastrada."; return; }
  for (const line of items) {
    const tr = body.insertRow();
    for (const value of [line.id_linha, line.codigo, line.nome, line.cidade]) tr.insertCell().textContent = String(value);
    const actions = tr.insertCell();
    const edit = document.createElement("button"); edit.className = "table-action"; edit.type = "button"; edit.textContent = "Editar"; edit.dataset.action = "edit"; edit.dataset.id = line.id_linha;
    const remove = document.createElement("button"); remove.className = "table-action danger"; remove.type = "button"; remove.textContent = "Excluir"; remove.dataset.action = "delete"; remove.dataset.id = line.id_linha;
    actions.append(edit, remove);
  }
}
async function refreshCities() {
  $("reloadCities").disabled = true;
  try { cityRecords = await api("/cidades"); renderCities(); }
  catch (error) { cityRecords = []; renderCities(); $("cityCount").textContent = "Banco indisponível"; setStatus("cityFeedback", error.message, true); }
  finally { $("reloadCities").disabled = false; }
}
async function refreshLines() {
  $("reloadLines").disabled = true;
  try { lineRecords = await api("/linhas"); renderLines(); }
  catch (error) { lineRecords = []; renderLines(); $("lineCount").textContent = "Tabela indisponível"; setStatus("lineFeedback", error.message, true); }
  finally { $("reloadLines").disabled = false; }
}
async function refreshAll() { await Promise.all([refreshCities(), refreshLines()]); }
function resetCityForm() {
  cityEditId = null; $("cityForm").reset(); $("formTitle").textContent = "Nova cidade";
  $("formHelp").textContent = "O identificador será gerado pelo banco."; $("saveCity").textContent = "Cadastrar cidade";
  $("cancelEdit").classList.add("hidden");
}
function resetLineForm() {
  lineEditId = null; $("lineForm").reset(); $("lineFormTitle").textContent = "Nova linha";
  $("lineFormHelp").textContent = "Escolha uma cidade cadastrada para manter o vínculo.";
  $("saveLine").textContent = "Cadastrar linha"; $("cancelLineEdit").classList.add("hidden");
}
$("cityForm").addEventListener("submit", async event => {
  event.preventDefault(); if(mutationBusy)return; mutationBusy=true; const button = $("saveCity"); button.disabled = true;
  const method = cityEditId === null ? "POST" : "PUT";
  const path = cityEditId === null ? "/cidades" : `/cidades/${cityEditId}`;
  try {
    const result = await api(path, {method, body: JSON.stringify({nome: $("cityName").value.trim()})});
    setStatus("cityFeedback", cityEditId === null ? `Cidade cadastrada com ID ${result.id_cidade}.` : `Cidade ${result.id_cidade} atualizada.`);
    resetCityForm(); await refreshAll();
  } catch (error) { setStatus("cityFeedback", error.message + " Se houve falha de rede, consulte a lista antes de repetir o envio.", true); }
  finally { button.disabled = false; mutationBusy=false; }
});
$("cityRows").addEventListener("click", async event => {
  const button = event.target.closest("button[data-action]"); if (!button) return;
  const id = Number(button.dataset.id);
  if (button.dataset.action === "edit") {
    let city;
    try {city = await api(`/cidades/${id}`);} catch(error){setStatus("cityFeedback",error.message,true);return;}
    cityEditId = id; $("cityName").value = city.nome; $("formTitle").textContent = `Editar cidade · ID ${id}`;
    $("formHelp").textContent = "Altere o nome e salve para atualizar o registro."; $("saveCity").textContent = "Salvar alterações";
    $("cancelEdit").classList.remove("hidden"); $("cityName").focus(); return;
  }
  if (!window.confirm(`Excluir a cidade ${id}? Se houver linhas vinculadas, o banco impedirá a exclusão.`)) return;
  button.disabled = true;
  try { await api(`/cidades/${id}`, {method: "DELETE"}); setStatus("cityFeedback", `Cidade ${id} excluída.`); await refreshAll(); }
  catch (error) { setStatus("cityFeedback", error.message + " Se houve falha de rede, consulte a lista antes de repetir o envio.", true); }
  finally { button.disabled = false; mutationBusy=false; }
});
$("lineForm").addEventListener("submit", async event => {
  event.preventDefault(); if(mutationBusy)return; mutationBusy=true; const button = $("saveLine"); button.disabled = true;
  const idCidade = Number($("lineCity").value);
  const payload = {id_cidade: idCidade, codigo: $("lineCode").value.trim(), nome: $("lineName").value.trim()};
  const method = lineEditId === null ? "POST" : "PUT";
  const path = lineEditId === null ? "/linhas" : `/linhas/${lineEditId}`;
  try {
    const result = await api(path, {method, body: JSON.stringify(payload)});
    setStatus("lineFeedback", lineEditId === null ? `Linha cadastrada com ID ${result.id_linha}.` : `Linha ${result.id_linha} atualizada.`);
    resetLineForm(); await refreshLines();
  } catch (error) { setStatus("lineFeedback", error.message + " Se houve falha de rede, consulte a lista antes de repetir o envio.", true); }
  finally { button.disabled = false; mutationBusy=false; }
});
$("lineRows").addEventListener("click", async event => {
  const button = event.target.closest("button[data-action]"); if (!button) return;
  const id = Number(button.dataset.id);
  if (button.dataset.action === "edit") {
    try {
      const line = await api(`/linhas/${id}`); await refreshCities(); lineEditId = id; $("lineCity").value = String(line.id_cidade);
      showSelectedCity(); $("lineCode").value = line.codigo; $("lineName").value = line.nome;
      $("lineFormTitle").textContent = `Editar linha · ID ${id}`; $("lineFormHelp").textContent = "Confira os dados e salve para atualizar.";
      $("saveLine").textContent = "Salvar alterações"; $("cancelLineEdit").classList.remove("hidden"); $("lineCode").focus();
    } catch (error) { setStatus("lineFeedback", error.message, true); }
    return;
  }
  if (!window.confirm(`Excluir a linha ${id}? O banco pode impedir a exclusão se ela estiver relacionada a registros.`)) return;
  button.disabled = true;
  try { await api(`/linhas/${id}`, {method: "DELETE"}); setStatus("lineFeedback", `Linha ${id} excluída.`); await refreshLines(); }
  catch (error) { setStatus("lineFeedback", error.message + " Se houve falha de rede, consulte a lista antes de repetir o envio.", true); }
  finally { button.disabled = false; mutationBusy=false; }
});
$("lookupForm").addEventListener("submit", async event => {
  event.preventDefault();
  try { const city = await api(`/cidades/${Number($("lookupId").value)}`); setStatus("lookupFeedback", `Encontrada: ${city.nome} (ID ${city.id_cidade}).`); }
  catch (error) { setStatus("lookupFeedback", error.message, true); }
});
$("lookupLineForm").addEventListener("submit", async event => {
  event.preventDefault();
  try { const line = await api(`/linhas/${Number($("lookupLineId").value)}`); setStatus("lookupLineFeedback", `Encontrada: ${line.codigo} · ${line.nome} — ${line.cidade} (ID ${line.id_linha}).`); }
  catch (error) { setStatus("lookupLineFeedback", error.message, true); }
});
$("cancelEdit").addEventListener("click", resetCityForm);
$("clearCity").addEventListener("click", () => { resetCityForm(); setStatus("cityFeedback", "Campos limpos."); });
$("cancelLineEdit").addEventListener("click", resetLineForm);
$("reloadCities").addEventListener("click", refreshCities);
$("reloadLines").addEventListener("click", refreshLines);
function showSelectedCity(){
 const s=$("lineCity"); $("selectedCity").textContent=s.value ? `Cidade: ${s.selectedOptions[0].textContent}. ID enviado: ${s.value}.` : "Escolha a cidade pelo nome. O vínculo será gravado pelo ID.";
}
$("lineCity").addEventListener("change",showSelectedCity);
checkService(); refreshAll();




