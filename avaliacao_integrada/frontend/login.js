"use strict";

const form = document.querySelector("#loginForm");
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const email = document.querySelector("#email").value.trim().toLowerCase();
  const senha = document.querySelector("#senha").value;
  if (email === "demo@transurban.test" && senha === "transurban-demo") {
    window.location.assign("/");
    return;
  }
  document.querySelector("#loginStatus").textContent =
    "Dados de teste incorretos. Use o e-mail e a senha indicados acima.";
});
