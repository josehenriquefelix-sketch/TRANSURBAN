"use strict";
let currentUser = null;
let routes = [];
let renewal = null;
let recoveryToken = null;
let rechargeOperation = null;
let activePage = "";
const pageTitles = {
  inicio: "Visão geral",
  dashboard: "Dashboard de mobilidade",
  cidades: "Gestão de cidades",
  linhas: "Gestão de linhas",
  trajetos: "Trajetos e horários",
  avaliacoes: "Avaliações",
  passe: "Meu passe"
};
const authForms = {
  login: "loginForm",
  cadastro: "registerForm",
  "esqueci-senha": "forgotForm",
  "nova-senha": "resetForm"
};
const money = value => new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL"
}).format(value / 100);
const timeLabel = value => new Intl.DateTimeFormat("pt-BR", {
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "America/Sao_Paulo"
}).format(new Date(value));
const dateLabel = value => new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "short",
  timeStyle: "short",
  timeZone: "America/Sao_Paulo"
}).format(new Date(value));

function localDay() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Sao_Paulo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).formatToParts(new Date());
  const part = name => parts.find(item => item.type === name).value;
  return `${part("year")}-${part("month")}-${part("day")}`;
}

function textElement(tag, text, className = "") {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}

function toast(text) {
  $("toast").textContent = text;
  $("toast").hidden = false;
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => {
    $("toast").hidden = true;
  }, 5000);
}
async function renewSession() {
  if (!renewal) renewal = api("/auth/refresh", {
    method: "POST"
  }, false).then(() => true).catch(() => false).finally(() => {
    renewal = null;
  });
  return renewal;
}

function updatePermissions() {
  const admin = Boolean(currentUser?.administrador);
  document.querySelectorAll("[data-admin-form]").forEach(form => {
    form.hidden = !admin;
    form.querySelectorAll("input,select,button").forEach(node => {
      node.disabled = !admin;
    });
  });
  document.querySelectorAll("#cityRows tr,#lineRows tr").forEach(row => {
    if (row.cells.length > 1) row.cells[row.cells.length - 1].hidden = !admin;
  });
  document.querySelectorAll("#cidades table th:last-child,#linhas table th:last-child").forEach(node => {
    node.hidden = !admin;
  });
  document.querySelectorAll("#cidades .crud-layout,#linhas .crud-layout").forEach(node => {
    node.classList.toggle("read-only", !admin);
  });
  document.querySelectorAll("#cityRows button,#lineRows button").forEach(button => {
    button.disabled = !admin;
    button.title = admin ? "" : "Acesso da equipe necessário";
  });
  document.querySelectorAll(".admin-notice").forEach(node => {
    node.hidden = true;
  });
  document.querySelectorAll("[data-private]").forEach(node => {
    node.hidden = Boolean(currentUser);
  });
  document.querySelectorAll(".private-content").forEach(node => {
    node.classList.toggle("is-locked", !currentUser);
    node.inert = !currentUser;
  });
}

function updateAccount() {
  $("accountLabel").textContent = currentUser ? currentUser.nome.split(" ")[0] : "Entrar na conta";
  $("accountAvatar").textContent = currentUser ? currentUser.nome.slice(0, 1).toUpperCase() : "↗";
  $("accountLink").href = currentUser ? "#passe" : "#login";
  $("logoutButton").hidden = !currentUser;
  updatePermissions();
}
async function loadAccount() {
  try {
    currentUser = await api("/auth/me", {}, false);
  } catch {
    if (await renewSession()) {
      try {
        currentUser = await api("/auth/me", {}, false);
      } catch {
        currentUser = null;
      }
    } else currentUser = null;
  }
  updateAccount();
}
async function changePage() {
  let page = window.location.hash.slice(1) || "login";
  if (!pageTitles[page] && !authForms[page]) page = "inicio";
  const auth = Boolean(authForms[page]);
  $("authScreen").hidden = !auth;
  $("appShell").hidden = auth;
  for (const [name, id] of Object.entries(authForms)) $(id).hidden = page !== name;
  document.querySelectorAll("main>.page").forEach(node => {
    node.hidden = node.id !== page;
  });
  document.querySelectorAll("nav a[data-page]").forEach(link => {
    link.classList.toggle("active", link.dataset.page === page);
    if (link.dataset.page === page) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  $("pageBreadcrumb").textContent = pageTitles[page] || "Conta";
  document.title = `TRANSURBAN | ${pageTitles[page]||"Sua conta"}`;
  document.querySelector(".sidebar").classList.remove("open");
  $("menuToggle").setAttribute("aria-expanded", "false");
  if (page !== activePage) window.scrollTo({
    top: 0
  });
  activePage = page;
  if (page === "dashboard") await Promise.all([refreshAnalysis(), loadOfficialContext()]);
  if (page === "cidades" || page === "linhas") await refreshAll();
  if (page === "trajetos") await loadRoutes();
  if (page === "avaliacoes") {
    await loadRoutes();
    if (currentUser) await loadReviews();
  }
  if (page === "passe" && currentUser) await loadWallet();
}
async function loadOfficialContext() {
  const target = $("officialContext");
  try {
    const data = await api("/portal/contexto");
    target.replaceChildren();
    target.append(textElement("span", "DOCUMENTOS PÚBLICOS • MARINGÁ E SARANDI", "eyebrow"), textElement("h1", data.titulo), textElement("p", data.descricao));
    const metrics = textElement("div", "", "official-metrics");
    for (const item of data.indicadores) {
      const card = textElement("article", "", "metric");
      card.append(textElement("span", item.rotulo, "metric-label"), textElement("strong", item.valor), textElement("small", item.contexto));
      const source = data.fontes.find(source => source.id === item.fonte_id),
        link = textElement("a", "Consultar documento ↗");
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener";
      card.append(link);
      metrics.append(card);
    }
    target.append(metrics);
    const records = textElement("div", "", "analysis-grid");
    for (const record of data.registros) {
      const card = textElement("article", "", "card");
      card.append(textElement("h3", record.titulo), textElement("p", record.texto));
      if (record.citacao) {
        const quote = textElement("blockquote", `“${record.citacao}”`);
        quote.append(textElement("cite", record.atribuicao));
        card.append(quote);
      }
      const source = data.fontes.find(source => source.id === record.fonte_id),
        link = textElement("a", `${source.titulo} ↗`);
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener";
      card.append(link);
      records.append(card);
    }
    target.append(records);
    const notes = textElement("div", "", "notice");
    notes.append(textElement("p", data.limite), textElement("small", `Fontes consultadas em ${data.consultado_em.split("-").reverse().join("/")}. Tabela DER com vigência informada em 15/03/2026. Ofício municipal de 2023 e indicação legislativa de 2025.`));
    target.append(notes);
  } catch (error) {
    target.replaceChildren(textElement("p", error.message, "status"));
  }
}
async function handleForm(formId, statusId, action) {
  const form = $(formId),
    button = form.querySelector('button:not([type="button"])');
  button.disabled = true;
  setStatus(statusId, "Aguarde…");
  try {
    await action();
  } catch (error) {
    setStatus(statusId, error.message, true);
  } finally {
    button.disabled = false;
  }
}
$("loginForm").addEventListener("submit", event => {
  event.preventDefault();
  handleForm("loginForm", "loginFeedback", async () => {
    await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        identificador: $("loginId").value,
        senha: $("loginPassword").value
      })
    });
    $("loginPassword").value = "";
    await loadAccount();
    if (!currentUser) throw new Error("A sessão não pôde ser iniciada. Confira se os cookies estão habilitados.");
    window.location.hash = "inicio";
    toast("Bem-vindo ao TRANSURBAN.");
  });
});
$("registerForm").addEventListener("submit", event => {
  event.preventDefault();
  handleForm("registerForm", "registerFeedback", async () => {
    if ($("registerPassword").value !== $("registerConfirm").value) throw new Error("As senhas precisam ser iguais.");
    const result = await api("/auth/cadastro", {
      method: "POST",
      body: JSON.stringify({
        nome: $("registerName").value,
        email: $("registerEmail").value,
        cpf: $("registerCpf").value,
        senha: $("registerPassword").value
      })
    });
    $("registerForm").reset();
    setStatus("registerFeedback", result.mensagem);
    if (result.autenticado) {
      await loadAccount();
      window.location.hash = "inicio";
    }
  });
});
$("forgotForm").addEventListener("submit", event => {
  event.preventDefault();
  handleForm("forgotForm", "forgotFeedback", async () => {
    const result = await api("/auth/esqueci-senha", {
      method: "POST",
      body: JSON.stringify({
        email: $("forgotEmail").value
      })
    });
    setStatus("forgotFeedback", result.mensagem);
  });
});
$("resetForm").addEventListener("submit", event => {
  event.preventDefault();
  handleForm("resetForm", "resetFeedback", async () => {
    if (!recoveryToken) throw new Error("Abra o link enviado ao seu e-mail. Se ele expirou, solicite outro.");
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
    setStatus("resetFeedback", result.mensagem);
  });
});
document.querySelectorAll(".show-password").forEach(button => button.addEventListener("click", () => {
  const input = $(button.dataset.for);
  input.type = input.type === "password" ? "text" : "password";
  button.textContent = input.type === "password" ? "Ver" : "Ocultar";
  button.setAttribute("aria-label", input.type === "password" ? "Mostrar senha" : "Ocultar senha");
}));
$("logoutButton").addEventListener("click", async () => {
  $("logoutButton").disabled = true;
  try {
    await api("/auth/logout", {
      method: "POST"
    });
    currentUser = null;
    updateAccount();
    $("reviewList").replaceChildren();
    $("walletHistory").replaceChildren();
    $("walletBalance").textContent = "R$ —";
    $("walletHolder").textContent = "Seu nome";
    $("walletNumber").textContent = "•••• ••••";
    $("reviewForm").reset();
    resetCityForm();
    resetLineForm();
    rechargeOperation = null;
    window.location.hash = "login";
    toast("Você saiu da conta.");
  } catch (error) {
    toast(error.message);
  } finally {
    $("logoutButton").disabled = false;
  }
});
$("menuToggle").addEventListener("click", () => {
  const opened = document.querySelector(".sidebar").classList.toggle("open");
  $("menuToggle").setAttribute("aria-expanded", String(opened));
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape") {
    document.querySelector(".sidebar").classList.remove("open");
    $("menuToggle").setAttribute("aria-expanded", "false");
  }
});

async function loadRoutes() {
  try {
    routes = await api("/portal/trajetos");
    for (const id of ["journeyRoute", "reviewRoute"]) {
      const select = $(id),
        previous = select.value;
      select.replaceChildren(new Option("Selecione um trajeto", ""));
      for (const route of routes) select.add(new Option(route.nome, String(route.id)));
      if (routes.some(route => String(route.id) === previous)) select.value = previous;
    }
    if (!routes.length) setStatus("journeyFeedback", "Nenhum trajeto cadastrado.");
  } catch (error) {
    setStatus("journeyFeedback", error.message, true);
    setStatus("reviewFeedback", error.message, true);
  }
}
$("journeyForm").addEventListener("submit", event => {
  event.preventDefault();
  handleForm("journeyForm", "journeyFeedback", async () => {
    const result = await api(`/portal/horarios?trajeto_id=${encodeURIComponent($("journeyRoute").value)}&dia=${encodeURIComponent($("journeyDate").value)}`);
    $("routeName").textContent = result.trajeto.nome;
    $("routeStops").replaceChildren();
    $("scheduleList").replaceChildren();
    for (const stop of result.trajeto.paradas) {
      const row = textElement("div", "", "stop"),
        copy = document.createElement("div");
      copy.append(textElement("strong", stop.nome), textElement("small", stop.minutos === 0 ? "Ponto de embarque" : `${stop.minutos} min após o embarque`));
      row.append(textElement("span", "", "stop-dot"), copy);
      $("routeStops").append(row);
    }
    for (const schedule of result.horarios) {
      const card = textElement("article", "", "schedule-item"),
        times = textElement("div", "", "schedule-time");
      for (const [value, label] of [
          [schedule.embarque, "EMBARQUE"],
          [schedule.chegada, "CHEGADA"]
        ]) {
        const column = document.createElement("div");
        column.append(textElement("small", label), textElement("strong", timeLabel(value)));
        if (times.childElementCount) times.append(textElement("span", "→"));
        times.append(column);
      }
      card.append(times, textElement("p", `${schedule.veiculo} · ${schedule.motorista}`));
      const stopTimes = schedule.paradas.map(stop => `${stop.nome}: ${timeLabel(stop.horario)}`).join(" · ");
      const details = document.createElement("details");
      details.append(textElement("summary", "Ver horários nas paradas"), textElement("p", stopTimes));
      card.append(details);
      $("scheduleList").append(card);
    }
    if (!result.horarios.length) $("scheduleList").append(textElement("p", "Não há horários programados para esta data."));
    setStatus("journeyFeedback", `${result.horarios.length} horários · Duração programada de ${result.trajeto.duracao_min} minutos · ${result.fonte}.`);
  });
});
async function loadReviewSchedules() {
  $("reviewSchedule").replaceChildren(new Option("Selecione um horário", ""));
  if (!$("reviewRoute").value) return;
  try {
    const result = await api(`/portal/horarios?trajeto_id=${$("reviewRoute").value}&dia=${$("reviewDate").value}`);
    for (const schedule of result.horarios) $("reviewSchedule").add(new Option(`${timeLabel(schedule.embarque)} · ${schedule.veiculo} · ${schedule.motorista}`, String(schedule.id)));
  } catch (error) {
    setStatus("reviewFeedback", error.message, true);
  }
}
$("reviewRoute").addEventListener("change", loadReviewSchedules);
$("reviewDate").addEventListener("change", loadReviewSchedules);
async function loadReviews() {
  try {
    const reviews = await api("/portal/avaliacoes");
    $("reviewList").replaceChildren();
    if (!reviews.length) $("reviewList").append(textElement("p", "Sua primeira avaliação pode começar por aqui."));
    for (const review of reviews) {
      const item = document.createElement("article");
      item.append(textElement("h3", `Ônibus ${review.nota_onibus} ★ · Motorista ${review.nota_motorista} ★`), textElement("small", `Experiência em ${review.dia.split("-").reverse().join("/")} · Horário #${review.horario_id}`));
      if (review.comentario) item.append(textElement("p", review.comentario));
      const remove = textElement("button", "Excluir minha avaliação", "table-action danger");
      remove.type = "button";
      remove.addEventListener("click", async () => {
        if (!window.confirm("Excluir esta avaliação?")) return;
        remove.disabled = true;
        try {
          await api(`/portal/avaliacoes/${review.id}`, {
            method: "DELETE"
          });
          await loadReviews();
          toast("Avaliação excluída.");
        } catch (error) {
          toast(error.message);
        } finally {
          remove.disabled = false;
        }
      });
      item.append(remove);
      $("reviewList").append(item);
    }
  } catch (error) {
    setStatus("reviewFeedback", error.message, true);
  }
}
$("reviewForm").addEventListener("submit", event => {
  event.preventDefault();
  handleForm("reviewForm", "reviewFeedback", async () => {
    const data = new FormData($("reviewForm"));
    await api("/portal/avaliacoes", {
      method: "POST",
      body: JSON.stringify({
        horario_id: Number($("reviewSchedule").value),
        dia: $("reviewDate").value,
        nota_onibus: Number(data.get("busRating")),
        nota_motorista: Number(data.get("driverRating")),
        comentario: $("reviewComment").value.trim()
      })
    });
    $("reviewComment").value = "";
    setStatus("reviewFeedback", "Avaliação registrada. Obrigado pela sua contribuição!");
    await loadReviews();
  });
});
async function loadWallet() {
  try {
    const wallet = await api("/portal/passe");
    $("walletBalance").textContent = money(wallet.saldo_centavos);
    $("walletHolder").textContent = currentUser.nome;
    $("walletNumber").textContent = `TU ${String(wallet.numero).padStart(8,"0")}`;
    $("walletHistory").replaceChildren();
    if (!wallet.recargas.length) $("walletHistory").append(textElement("p", "Você ainda não tem recargas de demonstração."));
    for (const recharge of wallet.recargas) {
      const item = document.createElement("article");
      item.append(textElement("strong", `+ ${money(recharge.valor_centavos)}`, "money"), textElement("h3", "Recarga demonstrativa concluída"), textElement("small", `${dateLabel(recharge.criado_em)} · Operação #${recharge.id}`));
      $("walletHistory").append(item);
    }
  } catch (error) {
    setStatus("walletFeedback", error.message, true);
  }
}
document.querySelectorAll("[data-amount]").forEach(button => button.addEventListener("click", () => {
  $("rechargeValue").value = button.dataset.amount;
  document.querySelectorAll("[data-amount]").forEach(node => node.classList.toggle("selected", node === button));
}));
$("rechargeForm").addEventListener("submit", event => {
  event.preventDefault();
  const value = Math.round(Number($("rechargeValue").value) * 100);
  if (!currentUser) {
    window.location.hash = "login";
    return;
  }
  // Mantém a chave após falha de rede. Repetir a confirmação não duplica o crédito.
  if (!rechargeOperation || rechargeOperation.valor_centavos !== value) rechargeOperation = {
    valor_centavos: value,
    chave: crypto.randomUUID()
  };
  $("rechargeConfirmValue").textContent = money(value);
  setStatus("rechargeDialogStatus", "");
  $("rechargeDialog").showModal();
});
$("confirmRecharge").addEventListener("click", async () => {
  $("confirmRecharge").disabled = true;
  try {
    await api("/portal/recargas", {
      method: "POST",
      body: JSON.stringify(rechargeOperation)
    });
    rechargeOperation = null;
    $("rechargeDialog").close();
    setStatus("walletFeedback", "Recarga demonstrativa registrada com sucesso.");
    $("demoConsent").checked = false;
    await loadWallet();
    toast("Créditos de demonstração adicionados ao passe.");
  } catch (error) {
    setStatus("rechargeDialogStatus", error.message, true);
  } finally {
    $("confirmRecharge").disabled = false;
  }
});
async function startPortal() {
  const fragment = new URLSearchParams(window.location.hash.slice(1));
  if (fragment.get("type") === "recovery" && fragment.get("access_token")) {
    recoveryToken = fragment.get("access_token");
    history.replaceState(null, "", "/#nova-senha");
  } else if (fragment.get("error_description")) {
    history.replaceState(null, "", "/#esqueci-senha");
    setStatus("forgotFeedback", "O link expirou ou já foi utilizado. Solicite um novo link.", true);
  } else if (fragment.get("access_token")) {
    // Confirmação de e-mail concluída. A sessão será criada pelo login.
    history.replaceState(null, "", "/#login");
    setStatus("loginFeedback", "E-mail confirmado. Entre com sua senha.");
  }
  $("journeyDate").value = localDay();
  $("reviewDate").value = localDay();
  $("reviewDate").max = localDay();
  window.addEventListener("hashchange", () => changePage().catch(error => toast(error.message)));
  updateAccount();
  await changePage();
  await Promise.all([loadAccount(), checkService()]);
  if (currentUser && !window.location.hash) window.location.hash = "inicio";
  if (currentUser && activePage === "passe") await loadWallet();
  if (currentUser && activePage === "avaliacoes") await loadReviews();
}
startPortal().catch(error => toast(error.message));
