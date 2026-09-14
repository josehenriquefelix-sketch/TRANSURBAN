const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");


// ======================================================
// BANCO DE DADOS
// ======================================================

const linhas = {

    maringa: {

        "007": {
            nome: "Interbairros Zona Norte",
            regioes: "Morangueira, Alvorada, Zona Norte e Terminal",
            horarios: "aproximadamente entre 5h e 23h30",
            atraso: "Pode apresentar atrasos principalmente nos horários de pico."
        },

        "010": {
            nome: "Universidade",
            regioes: "UEM, Zona 7, Centro e Terminal",
            horarios: "aproximadamente das 5h às 23h",
            atraso: "Pode apresentar atrasos principalmente por causa do trânsito."
        },

        "021": {
            nome: "Av. Tuiuti",
            regioes: "Av. Tuiuti, Jardim Alvorada e Centro",
            horarios: "aproximadamente das 5h às 23h",
            atraso: "Atrasos ocasionais podem ocorrer nos horários de maior movimento."
        },

        "022": {
            nome: "Conjunto Guaiapó",
            regioes: "Guaiapó, Centro e Terminal",
            horarios: "primeiras viagens por volta das 5h",
            atraso: "Pode apresentar lotação nos horários de pico."
        },

        "201": {
            nome: "Maringá–Iguatemi",
            regioes: "Centro, Terminal e Distrito de Iguatemi",
            horarios: "intervalos maiores, principalmente aos fins de semana",
            atraso: "Pode apresentar atrasos especialmente aos sábados e domingos."
        },

        "242": {
            nome: "Jardim América",
            regioes: "Jardim América, Shopping Catuaí e Centro",
            horarios: "aproximadamente das 5h às 23h",
            atraso: "A alta demanda pode provocar atrasos, principalmente pela manhã."
        },

        "023": {
            nome: "Jardim Olímpico",
            regioes: "Jardim Olímpico, Vila Esperança, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h20 às 22h50",
            atraso: "Pode apresentar atrasos de 5 a 10 minutos nos horários de pico."
        },

        "024": {
            nome: "Parque Itaipu",
            regioes: "Parque Itaipu, Jardim Novo Horizonte, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h10 às 23h",
            atraso: "Pode apresentar lotação e pequenos atrasos no início da manhã e fim da tarde."
        },

        "031": {
            nome: "Conjunto Requião",
            regioes: "Conjunto Requião, Jardim Paris, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h30 às 22h40",
            atraso: "Atrasos podem ocorrer em dias de chuva ou trânsito intenso."
        },

        "034": {
            nome: "Jardim São Silvestre",
            regioes: "Jardim São Silvestre, Vila Morangueira, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h15 às 22h30",
            atraso: "Pode apresentar atrasos ocasionais durante a tarde."
        },

        "324": {
            nome: "UEM / Unicesumar",
            regioes: "UEM, Unicesumar, Zona 7, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h às 23h10",
            atraso: "É comum ocorrer lotação e atrasos de até 10 minutos nos horários de entrada e saída das universidades."
        },

        "011": {
            nome: "Jardim Internorte",
            regioes: "Jardim Internorte, Jardim Império do Sol, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h10 às 22h50",
            atraso: "Pode apresentar atrasos de 5 a 10 minutos nos horários de maior movimento."
        },

        "013": {
            nome: "Jardim Montreal",
            regioes: "Jardim Montreal, Jardim Liberdade, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h20 às 23h",
            atraso: "Pode apresentar lotação e atrasos ocasionais no início da manhã."
        },

        "026": {
            nome: "Jardim Paulista",
            regioes: "Jardim Paulista, Vila Santo Antônio, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h às 22h45",
            atraso: "Atrasos podem ocorrer em dias chuvosos e no pico da tarde."
        },

        "032": {
            nome: "Parque Avenida",
            regioes: "Parque Avenida, Zona 8, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h30 às 22h30",
            atraso: "Pode sofrer atrasos devido ao trânsito nas avenidas centrais."
        },

        "035": {
            nome: "Jardim Pinheiros",
            regioes: "Jardim Pinheiros, Jardim Alamar, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h15 às 22h40",
            atraso: "Pode apresentar ônibus cheios e pequenos atrasos nos horários de trabalho."
        },

        "041": {
            nome: "Jardim Alvorada II",
            regioes: "Jardim Alvorada II, Jardim Paris, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h20 às 22h50",
            atraso: "Pode apresentar pequenos atrasos no pico da manhã."
        },

        "043": {
            nome: "Jardim Santa Felicidade",
            regioes: "Jardim Santa Felicidade, Vila Morangueira, Centro e Terminal",
            horarios: "aproximadamente das 5h15 às 22h40",
            atraso: "Pode operar com veículos cheios no fim da tarde e apresentar atrasos."
        },

        "051": {
            nome: "Parque das Grevíleas",
            regioes: "Parque das Grevíleas, Jardim Novo Horizonte, Centro e Terminal",
            horarios: "aproximadamente das 5h30 às 23h",
            atraso: "Os principais atrasos ocorrem em dias de chuva e congestionamentos."
        },

        "414": {
            nome: "Jardim São Jorge",
            regioes: "Jardim São Jorge, Zona Norte, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h10 às 22h45",
            atraso: "Pode apresentar intervalos maiores fora dos horários de pico."
        },

        "611": {
            nome: "Distrito Industrial",
            regioes: "Distrito Industrial, Centro e Terminal Urbano",
            horarios: "aproximadamente das 6h às 20h em dias úteis",
            atraso: "Possui baixa frequência e poucos horários disponíveis."
        },

        "052": {
            nome: "Jardim Bertioga",
            regioes: "Jardim Bertioga, Jardim Universo, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h20 às 22h40",
            atraso: "Pequenos atrasos podem ocorrer nos horários de pico."
        },

        "053": {
            nome: "Parque Hortência",
            regioes: "Parque Hortência, Jardim Imperial, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h30 às 23h",
            atraso: "Pode apresentar maior tempo de espera aos sábados e no período noturno."
        },

        "054": {
            nome: "Jardim Dias I",
            regioes: "Jardim Dias I, Jardim Dias II, Centro e Terminal Urbano",
            horarios: "aproximadamente das 5h10 às 22h50",
            atraso: "Pode apresentar lotação e atrasos entre 17h e 19h."
        }

    },


    londrina: {

        "101": {
            nome: "Jardim do Sol",
            regioes: "Terminal Central, Jardim do Sol e região Oeste",
            horarios: "aproximadamente das 5h às 23h10",
            atraso: "Pode apresentar atrasos de 5 a 10 minutos nos horários de pico."
        },

        "111": {
            nome: "Pioneiros",
            regioes: "Terminal Central, Jardim Pioneiros e região Leste",
            horarios: "aproximadamente das 5h10 às 22h50",
            atraso: "Geralmente possui boa pontualidade, mas pode sofrer pequenos atrasos."
        },

        "112": {
            nome: "Alexandre Urbanas",
            regioes: "Terminal Central, Alexandre Urbanas e Zona Leste",
            horarios: "aproximadamente das 5h20 às 22h45",
            atraso: "Pode apresentar atrasos em horários escolares e comerciais."
        },

        "113": {
            nome: "Jardim dos Pioneiros",
            regioes: "Terminal Central e Jardim dos Pioneiros",
            horarios: "aproximadamente das 5h15 às 22h50",
            atraso: "Pode sofrer variações em dias de chuva."
        },

        "114": {
            nome: "Jardim Maíra",
            regioes: "Terminal Central, Jardim Maíra e Zona Leste",
            horarios: "aproximadamente das 5h20 às 22h40",
            atraso: "Atrasos podem ocorrer devido ao trânsito em vias de grande circulação."
        },

        "121": {
            nome: "Três Figueiras",
            regioes: "Terminal Central, Três Figueiras e Parque Industrial Buena Vista",
            horarios: "aproximadamente das 5h às 23h",
            atraso: "Atrasos costumam ser inferiores a 10 minutos na maior parte do dia."
        },

        "203": {
            nome: "Ouro Branco",
            regioes: "Terminal Acapulco, Ouro Branco e Zona Sul",
            horarios: "aproximadamente das 5h20 às 22h40",
            atraso: "Pode apresentar atrasos nos horários de entrada e saída do trabalho."
        },

        "210": {
            nome: "União da Vitória",
            regioes: "Terminal Central, União da Vitória e Zona Sul",
            horarios: "aproximadamente das 5h10 às 22h50",
            atraso: "O tempo de viagem pode variar conforme o trânsito e obras."
        },

        "303": {
            nome: "Jardim Tókyo",
            regioes: "Terminal Central, Terminal Oeste e Jardim Tókyo",
            horarios: "aproximadamente das 5h às 23h",
            atraso: "Nos horários de menor movimento normalmente cumpre a programação."
        },

        "423": {
            nome: "São Jorge",
            regioes: "Terminal Vivi Xavier, São Jorge e Residencial Jequitibá",
            horarios: "aproximadamente das 5h20 às 22h40",
            atraso: "Chuva intensa ou acidentes podem causar atrasos maiores."
        }

    },


    sarandi: {

        "001": {
            nome: "Parque Alvamar / Conjunto Floresta",
            regioes: "Parque Alvamar, Jardim Panorama, Centro e Conjunto Floresta",
            horarios: "aproximadamente das 5h20 às 22h40",
            atraso: "Pode apresentar atrasos de 5 a 10 minutos no trânsito entre Sarandi e Maringá."
        },

        "254A": {
            nome: "Alvamar",
            regioes: "Parque Alvamar, Jardim Panorama e região Norte",
            horarios: "aproximadamente das 5h30 às 23h",
            atraso: "Pode apresentar pequenas variações no início da manhã e fim da tarde."
        },

        "254C": {
            nome: "Jardim Cometa",
            regioes: "Jardim Cometa, Centro e região Oeste",
            horarios: "aproximadamente das 5h10 às 22h45",
            atraso: "Pode sofrer atrasos em períodos de maior movimento."
        },

        "254E": {
            nome: "Jardim Esperança",
            regioes: "Jardim Esperança, Centro e bairros próximos",
            horarios: "aproximadamente das 5h20 às 22h30",
            atraso: "Atrasos podem ocorrer em dias de chuva ou aumento do fluxo de passageiros."
        },

        "254I": {
            nome: "Jardim Independência",
            regioes: "Jardim Independência, Jardim Monte Rey e região Norte/Leste",
            horarios: "aproximadamente das 5h15 às 22h50",
            atraso: "Pode apresentar demora nos horários de entrada e saída de trabalhadores e estudantes."
        },

        "254J": {
            nome: "Conjunto José Richa",
            regioes: "Conjunto José Richa, Jardim Panorama e região Central",
            horarios: "aproximadamente das 5h30 às 22h40",
            atraso: "Pode apresentar atrasos pontuais durante o dia."
        },

        "254L": {
            nome: "Jardim Leblon",
            regioes: "Jardim Leblon e Centro",
            horarios: "aproximadamente das 5h20 às 23h",
            atraso: "O tempo de viagem pode variar conforme as condições das vias."
        },

        "254M": {
            nome: "Monte Rey",
            regioes: "Jardim Monte Rey e Jardim Independência",
            horarios: "aproximadamente das 5h10 às 22h45",
            atraso: "Pode apresentar atrasos eventuais nos horários de pico."
        },

        "254N": {
            nome: "Nova Aliança",
            regioes: "Jardim Nova Aliança e região Central",
            horarios: "aproximadamente das 5h20 às 22h35",
            atraso: "Pode ocorrer atraso devido ao trânsito entre bairros e região central."
        },

        "254O": {
            nome: "Ouro Verde",
            regioes: "Jardim Ouro Verde e região Sul/Leste",
            horarios: "aproximadamente das 5h30 às 22h50",
            atraso: "Obras, acidentes ou chuvas fortes podem provocar atrasos maiores."
        }

    }

};


// ======================================================
// DESCOBRIR CIDADE
// ======================================================

function descobrirCidade(texto) {

    texto = texto.toLowerCase();

    if (
        texto.includes("maringá") ||
        texto.includes("maringa") ||
        texto.includes("uem") ||
        texto.includes("unicesumar")
    ) {
        return "maringa";
    }

    if (
        texto.includes("londrina") ||
        texto.includes("terminal central") ||
        texto.includes("jardim do sol")
    ) {
        return "londrina";
    }

    if (
        texto.includes("sarandi") ||
        texto.includes("alvamar") ||
        texto.includes("monte rey")
    ) {
        return "sarandi";
    }

    return null;
}


// ======================================================
// ENCONTRAR LINHA
// ======================================================

function encontrarLinha(texto) {

    const numeros = texto.toUpperCase()
        .match(/\b\d{3}[A-Z]?\b/g);

    if (!numeros) {
        return null;
    }

    return numeros[0];
}


// ======================================================
// TODAS AS LINHAS DE UMA CIDADE
// ======================================================

function listarLinhas(cidade) {

    const dados = linhas[cidade];

    if (!dados) {
        return "Não encontrei os dados dessa cidade.";
    }

    const nomes = Object.keys(dados)
        .map(codigo => `${codigo} – ${dados[codigo].nome}`)
        .join("<br>");

    return nomes;
}


// ======================================================
// RESPOSTA DO CHAT
// ======================================================

function gerarResposta(pergunta) {

    const texto = pergunta.toLowerCase();

    const cidade = descobrirCidade(texto);

    const codigo = encontrarLinha(pergunta);


    // --------------------------------------------
    // PERGUNTA SOBRE CIDADE
    // --------------------------------------------

    if (
        texto.includes("linhas de maringá") ||
        texto.includes("linhas de maringa")
    ) {

        return `
            🚌 <strong>Linhas cadastradas de Maringá:</strong>
            <br><br>
            ${listarLinhas("maringa")}
        `;
    }


    if (texto.includes("linhas de londrina")) {

        return `
            🚌 <strong>Linhas cadastradas de Londrina:</strong>
            <br><br>
            ${listarLinhas("londrina")}
        `;
    }


    if (texto.includes("linhas de sarandi")) {

        return `
            🚌 <strong>Linhas cadastradas de Sarandi:</strong>
            <br><br>
            ${listarLinhas("sarandi")}
        `;
    }


    // --------------------------------------------
    // NÃO ENCONTROU CÓDIGO
    // --------------------------------------------

    if (!codigo) {

        if (
            texto.includes("atras") ||
            texto.includes("demor") ||
            texto.includes("esper")
        ) {

            return `
                ⚠️ Entendi que você está com um problema de atraso.

                <br><br>

                Para eu ajudar melhor, informe o <strong>número da linha</strong>.

                <br><br>

                Por exemplo:
                <br>
                <em>"A linha 324 atrasou, o que eu faço?"</em>
            `;
        }


        return `
            Posso ajudar com informações sobre ônibus e linhas de
            <strong>Maringá, Londrina e Sarandi</strong>.

            <br><br>

            Você pode perguntar, por exemplo:

            <br><br>

            🚌 "A linha 324 atrasou, o que eu faço?"

            <br>

            📍 "Quais bairros a linha 324 atende?"

            <br>

            🕐 "Qual o horário da linha 101?"

            <br>

            🔎 "Me fale sobre a linha 254A."
        `;
    }


    // --------------------------------------------
    // LOCALIZAR LINHA
    // --------------------------------------------

    let dados = null;
    let cidadeEncontrada = cidade;


    if (cidadeEncontrada && linhas[cidadeEncontrada][codigo]) {

        dados = linhas[cidadeEncontrada][codigo];

    } else {

        for (const nomeCidade in linhas) {

            if (linhas[nomeCidade][codigo]) {

                dados = linhas[nomeCidade][codigo];

                cidadeEncontrada = nomeCidade;

                break;
            }
        }
    }


    // --------------------------------------------
    // LINHA NÃO CADASTRADA
    // --------------------------------------------

    if (!dados) {

        return `
            🔎 Não encontrei a linha <strong>${codigo}</strong>
            nos dados cadastrados do Trans Urban.

            <br><br>

            Confira se o número foi digitado corretamente.
        `;
    }


    // --------------------------------------------
    // PERGUNTA SOBRE ATRASO
    // --------------------------------------------

    if (
        texto.includes("atras") ||
        texto.includes("demor") ||
        texto.includes("esper")
    ) {

        return `
            ⚠️ <strong>Sobre a linha ${codigo} – ${dados.nome}</strong>

            <br><br>

            ${dados.atraso}

            <br><br>

            <strong>Se o ônibus estiver atrasado agora:</strong>

            <br><br>

            • Aguarde alguns minutos e confira se o próximo veículo chega.

            <br>

            • Se possível, procure outra opção de linha para o mesmo destino.

            <br>

            • Em caso de atraso muito grande, procure os canais oficiais
            da empresa responsável pelo transporte.

            <br><br>

            ℹ️ O Trans Urban não possui rastreamento em tempo real.
        `;
    }


    // --------------------------------------------
    // PERGUNTA SOBRE HORÁRIO
    // --------------------------------------------

    if (
        texto.includes("horário") ||
        texto.includes("horario") ||
        texto.includes("que horas") ||
        texto.includes("funciona")
    ) {

        return `
            🕐 <strong>Linha ${codigo} – ${dados.nome}</strong>

            <br><br>

            O cadastro do Trans Urban indica operação
            <strong>${dados.horarios}</strong>.

            <br><br>

            ⚠️ Esses são horários de referência e podem sofrer
            alterações na operação real.
        `;
    }


    // --------------------------------------------
    // PERGUNTA SOBRE BAIRROS / REGIÕES
    // --------------------------------------------

    if (
        texto.includes("bairro") ||
        texto.includes("região") ||
        texto.includes("regiao") ||
        texto.includes("passa") ||
        texto.includes("atende")
    ) {

        return `
            📍 <strong>Linha ${codigo} – ${dados.nome}</strong>

            <br><br>

            Essa linha atende:

            <br><br>

            <strong>${dados.regioes}</strong>
        `;
    }


    // --------------------------------------------
    // RESPOSTA GERAL SOBRE LINHA
    // --------------------------------------------

    return `
        🚌 <strong>Linha ${codigo} – ${dados.nome}</strong>

        <br><br>

        📍 <strong>Regiões:</strong><br>
        ${dados.regioes}

        <br><br>

        🕐 <strong>Horários:</strong><br>
        ${dados.horarios}

        <br><br>

        ⚠️ <strong>Atrasos:</strong><br>
        ${dados.atraso}
    `;
}


// ======================================================
// ENVIAR MENSAGEM
// ======================================================

function sendMessage() {

    const texto = userInput.value.trim();

    if (!texto) {
        return;
    }

    adicionarMensagem(texto, "user");

    userInput.value = "";

    mostrarDigitando();


    setTimeout(() => {

        removerDigitando();

        const resposta = gerarResposta(texto);

        adicionarMensagem(resposta, "bot");

    }, 600);
}


// ======================================================
// SUGESTÕES
// ======================================================

function sendSuggestion(texto) {

    userInput.value = texto;

    sendMessage();
}


// ======================================================
// ADICIONAR MENSAGEM
// ======================================================

function adicionarMensagem(texto, tipo) {

    const message = document.createElement("div");

    message.className = `message ${tipo}`;

    const avatar = document.createElement("div");

    avatar.className = "avatar";

    avatar.innerText = tipo === "bot" ? "TU" : "VOCÊ";


    const bubble = document.createElement("div");

    bubble.className = "bubble";

    bubble.innerHTML = texto;


    message.appendChild(avatar);

    message.appendChild(bubble);

    chatMessages.appendChild(message);


    chatMessages.scrollTop = chatMessages.scrollHeight;
}


// ======================================================
// DIGITANDO
// ======================================================

function mostrarDigitando() {

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
        sendMessage();
    }

});