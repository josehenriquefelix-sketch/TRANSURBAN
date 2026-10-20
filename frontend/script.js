"use strict";
const byId = id => document.getElementById(id);
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
function renderRows(target, records, fields) {
  const rows = byId(target); rows.replaceChildren();
  if (!records.length) {
    const row = rows.insertRow(); const cell = row.insertCell();
    cell.colSpan = fields.length; cell.textContent = "Nenhum registro cadastrado."; return;
  }
  for (const record of records) {
    const row = rows.insertRow();
    for (const field of fields) row.insertCell().textContent = String(record[field]);
  }
}
async function refresh() {
  byId("refresh").disabled = true;
  feedback("queryFeedback", "Consultando…");
  try {
    const [cities, lines] = await Promise.all([request("/cidades"), request("/linhas")]);
    renderRows("cityRows", cities, ["id_cidade","nome"]);
    renderRows("lineRows", lines, ["id_linha","codigo","nome","cidade"]);
    byId("cityCount").textContent = cities.length;
    byId("lineCount").textContent = lines.length;
    const select = byId("lineCity"); const previous = select.value;
    select.replaceChildren(new Option("Selecione uma cidade", ""));
    for (const city of cities) select.add(new Option(city.nome, String(city.id_cidade)));
    select.value = previous;
    byId("saveLine").disabled = cities.length === 0;
    feedback("connection", "Banco conectado");
    feedback("queryFeedback", "Consultas atualizadas.");
    return true;
  } catch (error) {
    feedback("connection", "Conexão pendente", true);
    feedback("queryFeedback", error.message, true);
    byId("cityCount").textContent = "—"; byId("lineCount").textContent = "—";
    renderRows("cityRows", [], ["id_cidade","nome"]);
    renderRows("lineRows", [], ["id_linha","codigo","nome","cidade"]);
    for (const id of ["cityRows","lineRows"]) byId(id).rows[0].cells[0].textContent = "Consulta indisponível. Tente atualizar.";
    byId("saveLine").disabled = true; return false;
  } finally { byId("refresh").disabled = false; }
}
byId("cityForm").addEventListener("submit", async event => {
  event.preventDefault(); const button = event.target.querySelector("button"); button.disabled = true;
  try {
    const city = await request("/cidades", {nome:byId("cityName").value.trim()});
    event.target.reset();
    const updated = await refresh();
    if (updated) byId("lineCity").value = String(city.id_cidade);
    feedback("cityFeedback", "Cidade cadastrada. ID: " + city.id_cidade + (updated ? "." : ". Atualize a consulta quando a conexão voltar."));
  } catch (error) { feedback("cityFeedback", error.message, true); }
  finally { button.disabled = false; }
});
byId("lineForm").addEventListener("submit", async event => {
  event.preventDefault(); byId("saveLine").disabled = true;
  try {
    const line = await request("/linhas", {id_cidade:Number(byId("lineCity").value),codigo:byId("lineCode").value.trim(),nome:byId("lineName").value.trim()});
    event.target.reset(); await refresh();
    feedback("lineFeedback", "Linha cadastrada. ID: " + line.id_linha + ". Cidade: " + line.cidade + ".");
  } catch (error) { feedback("lineFeedback", error.message, true); }
  finally { byId("saveLine").disabled = byId("lineCity").options.length <= 1; }
});
byId("refresh").addEventListener("click", refresh);
refresh();
