socket = null;

chatElement = document.getElementById("chat");
chatInputElement = document.getElementById("chat-input");

function connect() {
    if (socket != null) {
        socket.close();
    }
    
    const connectionString = document.getElementById("connection-string").value;
    
    socket = new WebSocket(connectionString);
    socket.onopen = onOpen;
    socket.onmessage = onMessage;
    socket.onerror = onError;
    socket.onclose = onClose;
}

chatInputElement.addEventListener("keyup", function(event) {
    // Number 13 is the "Enter" key on the keyboard
    if (event.keyCode === 13) {
        event.preventDefault();
        sendMessage(event.target.value);
        event.target.value = "";
    }
});

function sendMessage(text) {
    text = text.trim();
    if (socketClosed()) {
        addChatMessage("[INFO]: Primeiro conecte-se ao servidor!");
        return;
    }
    
    if (text.length > 0) {
        socket.send(text);
        addChatMessage("[Voce]: " + text, true);
    }
}

function onOpen(ev) {
    addChatMessage("[SERVER]: Conexão realizada com sucesso!")
    addChatMessage("[SERVER]: Digite /help para descobrir os comandos")
}

function onMessage(ev) {
    addChatMessage(ev.data);
}

function onClose(ev) {
    addChatMessage("[SERVER]: Desconectando...");
}

function onError(ev) {
    console.log(ev);
    addChatMessage("[SERVER_ERROR]" + ev.toString());
}

function addChatMessage(text, isPersonal = false) {
    const personalClass = isPersonal ? "pessoal" : "server";
    const messageElement = document.createElement("p");

    messageElement.classList.add("mensagem", personalClass);
    text.split(/\n/).forEach((line, index, list) => {
        const lineElement = document.createElement("span");
        lineElement.textContent = line;

        messageElement.appendChild(lineElement);

        if (index + 1 < list.length) {
            messageElement.appendChild(document.createElement("br"));
        }
    });

    chatElement.prepend(messageElement);
}

function socketClosed() {
    return socket == null || socket.readyState == socket.CLOSED;
}