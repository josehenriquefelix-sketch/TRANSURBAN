const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");


// ======================================================
// ENVIAR MENSAGEM PARA O BACKEND
// ======================================================

async function sendMessage() {

    const texto = userInput.value.trim();

    if (!texto) {
        return;
    }

    adicionarMensagem(texto, "user");

    userInput.value = "";

    mostrarDigitando();

    try {

        const resposta = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: texto
            })
        });

        const dados = await resposta.json();

        removerDigitando();

        if (!resposta.ok) {
            throw new Error(
                dados.error || "Não foi possível consultar a IA."
            );
        }

        adicionarMensagem(
            formatarResposta(dados.answer),
            "bot"
        );

    } catch (erro) {

        removerDigitando();

        adicionarMensagem(
            "Não foi possível consultar a IA agora.<br><br>" +
            escaparHtml(erro.message),
            "bot"
        );
    }
}


// ======================================================
// SUGESTÕES
// ======================================================

function sendSuggestion(texto) {

    userInput.value = texto;

    sendMessage();
}


// ======================================================
// FORMATAR RESPOSTA
// ======================================================

function formatarResposta(texto) {

    return escaparHtml(texto)
        .replace(/\n/g, "<br>");
}


// ======================================================
// PROTEÇÃO DO HTML
// ======================================================

function escaparHtml(texto) {

    const div = document.createElement("div");

    div.textContent = texto;

    return div.innerHTML;
}


// ======================================================
// ADICIONAR MENSAGEM
// ======================================================

function adicionarMensagem(texto, tipo) {

    const message = document.createElement("div");

    message.className = `message ${tipo}`;

    const avatar = document.createElement("div");

    avatar.className = "avatar";

    avatar.innerText = tipo === "bot"
        ? "TU"
        : "VOCÊ";


    const bubble = document.createElement("div");

    bubble.className = "bubble";

    bubble.innerHTML = texto;


    message.appendChild(avatar);

    message.appendChild(bubble);

    chatMessages.appendChild(message);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


// ======================================================
// INDICADOR DE DIGITAÇÃO
// ======================================================

function mostrarDigitando() {

    removerDigitando();

    const typing = document.createElement("div");

    typing.id = "typing";

    typing.className = "message bot";

    typing.innerHTML = `
        <div class="avatar">TU</div>

        <div class="bubble">
            Digitando...
        </div>
    `;

    chatMessages.appendChild(typing);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function removerDigitando() {

    const typing = document.getElementById("typing");

    if (typing) {
        typing.remove();
    }
}


// ======================================================
// ENTER PARA ENVIAR
// ======================================================

userInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }

});
