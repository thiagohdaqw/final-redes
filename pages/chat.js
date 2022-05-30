MessageTypes = {
    MESSAGE: 'M:',
    WEBCAM: 'W:',
    AUDIO: 'A:',
}

Commands = {
    CREATE: '/CREATE',
    JOIN: '/JOIN',
    EXIT: '/EXIT'
}

chatElement = document.getElementById("chat");
chatInputElement = document.getElementById("chat-input");

socket = null;

usersWebcams = {};
isInChannel = false;

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

onWebcamCapture = data => {
    if (!isInChannel) {
        return;
    }
    console.log(data.length)
    socket.send(data);
};

function onOpen(ev) {
    addChatMessage("[SERVER]: Conexão realizada com sucesso!")
    addChatMessage("[SERVER]: Digite /help para descobrir os comandos")
}

function onMessage(ev) {
    let msg = ev.data;

    if (msg.startsWith('W'))
        return manageWebcamResponse(msg);
    if (msg.startsWith('/'))
        return manageCommandResponse(msg);
    if (msg.startsWith(MessageTypes.MESSAGE))
        msg = msg.slice(2, msg.length);
    addChatMessage(msg);
}

function onClose(ev) {
    isInChannel = false;
    addChatMessage("[SERVER]: Desconectando...");
}

function onError(ev) {
    console.log(ev);
    isInChannel = false;
    addChatMessage("[SERVER_ERROR]" + ev.toString());
}

function manageCommandResponse(msg) {
    equals = com => msg.startsWith(com)
    isInChannel = !equals(Commands.EXIT)
}

function manageWebcamResponse(msg) {
    let [username, index] = getUsername(msg);
    let img = usersWebcams[username];
    const dataUrl = msg.slice(index+2, msg.length);

    if (!img) {
        img = createWebcamElement(dataUrl)
        usersWebcams[username] = img;
    }
    setImgSrc(img, dataUrl);
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

function getUsername(msg) {
    let i = 3;
    let username = '';
    while (msg[i] != ']' && msg[i+1] != ':') {
        username += msg[i++];
    }
    return [username, i];
}