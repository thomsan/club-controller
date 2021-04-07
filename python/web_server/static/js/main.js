const server_ip = '127.0.0.1';
let audioServerWebsocket;

function setGpioPin(id, value) {
    const url = 'http://127.0.0.1:5000/gpio'
    let data = { id: id, value: value };

    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(res => {
        console.log("Request complete! response:", res);
    });
}

function setColor(value) {
    const url = 'http://127.0.0.1:5000/color'
    let data = { value: value };

    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(res => {
        console.log("Request complete! response:", res);
    });
}

function onGpioButtonClick(buttonEl, id) {
    if (buttonEl.className == "disabled") {
        buttonEl.className = "";
        console.log("enabled")
        setGpioPin(id, true);
    } else {
        buttonEl.className = "disabled";
        console.log("disabled");
        setGpioPin(id, false);
    }
}

function addButton(elementId, text, id, active) {
    var buttonEl = document.createElement("button");
    if (!active) {
        buttonEl.className = "disabled";
    } else {
        buttonEl.className = "";
    }
    buttonEl.id = "button-gpio-" + id;
    buttonEl.addEventListener('click', function () { onGpioButtonClick(buttonEl, id); }, false);

    var buttonTextEl = document.createElement("span");
    buttonTextEl.className = "button-text";
    buttonTextEl.innerText = text;
    buttonEl.appendChild(buttonTextEl);
    document.getElementById(elementId).appendChild(buttonEl);
}


function initUI() {
    const url = 'http://' + server_ip + ':5000/gpio'
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log("Received GPIO status: " + json);
            console.log(json)
            addButton("smoke-button", "Smoke", 4, json[4])
        })
}

function setupWebsocket() {
    audioServerWebsocket = new WebSocket('ws://' + server_ip + ':6789/');
    audioServerWebsocket.onmessage = function (event) {
        let data = JSON.parse(event.data);
        console.log(data)
        switch (data.type) {
            case 'state':
                //value.textContent = data.value;
                break;
            case 'users':
                //users.textContent = (
                //    data.count.toString() + " user" +
                //    (data.count == 1 ? "" : "s"));
                break;
            default:
                console.error(
                    "unsupported event", data);
        }
    };
}


//initUI()
setupWebsocket();
